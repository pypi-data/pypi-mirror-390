# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


### Added
- Initial release of PyLoad - Asynchronous HTTP Load Testing Tool
- Support for GET, POST, PUT, DELETE, PATCH HTTP methods
- Concurrent request handling with configurable limits
- SQLite database storage for test results
- Loki integration for failure logging and monitoring
- Comprehensive statistics calculation (min, max, average response times)
- History mode for viewing past test results
- Command-line interface with flexible argument parsing
- Async/await implementation using aiohttp
- Environment-based configuration
- Comprehensive test suite with unit and integration tests

### Features
- Real-time response time metrics (first byte, last byte, total)
- Configurable request timeouts
- Error handling and logging
- Database schema with proper indexing
- Betterstack integration for centralized monitoring

### Technical Details
- Python 3.7+ compatibility
- Asynchronous I/O operations
- SQLite database backend
- RESTful API testing capabilities
- Extensible architecture for custom monitoring integrations

## [0.1.0] - 2025-01-09

### Added
- Complete implementation of async load testing functionality
- Database operations for result storage and retrieval
- Loki logging integration for failure monitoring
- Comprehensive test coverage
- Documentation and packaging setup
- CLI interface with argument validation

### Dependencies
- aiohttp>=3.7.0
- requests>=2.25.0
- python-dotenv>=0.15.0
- logtail>=1.0.1
### Testing
- Unit tests for all core functionality
- Integration tests with real API calls
- Mocked database operations for reliable testing
- Async test support with proper fixtures

### Packaging
- setuptools-based distribution
- pyproject.toml for modern Python packaging
- Comprehensive MANIFEST.in for file inclusion
- MIT License
- Complete README with usage examples
