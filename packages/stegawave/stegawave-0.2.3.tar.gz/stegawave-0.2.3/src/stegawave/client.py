"""HTTP client for the Stegawave REST API."""

from __future__ import annotations

import os
import time
from typing import Any, Dict, Iterable, Optional, Type, TypeVar, Union

import requests
from pydantic import BaseModel

from . import models
from .exceptions import (
    AuthenticationError,
    AuthorizationError,
    NetworkError,
    ProvisioningError,
    RateLimitError,
    ServerError,
    StegawaveError,
    UnexpectedResponseError,
    ValidationError,
)
from .workflow import PipelineSession

T = TypeVar("T", bound=BaseModel)

DEFAULT_BASE_URL = "https://api.stegawave.com"


class StegawaveClient:
    """Lightweight wrapper around the Stegawave REST API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        *,
        base_url: Optional[str] = None,
        timeout: float = 15.0,
        retry_attempts: int = 3,
        retry_backoff: float = 1.0,
        session: Optional[requests.Session] = None,
    ) -> None:
        self.api_key = api_key or os.getenv("STEGAWAVE_API_KEY")
        if not self.api_key:
            raise AuthenticationError("API key required", status_code=None)

        self.base_url = (base_url or os.getenv("STEGAWAVE_API_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")
        self.timeout = timeout
        self.retry_attempts = max(1, retry_attempts)
        self.retry_backoff = max(0.0, retry_backoff)
        self._session = session or requests.Session()

    def close(self) -> None:
        self._session.close()

    # Generic request handler -------------------------------------------------
    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        payload: Optional[Dict[str, Any]] = None,
        model: Optional[Type[T]] = None,
    ) -> Union[T, Dict[str, Any], Any]:
        url = f"{self.base_url}{path}"
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
        }

        last_error: Optional[Exception] = None
        for attempt in range(1, self.retry_attempts + 1):
            try:
                response = self._session.request(
                    method,
                    url,
                    params=params,
                    json=payload,
                    headers=headers,
                    timeout=self.timeout,
                )
            except requests.RequestException as exc:  # network hiccup
                last_error = exc
                if attempt == self.retry_attempts:
                    raise NetworkError("Failed to reach Stegawave API") from exc
                time.sleep(self.retry_backoff * attempt)
                continue

            if response.status_code >= 400:
                self._raise_for_status(response)

            if response.content:
                try:
                    data = response.json()
                except ValueError as exc:  # pragma: no cover - unexpected HTML/plain
                    raise UnexpectedResponseError("Response was not valid JSON", status_code=response.status_code) from exc
            else:
                data = {}

            if not model:
                return data

            try:
                return model.model_validate(data)
            except Exception as exc:  # pragma: no cover - indicates schema mismatch
                raise UnexpectedResponseError("Response payload did not match expected schema", status_code=response.status_code, payload=data) from exc

        if last_error:
            raise NetworkError("Unable to complete request", payload={"error": str(last_error)})
        raise UnexpectedResponseError("Unhandled request failure")

    def _raise_for_status(self, response: requests.Response) -> None:
        try:
            payload = response.json()
        except ValueError:
            payload = {"message": response.text or response.reason}

        message = payload.get("message") or payload.get("error") or response.reason or "Unknown error"
        status = response.status_code

        if status == 400 or status == 422:
            raise ValidationError(message, status_code=status, payload=payload)
        if status == 401:
            raise AuthenticationError(message, status_code=status, payload=payload)
        if status == 403:
            raise AuthorizationError(message, status_code=status, payload=payload)
        if status == 404:
            raise StegawaveError(message, status_code=status, payload=payload)
        if status == 409:
            raise StegawaveError(message, status_code=status, payload=payload)
        if status == 429:
            raise RateLimitError(message, status_code=status, payload=payload)
        if 500 <= status < 600:
            raise ServerError(message, status_code=status, payload=payload)

        raise UnexpectedResponseError(message, status_code=status, payload=payload)

    # --------------------------------------------------------------------- API
    def create_pipeline(self, request: Union[models.CreatePipelineRequest, Dict[str, Any]]) -> models.CreatePipelineResponse:
        payload = self._dump(request)
        return self._request("POST", "/create-pipeline", payload=payload, model=models.CreatePipelineResponse)

    def create_pipeline_session(
        self,
        request: Union[models.CreatePipelineRequest, Dict[str, Any]],
        *,
        wait: bool = False,
        timeout: float = 600.0,
        poll_interval: float = 5.0,
    ) -> PipelineSession:
        response = self.create_pipeline(request)
        if not response.is_success():
            raise ProvisioningError(
                "Pipeline creation failed",
                status_code=None,
                payload=response.model_dump(exclude_none=True),
            )
        session = PipelineSession(self, response.eventID)
        if wait:
            session.wait_until_ready(timeout=timeout, poll_interval=poll_interval)
        return session

    def get_pipeline(self, event_id: str) -> models.PipelineStatusResponse:
        params = {"eventID": event_id}
        return self._request("GET", "/get-pipeline", params=params, model=models.PipelineStatusResponse)

    def get_pipeline_session(self, event_id: str) -> PipelineSession:
        status = self.get_pipeline(event_id)
        return PipelineSession(self, event_id, status=status)

    def list_pipelines(self) -> models.PipelineListResponse:
        data = self._request("GET", "/get-pipeline")
        # Handle both 'events' (legacy) and 'pipelines' (current)
        if isinstance(data, dict) and ("events" in data or "pipelines" in data):
            items_key = "pipelines" if "pipelines" in data else "events"
            return models.PipelineListResponse(
                pipelines=[models.PipelineListEntry.model_validate(item) for item in data[items_key]]
            )
        if isinstance(data, list):
            return models.PipelineListResponse(pipelines=[models.PipelineListEntry.model_validate(item) for item in data])
        raise UnexpectedResponseError("Unexpected list response", payload=data)

    def is_event_ready(self, event_id: str) -> bool:
        status = self.get_pipeline(event_id)
        return status.is_ready()

    def wait_for_event(
        self,
        event_id: str,
        *,
        timeout: float = 600.0,
        poll_interval: float = 5.0,
    ) -> models.PipelineStatusResponse:
        session = PipelineSession(self, event_id)
        return session.wait_until_ready(timeout=timeout, poll_interval=poll_interval)

    def get_state(self, event_id: str) -> models.StateResponse:
        payload = models.StateRequest(eventID=event_id, action="status").model_dump()
        return self._request("POST", "/pipeline-state", payload=payload, model=models.StateResponse)

    def start_pipeline(self, event_id: str) -> models.StateResponse:
        payload = models.StateRequest(eventID=event_id, action="start").model_dump()
        return self._request("POST", "/pipeline-state", payload=payload, model=models.StateResponse)

    def stop_pipeline(self, event_id: str) -> models.StateResponse:
        payload = models.StateRequest(eventID=event_id, action="stop").model_dump()
        return self._request("POST", "/pipeline-state", payload=payload, model=models.StateResponse)

    def delete_pipeline(self, event_id: str) -> models.DeleteResponse:
        payload = {"eventID": event_id}
        return self._request("DELETE", "/delete", payload=payload, model=models.DeleteResponse)

    def fetch_token(self, user_keys: Union[str, Iterable[str]], exp_hours: Optional[int] = None) -> models.TokenResponse:
        if isinstance(user_keys, str):
            user_keys = [user_keys]
        params = {"user_key": ",".join(user_keys)}
        if exp_hours is not None:
            params["exp"] = str(exp_hours)
        return self._request("GET", "/token", params=params, model=models.TokenResponse)

    def submit_decode_job(self, request: Union[models.DecodeJobRequest, Dict[str, Any]]) -> models.DecodeJobResponse:
        payload = self._dump(request)
        return self._request("POST", "/decode", payload=payload, model=models.DecodeJobResponse)

    def iptv_query(self, request: Union[models.IptvQueryRequest, Dict[str, Any]]) -> models.IptvQueryResponse:
        payload = self._dump(request)
        return self._request("POST", "/iptv", payload=payload, model=models.IptvQueryResponse)

    def get_vod_archive(
        self,
        event_id: str,
        *,
        expires_in: int = 3600,
        download: bool = False,
        download_path: Optional[str] = None,
    ) -> models.VodArchiveResponse:
        """
        Get VOD archive files for an event with presigned download URLs.
        
        Args:
            event_id: The event ID to get archive files for
            expires_in: URL expiration time in seconds (default: 3600, max: 604800)
            download: If True, download all archive files to download_path
            download_path: Directory path to download files to (required if download=True)
        
        Returns:
            VodArchiveResponse with file metadata and presigned URLs
        
        Raises:
            ValidationError: If download=True but download_path is not provided
            StegawaveError: If archive is not enabled or files not found
        """
        if download and not download_path:
            raise ValidationError(
                "download_path is required when download=True",
                status_code=None
            )
        
        params = {
            "eventID": event_id,
            "expiresIn": str(expires_in)
        }
        
        response = self._request(
            "GET",
            "/get-vod-archive",
            params=params,
            model=models.VodArchiveResponse
        )
        
        if download and download_path:
            import os
            from pathlib import Path
            
            # Ensure download directory exists
            download_dir = Path(download_path)
            download_dir.mkdir(parents=True, exist_ok=True)
            
            # Download each file using presigned URLs
            for file_obj in response.files:
                file_path = download_dir / file_obj.filename
                print(f"Downloading {file_obj.filename} ({file_obj.size})...")
                
                try:
                    # Use requests directly (not self._session) to avoid sending API key headers
                    file_response = requests.get(
                        file_obj.url,
                        stream=True,
                        timeout=self.timeout * 10  # Longer timeout for large files
                    )
                    file_response.raise_for_status()
                    
                    with open(file_path, 'wb') as f:
                        for chunk in file_response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    print(f"✓ Downloaded {file_obj.filename}")
                except Exception as exc:
                    raise NetworkError(
                        f"Failed to download {file_obj.filename}",
                        payload={"filename": file_obj.filename, "error": str(exc)}
                    ) from exc
            
            print(f"\n✓ Downloaded {len(response.files)} files to {download_dir}")
        
        return response

    # ----------------------------------------------------------------- helpers
    @staticmethod
    def _dump(obj: Union[BaseModel, Dict[str, Any]]) -> Dict[str, Any]:
        if isinstance(obj, BaseModel):
            return obj.model_dump(mode='json', exclude_none=True)
        return {k: v for k, v in obj.items() if v is not None}

    def __enter__(self) -> "StegawaveClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()
