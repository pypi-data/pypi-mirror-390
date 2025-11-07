# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.1] - 2025-11-06

### Added
- Initial release of Aegis Python SDK
- Core `@aegis_guard` decorator for tool protection
- `AegisConfig` for SDK configuration with environment variable support
- `DecisionClient` for interacting with Aegis Data Plane
- Full support for allow/deny/sanitize/approval_needed decisions
- Async/await compatibility for async functions
- Built-in retry logic and resilience features
- Type hints and py.typed marker for type checking
- Comprehensive error handling with custom exception hierarchy
- Debug logging and console output utilities
- Complete unit test suite with 100% code coverage
- CI/CD workflows for automated testing and publishing
- Production-ready packaging for PyPI distribution

### Security
- Secure API key handling with Pydantic SecretStr
- Safe model dumping with masked sensitive fields

[Unreleased]: https://github.com/mrsidrdx/aegis-python-sdk/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/mrsidrdx/aegis-python-sdk/releases/tag/v0.1.1
