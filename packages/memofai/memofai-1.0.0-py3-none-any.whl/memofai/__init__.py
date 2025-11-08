"""
memofai - Official Python SDK for Memory-of-Agents (MOA)

Build intelligent applications with persistent AI memory.
"""

from .api_client import MoaClient
from .http_client import HttpClient
from .endpoints import API_ENDPOINTS, WORKSPACE_ENDPOINTS, BOT_ENDPOINTS, MEMORY_ENDPOINTS
from .version import SDK_VERSION

# Core types
from .types import (
    HttpMethod,
    Headers,
    ApiResponse,
    ClientConfig,
    Environment,
    EnvironmentConfig,
    ENVIRONMENTS,
)

# User types
from .types import BasicUser

# Workspace types
from .types import (
    Workspace,
    WorkspaceMember,
    WorkspaceRole,
    CreateWorkspaceBody,
    UpdateWorkspaceBody,
)

# Bot types
from .types import (
    Bot,
    BotType,
    CreateBotBody,
    UpdateBotBody,
)

# Memory types
from .types import (
    Memory,
    MemoryType,
    PipelineStage,
    PermanenceLevel,
    PrivacyLevel,
    SourceType,
    StoreMemoryBody,
    SearchMemoriesBody,
    ListMemoryQueryParams,
    MemoryListResponse,
    SearchMemoriesResponse,
    ReprocessMemoryResponse,
    PaginationMetadata,
)

# Error types
from .types import MoaErrorResponse, ValidationErrorDetail

from .exceptions import (
    ApiError,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ServiceUnavailableError,
    NetworkError,
    RequestLimitError,
)


def create_moa_client(
    api_token: str,
    environment: Environment = "production",
    timeout: int = 30000,
    retries: int = 3,
    retry_delay: int = 1000,
) -> MoaClient:
    """
    Create a new MOA client instance.

    Args:
        api_token: Your MOA API token (starts with 'moa_')
        environment: Environment to use ('dev', 'alpha', 'beta', 'sandbox', 'production')
        timeout: Request timeout in milliseconds (default: 30000)
        retries: Number of retry attempts for failed requests (default: 3)
        retry_delay: Delay between retries in milliseconds (default: 1000)

    Returns:
        MoaClient instance

    Example:
        >>> from memofai import create_moa_client
        >>> client = create_moa_client(api_token='moa_your_token_here')
        >>> workspaces = client.workspaces.list()
    """
    config = ClientConfig(
        api_token=api_token,
        environment=environment,
        timeout=timeout,
        retries=retries,
        retry_delay=retry_delay,
    )
    return MoaClient(config)


__version__ = SDK_VERSION

__all__ = [
    # Main client
    "MoaClient",
    "create_moa_client",
    # HTTP client
    "HttpClient",
    # Endpoints
    "API_ENDPOINTS",
    "WORKSPACE_ENDPOINTS",
    "BOT_ENDPOINTS",
    "MEMORY_ENDPOINTS",
    # Version
    "SDK_VERSION",
    "__version__",
    # Core types
    "HttpMethod",
    "Headers",
    "ApiResponse",
    "ClientConfig",
    "Environment",
    "EnvironmentConfig",
    "ENVIRONMENTS",
    # User types
    "BasicUser",
    # Workspace types
    "Workspace",
    "WorkspaceMember",
    "WorkspaceRole",
    "CreateWorkspaceBody",
    "UpdateWorkspaceBody",
    # Bot types
    "Bot",
    "BotType",
    "CreateBotBody",
    "UpdateBotBody",
    # Memory types
    "Memory",
    "MemoryType",
    "PipelineStage",
    "PermanenceLevel",
    "PrivacyLevel",
    "SourceType",
    "StoreMemoryBody",
    "SearchMemoriesBody",
    "ListMemoryQueryParams",
    "MemoryListResponse",
    "SearchMemoriesResponse",
    "ReprocessMemoryResponse",
    "PaginationMetadata",
    # Error types
    "MoaErrorResponse",
    "ValidationErrorDetail",
    "ApiError",
    "ValidationError",
    "AuthenticationError",
    "AuthorizationError",
    "NotFoundError",
    "ServiceUnavailableError",
    "NetworkError",
    "RequestLimitError",
]
