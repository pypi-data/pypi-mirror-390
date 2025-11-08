# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-10-08

### Added

#### Initial Release
- **Clean Namespace API**: Intuitive methods organized by resource type
  - `client.workspaces.list()` - List all workspaces
  - `client.workspaces.create(data)` - Create workspace
  - `client.workspaces.retrieve(id)` - Get workspace
  - `client.workspaces.update(id, data)` - Update workspace
  - `client.workspaces.delete(id)` - Delete workspace
  - `client.bots.list()` - List all bots
  - `client.bots.create(data)` - Create bot
  - `client.bots.retrieve(id)` - Get bot
  - `client.bots.update(id, data)` - Update bot
  - `client.bots.delete(id)` - Delete bot
  - `client.memories.store(data)` - Store memory
  - `client.memories.list(bot_id, params)` - List memories
  - `client.memories.search(data)` - Search memories
  - `client.memories.reprocess(id)` - Reprocess memory
  - `client.memories.delete(id)` - Delete memory

- **Type Safety**: Full type hints with comprehensive type definitions
  - `ClientConfig` - Client configuration
  - `Workspace`, `Bot`, `Memory` - Resource types
  - `CreateWorkspaceBody`, `CreateBotBody`, `StoreMemoryBody` - Request bodies
  - `MemoryListResponse`, `SearchMemoriesResponse` - Response types
  - All types exported for external use

- **Error Handling**: Comprehensive exception hierarchy
  - `ApiError` - Base exception for all API errors
  - `ValidationError` - Validation failures
  - `AuthenticationError` - Authentication failures
  - `AuthorizationError` - Authorization failures
  - `NotFoundError` - Resource not found
  - `ServiceUnavailableError` - Service unavailable
  - `RequestLimitError` - Rate limit exceeded
  - `NetworkError` - Network errors

- **Features**:
  - Auto-retry logic with configurable retries and delays
  - Multiple environment support (dev, alpha, beta, sandbox, production)
  - Debug mode for request/response logging
  - Configurable timeouts
  - Clean API response unwrapping
  - Dataclass support for type-safe request bodies

- **Documentation**:
  - Comprehensive README with examples
  - API reference documentation
  - Type hints for IDE support
  - Security best practices
  - Contributing guidelines

### Technical Details

- Python 3.8+ support
- Uses `requests` library for HTTP
- Type hints with `typing` module
- Dataclasses for structured data
- Clean separation of concerns
- No external dependencies except `requests` and `urllib3`

### Migration from JavaScript SDK

The Python SDK provides a 1:1 mapping with the JavaScript SDK:

```python
# Python
client = create_moa_client(api_token='moa_token')
workspace = client.workspaces.create({'name': 'Test'})
```

```javascript
// JavaScript
const client = createMoaClient({ apiToken: 'moa_token' });
const workspace = await client.workspaces.create({ name: 'Test' });
```

[1.0.0]: https://github.com/memof-ai/memofai-python-sdk/releases/tag/v1.0.0
