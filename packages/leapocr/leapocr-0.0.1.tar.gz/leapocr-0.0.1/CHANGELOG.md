# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.0.1] - 2025-11-08

### Added
- Initial release of LeapOCR Python SDK
- Async-first client with httpx
- Support for file and URL processing
- Multiple output formats (Structured, Markdown, Per-Page Structured)
- Custom schema support for structured data extraction
- Built-in retry logic with exponential backoff
- Progress tracking with callbacks
- Comprehensive error handling hierarchy
- Type-safe API with full mypy support
- Direct multipart file uploads
- Concurrent batch processing support
- 93 unit tests and 13 integration tests
- Complete documentation and examples

### Core Features
- `LeapOCR` main client with async context manager
- `OCRService` for document processing operations
- `ProcessOptions` for configurable processing
- `PollOptions` for custom polling behavior
- `ClientConfig` for client configuration

### Error Classes
- `LeapOCRError` - Base error class
- `AuthenticationError` - Authentication failures
- `RateLimitError` - Rate limit exceeded
- `ValidationError` - Input validation errors
- `FileError` - File-related errors
- `JobError` - Job processing errors
- `JobFailedError` - Job processing failures
- `JobTimeoutError` - Job timeout errors
- `NetworkError` - Network connectivity issues
- `APIError` - API error responses
- `InsufficientCreditsError` - Insufficient credits

### Examples
- Basic file processing
- URL processing with manual polling
- Concurrent batch processing
- Schema-based extraction
- Custom configuration
- Error handling strategies
- Timeout handling

[Unreleased]: https://github.com/leapocr/leapocr-python/compare/v0.0.1...HEAD
[0.0.1]: https://github.com/leapocr/leapocr-python/releases/tag/v0.0.1
