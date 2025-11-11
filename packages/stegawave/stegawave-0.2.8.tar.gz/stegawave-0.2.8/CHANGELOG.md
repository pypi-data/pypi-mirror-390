# Changelog

All notable changes to `stegawave` will be documented here.

## [0.2.0] - 2025-01-XX

### Breaking Changes

**API Endpoint Changes:**
- `create_pipeline()`: Endpoint changed from `/create` to `/create-pipeline`
- `get_pipeline()`: Endpoint changed from `/get` to `/get-pipeline`
- `list_pipelines()`: Endpoint changed from `/get` to `/get-pipeline`
- `get_state()`, `start_pipeline()`, `stop_pipeline()`: Endpoint changed from `/state` to `/pipeline-state`
- Removed `get_passphrase()` and `rotate_passphrase()` methods (passphrase management now integrated into pipeline creation)

**Model Changes:**
- `InputType`: Added `RTP`, `RTP_FEC`, `RIST`, `ZIXI_PUSH`; Removed `RTMP_PUSH`, `RTMP_PULL`, `HLS`, `MP4_FILE`, `TS_FILE`
- `PipelineInputStatus`: 
  - Changed `endpoint` (str) to `endpoints` (List[str])
  - Added `passphraseEnabled` (bool) and `passphrase` (Optional[str]) fields
- `PipelineEncoderStatus`:
  - Removed `status` and `segmentLength` fields
  - Added `archive` (dict) field for archival configuration
- `PipelinePackagerEndpoint`:
  - Changed `manifests` from `List[str]` to `List[Union[ManifestInfo, str]]` with structured manifest info
- `PipelineCdnStatus`:
  - Changed `endpoints` from `List[str]` to `List[Union[CdnEndpoint, str]]` with protocol/url structure
- `PipelineStatusResponse`:
  - Added `detected_users` (List[Union[DetectedUser, str]]) field for watermark detection results
  - Each detection includes `user`, `user_key`, `similarity`, and `detected_at` timestamp
- `StateResponse`:
  - Added `components` (StateComponents) field with detailed component status (mediaconnect, ec2, medialive)
- `EncoderConfig`: Now supports both `Outputs` (List[OutputConfig]) and legacy `output_group` (OutputGroup) formats
- Removed models: `SourceConfig`, `PassphraseResponse`, `RotatePassphraseRequest`, `RotatePassphraseResponse`
- Added models: `ComponentStatus`, `StateComponents`, `ManifestInfo`, `CdnEndpoint`

**Workflow Changes:**
- `InputDetails.from_status()`: Updated to handle new `endpoints` array format
- `PipelineSession.get_manifests()`: Updated to handle new `CdnEndpoint` object format

### Migration Guide

**Passphrase Management:**
```python
# Old approach (removed):
response = client.get_passphrase(event_id)
passphrase = response.passphrase

# New approach (integrated into pipeline creation):
pipeline = CreatePipelineRequest(
    input=InputConfig(
        type="SRT_LISTENER",
        SrtListenerSettings=SrtListenerSettings(
            PassphraseEnabled=True,
            Passphrase="your-passphrase"  # Optional - auto-generated if omitted
        )
    )
)
status = client.get_pipeline(event_id)
passphrase = status.input.passphrase  # Access from status
```

**Input Types:**
```python
# Removed input types - migrate to alternatives:
# RTMP_PUSH, RTMP_PULL -> Use SRT_LISTENER or RTP
# HLS, MP4_FILE, TS_FILE -> Use RTP, RIST, or ZIXI_PUSH

# New input types available:
InputConfig(type="RTP", ...)
InputConfig(type="RTP_FEC", ...)
InputConfig(type="RIST", ...)
InputConfig(type="ZIXI_PUSH", ...)
```

**Accessing Endpoints:**
```python
# Old approach:
endpoint = status.input.endpoint  # str

# New approach:
endpoints = status.input.endpoints  # List[str]
endpoint = endpoints[0] if endpoints else None
```

**Accessing Manifests:**
```python
# Old approach:
manifests = status.packager.endpoints[0].manifests  # List[str]

# New approach (supports both formats):
manifests = status.packager.endpoints[0].manifests  # List[Union[ManifestInfo, str]]
for manifest in manifests:
    if isinstance(manifest, str):
        url = manifest
    else:
        url = manifest.name  # or manifest.type
```

**Accessing Detected Users:**
```python
# New in 0.2.0 - structured detection results:
if status.detected_users:
    for detection in status.detected_users:
        # Detection objects contain full watermark metadata
        print(f"User: {detection.user}")
        print(f"Key: {detection.user_key}")
        print(f"Similarity: {detection.similarity}")
        print(f"Detected at: {detection.detected_at}")
```

## [0.1.1] - 2025-10-17

- Improve provisioning workflow helpers and example script
- Expand test coverage for pipeline session retries and manifest helpers
- Prepare packaging metadata for PyPI publish attempt

## [0.1.0] - 2025-10-17

- Initial project scaffolding
- Added Pydantic models for pipeline creation and lifecycle endpoints
- Implemented `StegawaveClient` with typed responses, retry support, and pipeline session helpers
- Documented quick start and development workflow
