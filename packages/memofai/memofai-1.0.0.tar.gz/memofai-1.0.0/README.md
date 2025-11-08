# memofai

[![PyPI version](https://badge.fury.io/py/memofai.svg)](https://pypi.org/project/memofai/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)

Official Python SDK for Memory-of-Agents (MOA). Build intelligent applications with persistent AI memory.

## Features

✨ **Clean Namespace API** - Intuitive methods organized by resource type  
🔒 **Type-Safe** - Full type hints with comprehensive type definitions  
🧠 **Memory Management** - Store, search, and retrieve AI agent memories  
🤖 **Bot Operations** - Create and manage AI bots with ease  
🏢 **Workspace Control** - Organize your AI infrastructure  
⚡ **Auto-Retry** - Built-in retry logic for resilient API calls  
🎯 **Natural Language Search** - Query memories conversationally

## Installation

```bash
pip install memofai
```

## Quick Start

### Get Your API Token

1. Visit [dashboard.memof.ai/access-tokens](https://dashboard.memof.ai/access-tokens)
2. Click "Create New Token"
3. Copy your token (format: `moa_...`)

### Basic Example

```python
from memofai import create_moa_client

client = create_moa_client(
    api_token='moa_your_token_here',
    environment='production'
)

# Create a workspace
workspace = client.workspaces.create({
    'name': 'My AI Workspace',
    'description': 'Workspace for my AI agents'
})

# Create a bot
bot = client.bots.create({
    'name': 'Assistant',
    'description': 'Helpful AI assistant',
    'moa_workspace': workspace.id,
    'type': 'conversational',
})

# Store a memory
memory = client.memories.store({
    'bot_id': bot.id,
    'content_text': 'User prefers concise responses',
    'memory_type': 'preference',
    'source_type': 'manual'
})

# Search memories
results = client.memories.search({
    'bot_id': bot.id,
    'query': 'How should I communicate with the user?',
    'top_k': 5
})
```

## API Reference

### Configuration

```python
from memofai import create_moa_client, ClientConfig, MoaClient

# Using convenience function
client = create_moa_client(
    api_token='moa_your_token',
    environment='production',  # 'dev' | 'alpha' | 'beta' | 'sandbox' | 'production'
    timeout=30000,             # Optional: request timeout (ms)
    retries=3,                 # Optional: retry attempts
    retry_delay=1000           # Optional: retry delay (ms)
)

# Or using ClientConfig directly
config = ClientConfig(
    api_token='moa_your_token',
    environment='production',
    timeout=30000,
    retries=3,
    retry_delay=1000
)
client = MoaClient(config)
```

### Workspaces

```python
# List all workspaces
workspaces = client.workspaces.list()

# Create workspace
workspace = client.workspaces.create({
    'name': 'My Workspace',
    'description': 'Optional description'
})

# Get workspace
workspace = client.workspaces.retrieve(workspace_id)

# Update workspace
updated = client.workspaces.update(workspace_id, {
    'name': 'Updated Name',
    'description': 'Updated description'
})

# Delete workspace
client.workspaces.delete(workspace_id)
```

### Bots

```python
# List all bots
bots = client.bots.list()

# Create bot
bot = client.bots.create({
    'name': 'My Bot',
    'description': 'Bot description',
    'moa_workspace': workspace_id,
    'type': 'conversational'  # 'conversational' | 'knowledge_base' | 'task_oriented' | 'analytical' | 'creative'
})

# Get bot
bot = client.bots.retrieve(bot_id)

# Update bot
updated = client.bots.update(bot_id, {
    'name': 'Updated Bot Name',
    'is_active': True
})

# Delete bot
client.bots.delete(bot_id)
```

### Memories

```python
# Store a memory
memory = client.memories.store({
    'bot_id': bot_id,
    'content_text': 'Important information to remember',
    'source_type': 'manual',  # 'manual' | 'email' | 'call_transcript' | 'slack' | 'upload' | 'api' | 'sdk'
    'memory_type': 'fact',    # Optional: 'fact' | 'preference' | 'credential' | 'event' | 'task' | 'other'
    'importance_score': 0.8,  # Optional: 0.0 to 1.0
})

# List memories
memories = client.memories.list(
    bot_id=bot_id,
    query_params={
        'limit': 10,
        'offset': 0,
        'memory_type': 'fact',
        'pipeline_stage': 'completed'
    }
)

# Search memories
results = client.memories.search({
    'bot_id': bot_id,
    'query': 'What are the user preferences?',
    'top_k': 5,
    'generate_answer': True
})

# Reprocess a memory
response = client.memories.reprocess(memory_id)

# Delete a memory
client.memories.delete(memory_id)
```

## Type Safety

The SDK provides full type hints for better IDE support and type checking:

```python
from memofai import (
    MoaClient,
    ClientConfig,
    Workspace,
    Bot,
    Memory,
    CreateBotBody,
    SearchMemoriesBody,
    MemoryListResponse,
)

# Type-safe configuration
config: ClientConfig = ClientConfig(
    api_token='moa_token',
    environment='production'
)

# Type-safe responses
workspace: Workspace = client.workspaces.create({'name': 'My Workspace'})
bot: Bot = client.bots.retrieve(bot_id)
memories: MemoryListResponse = client.memories.list(bot_id)
```

## Error Handling

The SDK provides specific exception classes for different error types:

```python
from memofai import (
    ApiError,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ServiceUnavailableError,
    RequestLimitError,
    NetworkError,
)

try:
    workspace = client.workspaces.create({'name': 'Test'})
except ValidationError as e:
    print(f"Validation failed: {e.validation_errors}")
except AuthenticationError as e:
    print(f"Authentication failed: {e.message}")
except NotFoundError as e:
    print(f"Resource not found: {e.message}")
except RequestLimitError as e:
    print(f"Rate limit exceeded: {e.get_limit()}")
except ApiError as e:
    print(f"API error: {e.message} (status: {e.status})")
except NetworkError as e:
    print(f"Network error: {e.message}")
```

## Advanced Usage

### Using Dataclasses

You can use dataclasses for type-safe request bodies:

```python
from memofai import CreateBotBody, StoreMemoryBody

# Create bot using dataclass
bot_data = CreateBotBody(
    name='My Bot',
    description='Bot description',
    moa_workspace=workspace_id,
    type='conversational'
)
bot = client.bots.create(bot_data)

# Store memory using dataclass
memory_data = StoreMemoryBody(
    bot_id=bot_id,
    content_text='Important information',
    source_type='manual',
    memory_type='fact'
)
memory = client.memories.store(memory_data)
```

### Debug Mode

Enable debug logging to see API requests and responses:

```python
import os

os.environ['MOA_DEBUG'] = 'true'

# Now all API calls will log debug information
client = create_moa_client(api_token='moa_token')
```

### Custom Timeout and Retries

```python
client = create_moa_client(
    api_token='moa_token',
    timeout=60000,      # 60 seconds
    retries=5,          # 5 retry attempts
    retry_delay=2000    # 2 seconds between retries
)
```

## Environments

The SDK supports multiple environments:

- **dev**: `http://127.0.0.1:8000` - Development environment for internal testing
- **alpha**: `https://alpha-api.memof.ai` - Alpha environment for early testing
- **beta**: `https://beta-api.memof.ai` - Beta environment for pre-production testing
- **sandbox**: `https://sandbox-api.memof.ai` - Sandbox environment for development and testing
- **production**: `https://api.memof.ai` - Production environment (default)

```python
client = create_moa_client(
    api_token='moa_token',
    environment='sandbox'  # Use sandbox for testing
)
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## Security

For security issues, please see our [Security Policy](SECURITY.md).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📧 Email: dev@memof.ai
- 🌐 Website: https://memof.ai
- 📚 Documentation: https://docs.memof.ai
- 🐛 Issues: https://github.com/memof-ai/memofai-python-sdk/issues

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a history of changes to this project.

## Links

- [PyPI Package](https://pypi.org/project/memofai/)
- [GitHub Repository](https://github.com/memof-ai/memofai-python-sdk)
- [Official Website](https://memof.ai)
- [Documentation](https://docs.memof.ai)
- [Dashboard](https://dashboard.memof.ai)
