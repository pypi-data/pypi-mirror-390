# AI Agent Development Guidelines

This document provides guidelines for AI agents (like GitHub Copilot, ChatGPT, Claude, etc.) when working with or contributing to the TogoMQ SDK for Python.

## Project Overview

**Purpose**: Official Python SDK for TogoMQ, a cloud-based message queuing service  
**Language**: Python 3.9+  
**Key Technologies**: gRPC, Protocol Buffers, asyncio concepts  
**Package**: `togomq-sdk` (published on PyPI as `togomq-sdk`, imported as `togomq`)

## Architecture

### Core Components

1. **Client (`togomq/client.py`)**
   - Main entry point for SDK users
   - Manages gRPC connection lifecycle
   - Provides `pub()`, `pub_batch()`, and `sub()` methods
   - Thread-safe for concurrent operations
   - Uses context manager pattern for resource cleanup

2. **Config (`togomq/config.py`)**
   - Configuration management with sensible defaults
   - Required: `token` (authentication)
   - Optional: `host`, `port`, `log_level`, `use_tls`
   - Validates configuration on initialization

3. **Message (`togomq/message.py`)**
   - Represents messages for publishing and receiving
   - Builder pattern for fluent API (`with_variables()`, `with_postpone()`, etc.)
   - Immutable after creation (builder methods return self for chaining)

4. **SubscribeOptions (`togomq/subscribe_options.py`)**
   - Configuration for subscription behavior
   - Supports topic wildcards (`*`, `orders.*`)
   - Controls batch size and rate limiting

5. **Errors (`togomq/errors.py`)**
   - Custom exception hierarchy
   - Error codes for different failure types
   - Detailed error messages for debugging

6. **Logger (`togomq/logger.py`)**
   - Configurable logging system
   - Levels: debug, info, warn, error, none
   - Used throughout SDK for diagnostics

## Design Patterns

### 1. Builder Pattern
Messages and options use builder pattern for clean API:
```python
msg = Message("topic", b"data").with_variables({"key": "value"}).with_postpone(60)
```

### 2. Context Manager
Clients support context manager for automatic cleanup:
```python
with Client(config) as client:
    client.pub_batch(messages)
```

### 3. Generator-Based Streaming
Subscriptions return generators for memory-efficient streaming:
```python
msg_gen, err_gen = client.sub(options)
for msg in msg_gen:
    process(msg)
```

## Code Style Guidelines

### Python Style
- Follow PEP 8 conventions
- Use type hints for all public APIs
- Maximum line length: 100 characters
- Use Black for formatting
- Use Ruff for linting

### Documentation
- All public classes and methods must have docstrings
- Use Google-style docstrings
- Include Args, Returns, Raises sections
- Provide usage examples in class docstrings

### Error Handling
- Use custom `TogoMQError` for SDK-specific errors
- Always provide error codes for categorization
- Include helpful error messages and details
- Handle and convert gRPC errors appropriately

## Testing Guidelines

### Test Structure
- Use pytest for all tests
- Organize tests by module: `test_<module>.py`
- Mock gRPC calls for unit tests
- Include integration tests where appropriate

### Coverage Requirements
- Aim for >80% code coverage
- Test error paths and edge cases
- Test all public API methods
- Include tests for builder patterns

### Test Examples
```python
def test_config_validation():
    """Test that config validates token."""
    with pytest.raises(TogoMQError) as exc_info:
        Config(token="")
    assert exc_info.value.code == ErrorCode.CONFIGURATION
```

## Common Patterns for AI Agents

### When Adding Features

1. **Follow Existing Patterns**
   - Look at similar existing code first
   - Maintain consistency in API design
   - Use same error handling approach

2. **Update All Relevant Files**
   - Implementation in `togomq/`
   - Tests in `tests/`
   - Examples in `examples/`
   - Documentation in README.md
   - Update `__init__.py` exports if needed

3. **Maintain Type Safety**
   - Add type hints to all new code
   - Run `mypy togomq` to verify
   - Handle Optional types explicitly

### When Fixing Bugs

1. **Reproduce First**
   - Create a failing test
   - Understand the root cause
   - Document the fix in comments

2. **Consider Impact**
   - Check if fix affects API compatibility
   - Update version if breaking change
   - Document in changelog

### When Refactoring

1. **Preserve API**
   - Don't break existing public APIs
   - Maintain backward compatibility
   - Deprecate gradually if needed

2. **Improve Tests**
   - Add tests for refactored code
   - Ensure coverage doesn't decrease
   - Test edge cases

## Dependencies

### Core Dependencies
- `togomq-grpc>=0.1.11` - Generated gRPC stubs
- `grpcio>=1.60.0` - gRPC library
- `protobuf>=4.25.0` - Protocol Buffers

### Dev Dependencies
- `pytest>=7.4.0` - Testing framework
- `pytest-cov>=4.1.0` - Coverage reporting
- `black>=23.7.0` - Code formatting
- `ruff>=0.0.285` - Linting
- `mypy>=1.5.0` - Type checking

## CI/CD Pipeline

### GitHub Actions Workflows

1. **CI (`ci.yml`)**
   - Runs on pull requests and pushes
   - Tests across Python 3.8-3.12
   - Linting and type checking
   - Coverage reporting

2. **Release (`release.yml`)**
   - Triggered on version tags
   - Builds distribution packages
   - Publishes to PyPI
   - Creates GitHub release

### Version Management
- Use semantic versioning (MAJOR.MINOR.PATCH)
- Version in `pyproject.toml` and `togomq/__init__.py`
- Tag format: `v0.1.0`
- Auto-publish on tag push

## Common Tasks for AI Agents

### Adding a New Method to Client

1. Define method signature with type hints
2. Add docstring with examples
3. Implement with proper error handling
4. Add unit tests in `tests/test_client.py`
5. Add example in `examples/`
6. Document in README.md

### Adding a New Error Code

1. Add to `ErrorCode` enum in `errors.py`
2. Use in appropriate error handling
3. Document in README.md error codes section
4. Add test case for the error

### Updating Configuration

1. Add property to `Config` class
2. Update `__init__` and validation
3. Update tests in `test_config.py`
4. Document in README.md configuration section
5. Update examples if relevant

## Integration with TogoMQ gRPC

The SDK depends on `togomq-grpc` package which provides:
- `mq.v1.mq_pb2` - Message definitions
- `mq.v1.mq_pb2_grpc` - Service stubs

### Key gRPC Messages
- `PubMessageRequest` - Publish request
- `PubMessageResponse` - Publish response
- `SubMessageRequest` - Subscribe request
- `SubMessageResponse` - Subscribe response (streamed)
- `HealthCheckRequest/Response` - Health check

### Authentication
- Uses gRPC metadata
- Format: `("authorization", "Bearer <token>")`
- Applied to all RPC calls

## Gotchas and Important Notes

1. **Topic Requirements**
   - Publishing: Topic is REQUIRED for each message
   - Subscribing: Topic is REQUIRED (use "*" for all topics)

2. **Generator Cleanup**
   - Subscriptions return generators
   - Generators may hold resources
   - Always iterate to completion or explicitly close

3. **Thread Safety**
   - Clients are thread-safe
   - Create separate client per thread if needed
   - gRPC channels handle concurrent calls

4. **Error Handling**
   - Always convert gRPC errors to TogoMQError
   - Provide meaningful error messages
   - Include details for debugging

5. **Resource Management**
   - Always close clients when done
   - Use context managers when possible
   - Clean up in finally blocks

## Questions to Ask Before Changes

1. Does this change maintain backward compatibility?
2. Are all new public APIs documented?
3. Are there tests for the new functionality?
4. Does this follow existing patterns in the codebase?
5. Are error cases handled appropriately?
6. Is the change reflected in examples and README?

## Resources

- **TogoMQ Website**: https://togomq.io
- **Python SDK Repo**: https://github.com/TogoMQ/togomq-sdk-python
- **gRPC Python Repo**: https://github.com/TogoMQ/togomq-grpc-python
- **Go SDK (reference)**: https://github.com/TogoMQ/togomq-sdk-go
- **Python gRPC Docs**: https://grpc.io/docs/languages/python/

## Contact

For questions about this SDK or AI agent contributions:
- Open an issue on GitHub
- Check existing issues and PRs
- Review the Go SDK for feature parity reference