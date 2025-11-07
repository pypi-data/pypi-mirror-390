# RealtimeX Internal Utilities

Lightweight internal library providing utilities for LLM provider configuration and credential management across RealtimeX internal services.

## Installation

```bash
# Using uv (recommended) for local development
uv pip install -e /path/to/realtimex-toolkit

# Using pip from PyPI
pip install realtimex_toolkit
```

## Quick Start

### Agent Flow Management

Work with agent flow data. `get_flow_variable` now supports dotted paths for nested structures, safe defaults, and fetching the full payload.

```python
import json

from realtimex_toolkit import get_flow_variable

# Access nested variables using dotted notation
user_email = get_flow_variable("user.email")
print(user_email)  # "example@example.com"

# Provide defaults for missing keys
theme = get_flow_variable("user.theme", "light")
print(theme)  # "light"

# Get the entire payload when you need to inspect everything
variables = get_flow_variable()
print(json.dumps(variables))  # {"time":"12:40:28 PM", ...}
```

### Credential Management

Retrieve encrypted credentials from the RealtimeX app backend and decrypt them for use across RealtimeX ecosystem services.

```python
from realtimex_toolkit import get_credential

# Simplest usage - just the credential ID
# Connects to local RealtimeX backend (http://localhost:3001) by default
credential = get_credential("credential-id")
print(credential["payload"])  # {"name": "API_KEY", "value": "secret-value"}

# With API key for authenticated requests
credential = get_credential("credential-id", api_key="service-api-key")

# With custom backend URL (for non-default configurations)
credential = get_credential(
    "credential-id",
    api_key="service-api-key",
    base_url="http://custom-host:3001"  # Override default localhost:3001
)

# For long-running services, use CredentialManager directly
from realtimex_toolkit import CredentialManager

# Connects to http://localhost:3001 by default
manager = CredentialManager(api_key="service-api-key")
try:
    bundle = manager.get("credential-id")
    # Credentials are cached automatically
    bundle_again = manager.get("credential-id")  # Returns cached

    # Force refresh from backend
    fresh_bundle = manager.get("credential-id", force_refresh=True)
finally:
    manager.close()
```

**Configuration:**
- `base_url`: Base URL of the RealtimeX app backend (default: `http://localhost:3001`)
- `api_key`: Authentication token for backend API requests (optional)
- Credentials are encrypted using AES-256-CBC and decrypted using keys from `~/.realtimex.ai/Resources/server/.env.development`

**Return shape (`get_credential`):**

```python
{
    "credential_id": str,
    "name": str,
    "credential_type": str,
    "payload": dict[str, str],
    "metadata": dict | None,
    "updated_at": str | None,
}
```

## Supported LLM Providers

- **Major Providers**: OpenAI, Anthropic, Azure OpenAI
- **Cloud AI**: Google Gemini, AWS Bedrock
- **Alternative APIs**: Groq, Cohere, Mistral, Perplexity
- **Open Source Aggregators**: Open Router, Together AI, Fireworks AI
- **Emerging**: DeepSeek, xAI, Novita
- **Local Deployment**: Ollama, LocalAI, LM Studio, KoboldCPP
- **Custom**: Generic OpenAI, LiteLLM, Nvidia NIM, Hugging Face

## Development

```bash
# Install with dev dependencies
uv pip install -e ".[dev]"

# Run tests
pytest

# Run type checking
mypy src/realtimex_toolkit

# Format & lint
ruff check src/realtimex_toolkit tests
ruff format src/realtimex_toolkit tests
```

## Architecture

- **`realtimex_toolkit.llm`**: LLM provider configuration utilities
- **`realtimex_toolkit.credentials`**: Secure credential retrieval and decryption
- **`realtimex_toolkit.api`**: HTTP client with retry logic and error mapping
- **`realtimex_toolkit.utils`**: Internal utilities (path resolution, logging)

## License

Proprietary - Internal use only
