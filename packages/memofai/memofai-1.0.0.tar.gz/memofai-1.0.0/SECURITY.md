# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Currently supported versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

We take the security of memofai SDK seriously. If you discover a security vulnerability, please follow these steps:

### Please DO NOT

- Open a public GitHub issue for security vulnerabilities
- Disclose the vulnerability publicly before it has been addressed

### Please DO

1. **Email us directly**: Send details to **hello@memof.ai**
2. **Include the following information**:
   - Type of vulnerability
   - Full paths of source file(s) related to the vulnerability
   - Location of the affected source code (tag/branch/commit or direct URL)
   - Step-by-step instructions to reproduce the issue
   - Proof-of-concept or exploit code (if possible)
   - Impact of the issue, including how an attacker might exploit it

### What to Expect

- **Acknowledgment**: We will acknowledge your email within 48 hours
- **Communication**: We will send a more detailed response within 7 days indicating the next steps
- **Fix Timeline**: We aim to release a fix within 30 days for critical vulnerabilities
- **Credit**: We will credit you in our security advisory (unless you prefer to remain anonymous)

## Security Best Practices

When using memofai SDK:

### 1. API Token Security

- Get your token from https://dashboard.memof.ai/access-tokens
- Never commit API tokens to version control
- Use environment variables for sensitive data
- Rotate API tokens regularly
- Use different API tokens for different environments
- Token format: `moa_<alphanumeric_string>`

**Example: Using environment variables**

```python
import os
from memofai import create_moa_client

# Load from environment
api_token = os.environ.get('MOA_API_TOKEN')
if not api_token:
    raise ValueError('MOA_API_TOKEN environment variable is required')

client = create_moa_client(api_token=api_token)
```

**Example: Using python-dotenv**

```python
from dotenv import load_dotenv
import os
from memofai import create_moa_client

# Load .env file
load_dotenv()

client = create_moa_client(api_token=os.environ['MOA_API_TOKEN'])
```

### 2. Input Validation

Always validate and sanitize user inputs before storing as memories:

```python
def sanitize_input(text: str) -> str:
    """Sanitize user input before storing."""
    # Remove potential injection attempts
    # Limit length
    # Remove special characters if needed
    return text.strip()[:10000]

memory = client.memories.store({
    'bot_id': bot_id,
    'content_text': sanitize_input(user_input),
    'source_type': 'manual'
})
```

### 3. Error Handling

Handle errors gracefully without exposing sensitive information:

```python
from memofai import ApiError, AuthenticationError

try:
    workspace = client.workspaces.create({'name': 'Test'})
except AuthenticationError:
    # Log the error internally, show generic message to user
    logger.error("Authentication failed")
    return "Unable to authenticate. Please check your credentials."
except ApiError as e:
    # Log detailed error internally
    logger.error(f"API error: {e.status} - {e.message}")
    # Show generic message to user
    return "An error occurred. Please try again later."
```

### 4. Rate Limiting

Implement client-side rate limiting to avoid hitting API limits:

```python
import time
from typing import List

class RateLimitedClient:
    def __init__(self, client, requests_per_minute: int = 60):
        self.client = client
        self.min_interval = 60.0 / requests_per_minute
        self.last_request_time = 0
    
    def store_memory(self, data: dict):
        # Wait if needed
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        
        result = self.client.memories.store(data)
        self.last_request_time = time.time()
        return result
```

### 5. Secure Configuration

Use secure defaults and validate configuration:

```python
from memofai import create_moa_client, Environment

def create_secure_client(
    api_token: str,
    environment: Environment = 'production'
) -> MoaClient:
    """Create a client with secure defaults."""
    # Validate token format
    if not api_token.startswith('moa_'):
        raise ValueError('Invalid API token format')
    
    # Use production by default
    if environment not in ['production', 'sandbox']:
        raise ValueError('Only production and sandbox environments are allowed')
    
    return create_moa_client(
        api_token=api_token,
        environment=environment,
        timeout=30000,  # Reasonable timeout
        retries=3       # Limited retries
    )
```

### 6. PII and Sensitive Data

Be careful with personally identifiable information (PII):

```python
def store_safe_memory(client, bot_id: str, content: str):
    """Store memory with PII redaction."""
    # Use the built-in PII redaction
    memory = client.memories.store({
        'bot_id': bot_id,
        'content_text': content,
        'source_type': 'manual',
        'pii_redacted': True,  # Enable PII redaction
        'privacy_level': 'private'  # Set appropriate privacy level
    })
    return memory
```

### 7. HTTPS Only

The SDK uses HTTPS by default for all production environments. For development:

```python
# Production (HTTPS) - default
client = create_moa_client(api_token='moa_token')

# Development (HTTP) - only for local testing
client = create_moa_client(
    api_token='moa_token',
    environment='dev'  # http://127.0.0.1:8000
)
```

### 8. Dependency Security

Keep dependencies updated:

```bash
# Check for security vulnerabilities
pip install safety
safety check

# Update dependencies
pip install --upgrade memofai
```

## Additional Resources

- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)
- [MOA Documentation](https://docs.memof.ai)

## Version History

- **1.0.0** - Initial release with security best practices

## Contact

For security concerns, contact us at **hello@memof.ai**
