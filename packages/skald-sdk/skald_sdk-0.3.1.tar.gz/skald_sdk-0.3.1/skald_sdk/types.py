"""
Type definitions for the Skald SDK.

This module contains all the type definitions used throughout the SDK,
including request/response models and enums.
"""

from typing import Any, Dict, List, Literal, Optional, TypedDict, Union
from typing_extensions import NotRequired

# Type aliases for enums
IdType = Literal["memo_uuid", "reference_id"]
SearchMethod = Literal["chunk_semantic_search"]
FilterOperator = Literal["eq", "neq", "contains", "startswith", "endswith", "in", "not_in"]
FilterType = Literal["native_field", "custom_metadata"]
MemoStatus = Literal["processing", "processed", "error"]


# Input Types


class MemoData(TypedDict):
    """Data required to create a new memo."""

    title: str
    content: str
    metadata: NotRequired[Dict[str, Any]]
    reference_id: NotRequired[str]
    tags: NotRequired[List[str]]
    source: NotRequired[str]
    expiration_date: NotRequired[str]


class MemoFileData(TypedDict, total=False):
    """Optional data for creating a memo from a file upload."""

    title: str
    source: str
    reference_id: str
    expiration_date: str
    tags: List[str]
    metadata: Dict[str, Any]


class UpdateMemoData(TypedDict, total=False):
    """Data for updating an existing memo."""

    title: str
    content: str
    metadata: Dict[str, Any]
    client_reference_id: str
    source: str
    expiration_date: str


class ListMemosParams(TypedDict, total=False):
    """Parameters for listing memos."""

    page: int
    page_size: int


class Filter(TypedDict):
    """Filter for search and query operations."""

    field: str
    operator: FilterOperator
    value: Union[str, List[str]]
    filter_type: FilterType


class SearchRequest(TypedDict):
    """Request parameters for search operations."""

    query: str
    limit: NotRequired[int]
    filters: NotRequired[List[Filter]]


class ChatRequest(TypedDict):
    """Request parameters for chat operations."""

    query: str
    filters: NotRequired[List[Filter]]


# Output Types


class CreateMemoResponse(TypedDict):
    """Response from creating a memo."""

    memo_uuid: str


class UpdateMemoResponse(TypedDict):
    """Response from updating a memo."""

    ok: bool


class MemoStatusResponse(TypedDict):
    """Response from checking memo status."""

    memo_uuid: str
    status: MemoStatus
    processing_started_at: Optional[str]
    processing_completed_at: Optional[str]
    error_reason: Optional[str]


class Memo(TypedDict):
    """Complete memo details."""

    uuid: str
    created_at: str
    updated_at: str
    title: str
    content: str
    summary: str
    content_length: int
    metadata: Dict[str, Any]
    client_reference_id: Optional[str]
    source: Optional[str]
    type: str
    expiration_date: Optional[str]
    archived: bool
    pending: bool


class MemoListItem(TypedDict):
    """Lightweight memo information for list responses."""

    uuid: str
    created_at: str
    updated_at: str
    title: str
    summary: str
    content_length: int
    metadata: Dict[str, Any]
    client_reference_id: Optional[str]


class ListMemosResponse(TypedDict):
    """Response from listing memos."""

    count: int
    next: Optional[str]
    previous: Optional[str]
    results: List[MemoListItem]


class SearchResult(TypedDict):
    """A single search result."""

    memo_uuid: str
    chunk_uuid: str
    memo_title: str
    memo_summary: str
    content_snippet: str
    distance: Optional[float]


class SearchResponse(TypedDict):
    """Response from search operations."""

    results: List[SearchResult]


class ChatResponse(TypedDict):
    """Response from chat operations."""

    ok: bool
    response: str
    intermediate_steps: List[Any]


class ChatStreamEvent(TypedDict):
    """Event from streaming chat operations."""

    type: Literal["token", "done"]
    content: NotRequired[str]
