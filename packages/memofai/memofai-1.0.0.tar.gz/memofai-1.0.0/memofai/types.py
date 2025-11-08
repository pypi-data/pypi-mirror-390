"""
Type definitions for memofai SDK.

This module contains all type definitions used throughout the SDK,
including dataclasses, TypedDict, and Literal types for type safety.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional, Union
from datetime import datetime

# ============================================================================
# Core Types
# ============================================================================

HttpMethod = Literal["GET", "POST", "PUT", "PATCH", "DELETE"]
Environment = Literal["dev", "alpha", "beta", "sandbox", "production"]


@dataclass
class EnvironmentConfig:
    """Configuration for each environment."""

    base_url: str
    description: str


ENVIRONMENTS: Dict[Environment, EnvironmentConfig] = {
    "dev": EnvironmentConfig(
        base_url="http://127.0.0.1:8000", description="Development environment for internal testing"
    ),
    "alpha": EnvironmentConfig(
        base_url="https://alpha-api.memof.ai", description="Alpha environment for early testing"
    ),
    "beta": EnvironmentConfig(
        base_url="https://beta-api.memof.ai",
        description="Beta environment for pre-production testing",
    ),
    "sandbox": EnvironmentConfig(
        base_url="https://sandbox-api.memof.ai",
        description="Sandbox environment for development and testing",
    ),
    "production": EnvironmentConfig(
        base_url="https://api.memof.ai", description="Production environment"
    ),
}

Headers = Dict[str, str]


@dataclass
class ClientConfig:
    """Configuration for the MOA client."""

    api_token: str
    environment: Environment = "production"
    timeout: int = 30000  # milliseconds
    retries: int = 3
    retry_delay: int = 1000  # milliseconds


@dataclass
class ApiResponse:
    """Generic API response wrapper."""

    data: Any
    status: int
    status_text: str
    headers: Headers


# ============================================================================
# User Types (from MoaUserBasicSerializer)
# ============================================================================


@dataclass
class BasicUser:
    """Basic user information."""

    id: str
    username: str
    email: str


# ============================================================================
# Workspace Types (from MoaWorkspace model & MoaWorkspaceSerializer)
# ============================================================================

WorkspaceRole = Literal["co-owner", "admin", "member", "readonly"]


@dataclass
class WorkspaceMember:
    """Workspace member information."""

    id: str
    user: BasicUser
    role: WorkspaceRole
    joined_at: str


@dataclass
class Workspace:
    """Workspace model."""

    id: str
    name: str
    description: Optional[str]
    owner: BasicUser
    members: List[WorkspaceMember]
    is_active: bool
    settings: Dict[str, Any]
    created_at: str
    updated_at: str


@dataclass
class CreateWorkspaceBody:
    """Request body for creating a workspace."""

    name: str
    description: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UpdateWorkspaceBody:
    """Request body for updating a workspace."""

    name: Optional[str] = None
    description: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# Bot Types (from MoaBot model & MoaBotSerializer)
# ============================================================================

BotType = Literal["conversational", "knowledge_base", "task_oriented", "analytical", "creative"]


@dataclass
class Bot:
    """Bot model."""

    id: str
    name: str
    description: Optional[str]
    moa_workspace: str
    is_active: bool
    type: BotType
    total_interactions: int
    last_interaction_at: Optional[str]
    total_memories: int
    last_memory_added_at: Optional[str]
    created_at: str
    updated_at: str


@dataclass
class CreateBotBody:
    """Request body for creating a bot."""

    name: str
    moa_workspace: str
    description: Optional[str] = None
    type: BotType = "conversational"
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UpdateBotBody:
    """Request body for updating a bot."""

    name: Optional[str] = None
    description: Optional[str] = None
    moa_workspace: Optional[str] = None
    is_active: Optional[bool] = None
    type: Optional[BotType] = None
    extra: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# Memory Types (from memory-service)
# ============================================================================

MemoryType = Literal["fact", "preference", "credential", "event", "task", "other"]
PipelineStage = Literal["captured", "processing", "completed", "failed"]
PermanenceLevel = Literal["ephemeral", "session", "permanent"]
PrivacyLevel = Literal["private", "team", "public"]
SourceType = Union[
    Literal["manual", "email", "call_transcript", "slack", "upload", "api", "sdk"], str
]


@dataclass
class Memory:
    """Memory model."""

    id: str
    bot_id: str
    user_note: Optional[str]
    source_type: SourceType
    source_id: Optional[str]
    source_url: Optional[str]
    content_text: str
    canonical_text: Optional[str]
    summary: Optional[str]
    memory_type: MemoryType
    event_datetime: Optional[str]
    deadline_datetime: Optional[str]
    location_text: Optional[str]
    participants: Optional[List[Any]]
    entities: Optional[Dict[str, Any]]
    importance_score: float
    permanence_level: PermanenceLevel
    expiration_date: Optional[str]
    pii_redacted: bool
    privacy_level: PrivacyLevel
    language: Optional[str]
    source_confidence: float
    last_accessed_at: Optional[str]
    retrieval_count: int
    verified_flag: bool
    verification_notes: Optional[str]
    pipeline_stage: PipelineStage
    created_at: str
    updated_at: str


@dataclass
class StoreMemoryBody:
    """Request body for storing a memory."""

    bot_id: str
    content_text: str
    source_type: SourceType
    user_note: Optional[str] = None
    source_id: Optional[str] = None
    source_url: Optional[str] = None
    canonical_text: Optional[str] = None
    summary: Optional[str] = None
    memory_type: Optional[MemoryType] = None
    event_datetime: Optional[str] = None
    deadline_datetime: Optional[str] = None
    location_text: Optional[str] = None
    participants: Optional[List[Any]] = None
    entities: Optional[Dict[str, Any]] = None
    importance_score: Optional[float] = None
    permanence_level: Optional[PermanenceLevel] = None
    expiration_date: Optional[str] = None
    pii_redacted: Optional[bool] = None
    privacy_level: Optional[PrivacyLevel] = None
    language: Optional[str] = None
    source_confidence: Optional[float] = None
    verified_flag: Optional[bool] = None
    verification_notes: Optional[str] = None
    pipeline_stage: Optional[PipelineStage] = None
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchMemoriesBody:
    """Request body for searching memories."""

    bot_id: str
    query: str
    top_k: Optional[int] = None
    generate_answer: Optional[bool] = None
    filters: Optional[Dict[str, Any]] = None
    extra: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# Query Parameter Types
# ============================================================================


@dataclass
class ListMemoryQueryParams:
    """Query parameters for listing memories."""

    memory_type: Optional[MemoryType] = None
    pipeline_stage: Optional[PipelineStage] = None
    limit: Optional[int] = None
    offset: Optional[int] = None
    extra: Dict[str, Union[str, int, bool]] = field(default_factory=dict)


# ============================================================================
# Response Types
# ============================================================================


@dataclass
class PaginationMetadata:
    """Pagination metadata for list responses."""

    limit: int
    offset: int
    total: int
    has_more: bool


@dataclass
class MemoryListResponse:
    """Response for listing memories."""

    memories: List[Memory]
    pagination: PaginationMetadata


@dataclass
class SearchMemoriesResponse:
    """Response for searching memories."""

    answer: Optional[str]
    evidence: List[Memory]
    retrieval_stats: Dict[str, Any]


@dataclass
class ReprocessMemoryResponse:
    """Response for reprocessing a memory."""

    success: bool
    message: str
    memory_id: str
    pipeline_stage: PipelineStage


# ============================================================================
# Error Types - Comprehensive Error Handling
# ============================================================================


@dataclass
class MoaErrorResponse:
    """Error response from the API."""

    detail: Optional[str] = None
    error_type: Optional[str] = None
    resource_type: Optional[Literal["workspace", "bot", "memory", "request"]] = None
    limit: Optional[int] = None
    current_usage: Optional[int] = None
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationErrorDetail:
    """Validation error detail."""

    field: str
    message: str
    code: Optional[str] = None
