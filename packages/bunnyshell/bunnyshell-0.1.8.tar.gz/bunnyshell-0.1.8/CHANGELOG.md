# Changelog

All notable changes to the Bunnyshell Python SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
