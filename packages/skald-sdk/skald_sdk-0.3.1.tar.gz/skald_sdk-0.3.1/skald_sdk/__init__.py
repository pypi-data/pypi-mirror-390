"""
Skald Python SDK

Official Python SDK for Skald - The AI-powered knowledge management platform.
"""

from skald_sdk.client import Skald
from skald_sdk.types import (
    MemoData,
    MemoFileData,
    UpdateMemoData,
    ListMemosParams,
    SearchRequest,
    ChatRequest,
    CreateMemoResponse,
    UpdateMemoResponse,
    MemoStatusResponse,
    Memo,
    MemoListItem,
    ListMemosResponse,
    SearchResponse,
    SearchResult,
    ChatResponse,
    ChatStreamEvent,
    Filter,
    IdType,
    MemoStatus,
    SearchMethod,
    FilterOperator,
    FilterType,
)

__version__ = "0.3.1"
__all__ = [
    "Skald",
    "MemoData",
    "MemoFileData",
    "UpdateMemoData",
    "ListMemosParams",
    "SearchRequest",
    "ChatRequest",
    "CreateMemoResponse",
    "UpdateMemoResponse",
    "MemoStatusResponse",
    "Memo",
    "MemoListItem",
    "ListMemosResponse",
    "SearchResponse",
    "SearchResult",
    "ChatResponse",
    "ChatStreamEvent",
    "Filter",
    "IdType",
    "MemoStatus",
    "SearchMethod",
    "FilterOperator",
    "FilterType",
]
