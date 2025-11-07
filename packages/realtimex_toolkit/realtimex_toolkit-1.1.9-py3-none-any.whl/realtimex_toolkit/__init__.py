"""RealtimeX Internal Utilities - Lightweight library for LLM and credential management."""

__version__ = "1.1.0"

from realtimex_toolkit.credentials import (
    CredentialBundle,
    CredentialManager,
    CredentialType,
    get_credential,
)

from realtimex_toolkit.agent_flow import (
    get_flow_variable,
    get_thread_id,
    get_workspace_slug,
    get_workspace_data_dir
)

from realtimex_toolkit.exceptions import (
    ApiError,
    AuthenticationError,
    ConnectionError,
    CredentialError,
    ProviderError,
    RateLimitError,
    RealtimeXError,
    ResourceNotFoundError,
    ServerError,
)
from realtimex_toolkit.llm import LLMProviderManager, configure_provider, get_provider_env_vars

__all__ = [
    # Version
    "__version__",
    # Exceptions
    "ApiError",
    "AuthenticationError",
    "ConnectionError",
    "CredentialError",
    "ProviderError",
    "RateLimitError",
    "RealtimeXError",
    "ResourceNotFoundError",
    "ServerError",
    # LLM
    "LLMProviderManager",
    "configure_provider",
    "get_provider_env_vars",
    # Credentials
    "CredentialBundle",
    "CredentialManager",
    "CredentialType",
    "get_credential",
    "get_flow_variable",
    "get_thread_id",
    "get_workspace_slug",
    "get_workspace_data_dir"
]
