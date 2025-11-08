"""
Endpoint definitions for the memofai SDK.

This module defines all API endpoints with their paths, methods, and descriptions.
Only includes @flexible_auth_required endpoints.
"""

from typing import Dict, Literal, TypedDict
from .types import HttpMethod


class EndpointConfig(TypedDict):
    """Configuration for an API endpoint."""

    path: str
    method: HttpMethod
    description: str


# ============================================================================
# Workspace Endpoints (5 endpoints)
# ============================================================================

WORKSPACE_ENDPOINTS: Dict[str, EndpointConfig] = {
    "listWorkspaces": {
        "path": "/api/workspaces/workspaces",
        "method": "GET",
        "description": "List all user workspaces",
    },
    "createWorkspace": {
        "path": "/api/workspaces/workspace/create",
        "method": "POST",
        "description": "Create a new workspace",
    },
    "retrieveWorkspace": {
        "path": "/api/workspaces/workspace/:workspace_id",
        "method": "GET",
        "description": "Get workspace details",
    },
    "updateWorkspace": {
        "path": "/api/workspaces/workspace/:workspace_id/update",
        "method": "PUT",
        "description": "Update workspace",
    },
    "deleteWorkspace": {
        "path": "/api/workspaces/workspace/:workspace_id/delete",
        "method": "DELETE",
        "description": "Delete workspace",
    },
}

# ============================================================================
# Bot Endpoints (5 endpoints)
# ============================================================================

BOT_ENDPOINTS: Dict[str, EndpointConfig] = {
    "listBots": {
        "path": "/api/bots/bots",
        "method": "GET",
        "description": "List all user bots",
    },
    "createBot": {
        "path": "/api/bots/bot/create",
        "method": "POST",
        "description": "Create a new bot",
    },
    "retrieveBot": {
        "path": "/api/bots/bot/:bot_id",
        "method": "GET",
        "description": "Get bot details",
    },
    "updateBot": {
        "path": "/api/bots/bot/:bot_id/update",
        "method": "PUT",
        "description": "Update bot",
    },
    "deleteBot": {
        "path": "/api/bots/bot/:bot_id/delete",
        "method": "DELETE",
        "description": "Delete bot",
    },
}

# ============================================================================
# Memory Endpoints (5 endpoints)
# ============================================================================

MEMORY_ENDPOINTS: Dict[str, EndpointConfig] = {
    "storeMemory": {
        "path": "/api/integrations/memory/store",
        "method": "POST",
        "description": "Store a new memory",
    },
    "listMemory": {
        "path": "/api/integrations/memory/:bot_id/list",
        "method": "GET",
        "description": "List memories for a specific bot",
    },
    "reprocessMemory": {
        "path": "/api/integrations/memory/:memory_id/reprocess",
        "method": "PATCH",
        "description": "Reprocess a memory",
    },
    "deleteMemory": {
        "path": "/api/integrations/memory/:memory_id/delete",
        "method": "DELETE",
        "description": "Delete a memory",
    },
    "searchMemories": {
        "path": "/api/integrations/memory/search",
        "method": "POST",
        "description": "Search memories with natural language query",
    },
}

# ============================================================================
# Combined Endpoints
# ============================================================================

API_ENDPOINTS: Dict[str, EndpointConfig] = {
    **WORKSPACE_ENDPOINTS,
    **BOT_ENDPOINTS,
    **MEMORY_ENDPOINTS,
}

EndpointName = Literal[
    "listWorkspaces",
    "createWorkspace",
    "retrieveWorkspace",
    "updateWorkspace",
    "deleteWorkspace",
    "listBots",
    "createBot",
    "retrieveBot",
    "updateBot",
    "deleteBot",
    "storeMemory",
    "listMemory",
    "reprocessMemory",
    "deleteMemory",
    "searchMemories",
]
