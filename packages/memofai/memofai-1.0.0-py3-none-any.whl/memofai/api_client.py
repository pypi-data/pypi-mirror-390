"""
API client for the memofai SDK.

This module provides the main MoaClient class with namespace-based API access
for workspaces, bots, and memories.
"""

from typing import Any, Dict, List, Optional, Union
from dataclasses import asdict

from .http_client import HttpClient, RequestConfig
from .endpoints import API_ENDPOINTS, EndpointName
from .types import (
    ClientConfig,
    Headers,
    # Workspace types
    Workspace,
    CreateWorkspaceBody,
    UpdateWorkspaceBody,
    # Bot types
    Bot,
    CreateBotBody,
    UpdateBotBody,
    # Memory types
    Memory,
    StoreMemoryBody,
    SearchMemoriesBody,
    ListMemoryQueryParams,
    MemoryListResponse,
    SearchMemoriesResponse,
    ReprocessMemoryResponse,
)


def _dataclass_to_dict(obj: Any) -> Dict[str, Any]:
    """Convert a dataclass to a dictionary, removing None values and 'extra' fields."""
    if not hasattr(obj, "__dataclass_fields__"):
        return obj

    result = asdict(obj)

    # Remove None values
    result = {k: v for k, v in result.items() if v is not None}

    # Merge 'extra' field if present
    if "extra" in result:
        extra = result.pop("extra")
        result.update(extra)

    return result


class WorkspaceNamespace:
    """Workspace namespace with all workspace-related methods."""

    def __init__(self, request_fn):
        self._request = request_fn

    def list(self) -> List[Workspace]:
        """List all workspaces for the authenticated user."""
        return self._request("listWorkspaces")

    def create(self, data: Union[CreateWorkspaceBody, Dict[str, Any]]) -> Workspace:
        """Create a new workspace."""
        if isinstance(data, CreateWorkspaceBody):
            data = _dataclass_to_dict(data)
        return self._request("createWorkspace", body=data)

    def retrieve(self, workspace_id: str) -> Workspace:
        """Get workspace details by ID."""
        return self._request("retrieveWorkspace", path_params={"workspace_id": workspace_id})

    def update(
        self, workspace_id: str, data: Union[UpdateWorkspaceBody, Dict[str, Any]]
    ) -> Workspace:
        """Update a workspace."""
        if isinstance(data, UpdateWorkspaceBody):
            data = _dataclass_to_dict(data)
        return self._request(
            "updateWorkspace", path_params={"workspace_id": workspace_id}, body=data
        )

    def delete(self, workspace_id: str) -> None:
        """Delete a workspace."""
        return self._request("deleteWorkspace", path_params={"workspace_id": workspace_id})


class BotNamespace:
    """Bot namespace with all bot-related methods."""

    def __init__(self, request_fn):
        self._request = request_fn

    def list(self) -> List[Bot]:
        """List all bots for the authenticated user."""
        return self._request("listBots")

    def create(self, data: Union[CreateBotBody, Dict[str, Any]]) -> Bot:
        """Create a new bot."""
        if isinstance(data, CreateBotBody):
            data = _dataclass_to_dict(data)
        return self._request("createBot", body=data)

    def retrieve(self, bot_id: str) -> Bot:
        """Get bot details by ID."""
        return self._request("retrieveBot", path_params={"bot_id": bot_id})

    def update(self, bot_id: str, data: Union[UpdateBotBody, Dict[str, Any]]) -> Bot:
        """Update a bot."""
        if isinstance(data, UpdateBotBody):
            data = _dataclass_to_dict(data)
        return self._request("updateBot", path_params={"bot_id": bot_id}, body=data)

    def delete(self, bot_id: str) -> None:
        """Delete a bot."""
        return self._request("deleteBot", path_params={"bot_id": bot_id})


class MemoryNamespace:
    """Memory namespace with all memory-related methods."""

    def __init__(self, request_fn):
        self._request = request_fn

    def store(self, data: Union[StoreMemoryBody, Dict[str, Any]]) -> Memory:
        """Store a new memory."""
        if isinstance(data, StoreMemoryBody):
            data = _dataclass_to_dict(data)
        return self._request("storeMemory", body=data)

    def list(
        self,
        bot_id: str,
        query_params: Optional[Union[ListMemoryQueryParams, Dict[str, Any]]] = None,
    ) -> MemoryListResponse:
        """List memories for a specific bot."""
        if isinstance(query_params, ListMemoryQueryParams):
            query_params = _dataclass_to_dict(query_params)
        return self._request(
            "listMemory", path_params={"bot_id": bot_id}, query_params=query_params
        )

    def reprocess(self, memory_id: str) -> ReprocessMemoryResponse:
        """Reprocess a memory."""
        return self._request("reprocessMemory", path_params={"memory_id": memory_id})

    def delete(self, memory_id: str) -> None:
        """Delete a memory."""
        return self._request("deleteMemory", path_params={"memory_id": memory_id})

    def search(self, data: Union[SearchMemoriesBody, Dict[str, Any]]) -> SearchMemoriesResponse:
        """Search memories with natural language query."""
        if isinstance(data, SearchMemoriesBody):
            data = _dataclass_to_dict(data)
        return self._request("searchMemories", body=data)


class MoaClient:
    """
    Main client for the Memory-of-Agents (MOA) API.

    Provides namespace-based access to workspaces, bots, and memories.

    Example:
        >>> client = MoaClient(ClientConfig(api_token='moa_...'))
        >>> workspaces = client.workspaces.list()
        >>> bot = client.bots.create({'name': 'My Bot', 'moa_workspace': workspace_id})
        >>> memory = client.memories.store({'bot_id': bot_id, 'content_text': '...'})
    """

    def __init__(self, config: ClientConfig):
        """
        Initialize the MOA client.

        Args:
            config: Client configuration including API token and environment
        """
        self.http_client = HttpClient(config)

        # Initialize namespaces
        self.workspaces = WorkspaceNamespace(self._request)
        self.bots = BotNamespace(self._request)
        self.memories = MemoryNamespace(self._request)

    def _request(
        self,
        endpoint_name: EndpointName,
        path_params: Optional[Dict[str, str]] = None,
        query_params: Optional[Dict[str, Union[str, int, bool]]] = None,
        body: Optional[Dict[str, Any]] = None,
        headers: Optional[Headers] = None,
    ) -> Any:
        """
        Generic request method with path parameter substitution.

        Args:
            endpoint_name: Name of the endpoint to call
            path_params: Path parameters to substitute in the URL
            query_params: Query parameters to include in the URL
            body: Request body
            headers: Additional headers

        Returns:
            Response data
        """
        endpoint = API_ENDPOINTS[endpoint_name]
        path = endpoint["path"]

        # Substitute path parameters
        if path_params:
            for key, value in path_params.items():
                path = path.replace(f":{key}", value)

        # Filter out None values from query params
        clean_query_params = None
        if query_params:
            clean_query_params = {k: v for k, v in query_params.items() if v is not None}

        # Make request
        request_config = RequestConfig(
            path=path,
            method=endpoint["method"],
            query_params=clean_query_params,
            body=body,
            headers=headers,
        )

        response = self.http_client.request(request_config)
        return response.data
