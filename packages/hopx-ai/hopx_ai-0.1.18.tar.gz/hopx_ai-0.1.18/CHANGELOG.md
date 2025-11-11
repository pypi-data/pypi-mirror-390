# Changelog

All notable changes to the Bunnyshell Python SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.10] - 2025-11-09

### Fixed
- **CRITICAL**: Fixed `template_id` type conversion issue when creating sandboxes from built templates
  - Template build API returns integer template_id (e.g., `83`)
  - Sandbox create API expects string template_id (e.g., `"83"`)
  - SDK now automatically converts `template_id` to string in both `Sandbox.create()` and `AsyncSandbox.create()`
  - Fixes error: `NotFoundError: The template '83' was not found`

### Technical Details
- Added `str(template_id)` conversion in `sandbox.py` and `async_sandbox.py`
- Works with both integer and string `template_id` values
- Maintains backward compatibility

## [0.1.9] - 2025-11-09

### Added
- **NEW**: `timeout_seconds` parameter in `Sandbox.create()` - auto-kill sandbox after specified seconds
- **NEW**: `internet_access` parameter in `Sandbox.create()` - enable/disable internet access (default: True)
- Support for both parameters in sync (`Sandbox`) and async (`AsyncSandbox`) versions

### Changed
- **BREAKING**: Renamed parameter `timeout` → `timeout_seconds` to match API specification
  - Old parameter was never functional (not sent to API), so impact is minimal
  - Migration: Change `timeout=300` to `timeout_seconds=300`

### Fixed
- `timeout_seconds` now correctly sent to API (was previously ignored)

## [0.1.8] - 2025-11-07

### Fixed
- **CRITICAL**: Fixed IPv6 timeout issue causing 60-270 second delays on all API calls
  - Forced IPv4 resolution in HTTPClient, AgentHTTPClient, and AsyncHTTPClient
  - Performance improvement: 120-600x faster API calls (from 60-270s to 0.2-0.5s)
- Fixed `/execute` endpoint usage (was using `/execute/rich` which returned kernel setup code)
- Added agent readiness check with retry to avoid 401 errors on newly created sandboxes

### Changed
- Updated HTTPClient transport to use `local_address="0.0.0.0"` to force IPv4
- Updated AgentHTTPClient transport to use `local_address="0.0.0.0"` to force IPv4
- Updated AsyncHTTPClient transport to use `local_address="0.0.0.0"` to force IPv4
- Improved agent initialization with health check and retry logic

### Performance
- Create sandbox: 60-270s → 0.5s (120-600x faster)
- Get info: 60s → 0.2s (300x faster)
- Run code: 60s → 0.5s (120x faster)

## [0.1.7] - 2024-10-22

### Added
- Template building support
- Desktop automation features
- WebSocket features for streaming
- Advanced use cases examples

## [0.1.6] - 2024-10-15

### Added
- Environment variables management
- Process management
- Cache management

## [0.1.5] - 2024-10-08

### Added
- File operations (read, write, upload, download)
- Command execution
- IPython kernel support

## [0.1.4] - 2024-10-01

### Added
- Basic code execution
- Multiple language support (Python, JavaScript, Bash, Go)
- Background execution

## [0.1.0] - 2024-09-15

### Added
- Initial release
- Basic sandbox creation and management
- Sync and async support
- JWT authentication
