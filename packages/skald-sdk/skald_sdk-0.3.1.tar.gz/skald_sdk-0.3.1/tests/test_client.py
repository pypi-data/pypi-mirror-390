"""
Comprehensive unit tests for the Skald SDK client.

All tests use mocked HTTP responses and do not require a running Skald instance.
"""

import json
from typing import AsyncIterator

import pytest
from pytest_mock import MockerFixture

from skald_sdk import Skald
from skald_sdk.types import (
    ChatStreamEvent,
    CreateMemoResponse,
    ListMemosResponse,
    Memo,
    SearchResponse,
)


@pytest.fixture
async def skald_client() -> AsyncIterator[Skald]:
    """Fixture that provides a Skald client instance."""
    client = Skald("test-api-key", "https://api.test.com")
    yield client
    await client.close()


class TestInitialization:
    """Tests for Skald client initialization."""

    async def test_initialization_with_defaults(self) -> None:
        """Test client initialization with default base URL."""
        client = Skald("test-key")
        assert client._api_key == "test-key"
        assert client._base_url == "https://api.useskald.com"
        await client.close()

    async def test_initialization_with_custom_base_url(self) -> None:
        """Test client initialization with custom base URL."""
        client = Skald("test-key", "https://custom.api.com")
        assert client._api_key == "test-key"
        assert client._base_url == "https://custom.api.com"
        await client.close()

    async def test_trailing_slash_removed_from_base_url(self) -> None:
        """Test that trailing slashes are removed from base URL."""
        client = Skald("test-key", "https://api.test.com/")
        assert client._base_url == "https://api.test.com"
        await client.close()

    async def test_context_manager(self) -> None:
        """Test async context manager usage."""
        async with Skald("test-key") as client:
            assert client._api_key == "test-key"


class TestCreateMemo:
    """Tests for creating memos."""

    async def test_create_memo_success(
        self, skald_client: Skald, mocker: MockerFixture
    ) -> None:
        """Test successful memo creation."""
        mock_response = mocker.Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {"ok": True}

        mocker.patch.object(
            skald_client._client, "request", return_value=mock_response
        )

        result = await skald_client.create_memo({
            "title": "Test Memo",
            "content": "Test content",
        })

        assert result == {"ok": True}
        skald_client._client.request.assert_called_once_with(
            "POST",
            "https://api.test.com/api/v1/memo",
            json={
                "title": "Test Memo",
                "content": "Test content",
                "metadata": {},  # Auto-initialized
            },
        )

    async def test_create_memo_with_metadata(
        self, skald_client: Skald, mocker: MockerFixture
    ) -> None:
        """Test memo creation with metadata."""
        mock_response = mocker.Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {"ok": True}

        mocker.patch.object(
            skald_client._client, "request", return_value=mock_response
        )

        result = await skald_client.create_memo({
            "title": "Test Memo",
            "content": "Test content",
            "metadata": {"key": "value"},
            "tags": ["tag1", "tag2"],
            "source": "test-source",
        })

        assert result == {"ok": True}
        call_args = skald_client._client.request.call_args
        assert call_args[1]["json"]["metadata"] == {"key": "value"}
        assert call_args[1]["json"]["tags"] == ["tag1", "tag2"]

    async def test_create_memo_error(
        self, skald_client: Skald, mocker: MockerFixture
    ) -> None:
        """Test memo creation with API error."""
        mock_response = mocker.Mock()
        mock_response.is_success = False
        mock_response.status_code = 400
        mock_response.text = "Bad Request"

        mocker.patch.object(
            skald_client._client, "request", return_value=mock_response
        )

        with pytest.raises(Exception, match="Skald API error \\(400\\): Bad Request"):
            await skald_client.create_memo({
                "title": "Test",
                "content": "Test",
            })


class TestGetMemo:
    """Tests for retrieving memos."""

    async def test_get_memo_by_uuid(
        self, skald_client: Skald, mocker: MockerFixture
    ) -> None:
        """Test retrieving a memo by UUID."""
        mock_memo = {
            "uuid": "550e8400-e29b-41d4-a716-446655440000",
            "title": "Test Memo",
            "content": "Test content",
            "summary": "Test summary",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
            "content_length": 12,
            "metadata": {},
            "client_reference_id": None,
            "source": None,
            "type": "memo",
            "expiration_date": None,
            "archived": False,
            "pending": False,
            "tags": [],
            "chunks": [],
        }

        mock_response = mocker.Mock()
        mock_response.is_success = True
        mock_response.json.return_value = mock_memo

        mocker.patch.object(
            skald_client._client, "request", return_value=mock_response
        )

        result = await skald_client.get_memo("550e8400-e29b-41d4-a716-446655440000")

        assert result == mock_memo
        skald_client._client.request.assert_called_once_with(
            "GET",
            "https://api.test.com/api/v1/memo/550e8400-e29b-41d4-a716-446655440000",
            json=None,
        )

    async def test_get_memo_by_reference_id(
        self, skald_client: Skald, mocker: MockerFixture
    ) -> None:
        """Test retrieving a memo by reference ID."""
        mock_memo = {
            "uuid": "550e8400-e29b-41d4-a716-446655440000",
            "title": "Test Memo",
            "content": "Test content",
            "summary": "Test summary",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
            "content_length": 12,
            "metadata": {},
            "client_reference_id": "ref-123",
            "source": None,
            "type": "memo",
            "expiration_date": None,
            "archived": False,
            "pending": False,
            "tags": [],
            "chunks": [],
        }

        mock_response = mocker.Mock()
        mock_response.is_success = True
        mock_response.json.return_value = mock_memo

        mocker.patch.object(
            skald_client._client, "request", return_value=mock_response
        )

        result = await skald_client.get_memo("ref-123", id_type="reference_id")

        assert result == mock_memo
        skald_client._client.request.assert_called_once_with(
            "GET",
            "https://api.test.com/api/v1/memo/ref-123?id_type=reference_id",
            json=None,
        )

    async def test_get_memo_url_encoding(
        self, skald_client: Skald, mocker: MockerFixture
    ) -> None:
        """Test that memo IDs are properly URL encoded."""
        mock_response = mocker.Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {}

        mocker.patch.object(
            skald_client._client, "request", return_value=mock_response
        )

        await skald_client.get_memo("id with spaces")

        call_args = skald_client._client.request.call_args[0]
        assert "id%20with%20spaces" in call_args[1]

    async def test_get_memo_invalid_id_type(self, skald_client: Skald) -> None:
        """Test error handling for invalid ID type."""
        with pytest.raises(ValueError, match="Invalid id_type"):
            await skald_client.get_memo("some-id", id_type="invalid")  # type: ignore


class TestListMemos:
    """Tests for listing memos."""

    async def test_list_memos_default_params(
        self, skald_client: Skald, mocker: MockerFixture
    ) -> None:
        """Test listing memos with default parameters."""
        mock_response_data = {
            "count": 2,
            "next": None,
            "previous": None,
            "results": [
                {
                    "uuid": "uuid-1",
                    "title": "Memo 1",
                    "summary": "Summary 1",
                    "created_at": "2023-01-01T00:00:00Z",
                    "updated_at": "2023-01-01T00:00:00Z",
                    "content_length": 100,
                    "metadata": {},
                    "client_reference_id": None,
                },
                {
                    "uuid": "uuid-2",
                    "title": "Memo 2",
                    "summary": "Summary 2",
                    "created_at": "2023-01-02T00:00:00Z",
                    "updated_at": "2023-01-02T00:00:00Z",
                    "content_length": 200,
                    "metadata": {},
                    "client_reference_id": None,
                },
            ],
        }

        mock_response = mocker.Mock()
        mock_response.is_success = True
        mock_response.json.return_value = mock_response_data

        mocker.patch.object(
            skald_client._client, "request", return_value=mock_response
        )

        result = await skald_client.list_memos()

        assert result == mock_response_data
        skald_client._client.request.assert_called_once_with(
            "GET",
            "https://api.test.com/api/v1/memo?page=1&page_size=20",
            json=None,
        )

    async def test_list_memos_custom_params(
        self, skald_client: Skald, mocker: MockerFixture
    ) -> None:
        """Test listing memos with custom parameters."""
        mock_response = mocker.Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {
            "count": 100,
            "next": "next-url",
            "previous": None,
            "results": [],
        }

        mocker.patch.object(
            skald_client._client, "request", return_value=mock_response
        )

        await skald_client.list_memos({"page": 2, "page_size": 50})

        skald_client._client.request.assert_called_once_with(
            "GET",
            "https://api.test.com/api/v1/memo?page=2&page_size=50",
            json=None,
        )


class TestUpdateMemo:
    """Tests for updating memos."""

    async def test_update_memo_by_uuid(
        self, skald_client: Skald, mocker: MockerFixture
    ) -> None:
        """Test updating a memo by UUID."""
        mock_response = mocker.Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {"ok": True}

        mocker.patch.object(
            skald_client._client, "request", return_value=mock_response
        )

        result = await skald_client.update_memo(
            "550e8400-e29b-41d4-a716-446655440000",
            {"title": "Updated Title"},
        )

        assert result == {"ok": True}
        skald_client._client.request.assert_called_once_with(
            "PATCH",
            "https://api.test.com/api/v1/memo/550e8400-e29b-41d4-a716-446655440000",
            json={"title": "Updated Title"},
        )

    async def test_update_memo_by_reference_id(
        self, skald_client: Skald, mocker: MockerFixture
    ) -> None:
        """Test updating a memo by reference ID."""
        mock_response = mocker.Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {"ok": True}

        mocker.patch.object(
            skald_client._client, "request", return_value=mock_response
        )

        await skald_client.update_memo(
            "ref-123",
            {"content": "Updated content"},
            id_type="reference_id",
        )

        skald_client._client.request.assert_called_once_with(
            "PATCH",
            "https://api.test.com/api/v1/memo/ref-123?id_type=reference_id",
            json={"content": "Updated content"},
        )

    async def test_update_memo_invalid_id_type(self, skald_client: Skald) -> None:
        """Test error handling for invalid ID type."""
        with pytest.raises(ValueError, match="Invalid id_type"):
            await skald_client.update_memo(
                "some-id", {"title": "Test"}, id_type="invalid"  # type: ignore
            )


class TestDeleteMemo:
    """Tests for deleting memos."""

    async def test_delete_memo_by_uuid(
        self, skald_client: Skald, mocker: MockerFixture
    ) -> None:
        """Test deleting a memo by UUID."""
        mock_response = mocker.Mock()
        mock_response.is_success = True

        mocker.patch.object(
            skald_client._client, "request", return_value=mock_response
        )

        result = await skald_client.delete_memo("550e8400-e29b-41d4-a716-446655440000")

        assert result is None
        skald_client._client.request.assert_called_once_with(
            "DELETE",
            "https://api.test.com/api/v1/memo/550e8400-e29b-41d4-a716-446655440000",
            json=None,
        )

    async def test_delete_memo_by_reference_id(
        self, skald_client: Skald, mocker: MockerFixture
    ) -> None:
        """Test deleting a memo by reference ID."""
        mock_response = mocker.Mock()
        mock_response.is_success = True

        mocker.patch.object(
            skald_client._client, "request", return_value=mock_response
        )

        await skald_client.delete_memo("ref-123", id_type="reference_id")

        skald_client._client.request.assert_called_once_with(
            "DELETE",
            "https://api.test.com/api/v1/memo/ref-123?id_type=reference_id",
            json=None,
        )


class TestSearch:
    """Tests for search operations."""

    async def test_search_vector(
        self, skald_client: Skald, mocker: MockerFixture
    ) -> None:
        """Test vector search."""
        mock_response_data = {
            "results": [
                {
                    "memo_uuid": "memo-1",
                    "chunk_uuid": "chunk-1",
                    "memo_title": "Result 1",
                    "memo_summary": "Summary 1",
                    "content_snippet": "Snippet 1",
                    "distance": 0.5,
                },
                {   
                    "memo_uuid": "memo-2",
                    "chunk_uuid": "chunk-2",
                    "memo_title": "Result 2",
                    "memo_summary": "Summary 2",
                    "content_snippet": "Snippet 2",
                    "distance": 0.7,
                },
            ]
        }

        mock_response = mocker.Mock()
        mock_response.is_success = True
        mock_response.json.return_value = mock_response_data

        mocker.patch.object(
            skald_client._client, "request", return_value=mock_response
        )

        result = await skald_client.search({
            "query": "test query",
            "limit": 10,
        })

        assert result == mock_response_data
        call_args = skald_client._client.request.call_args
        assert call_args[1]["json"]["query"] == "test query"

    async def test_search_with_filters(
        self, skald_client: Skald, mocker: MockerFixture
    ) -> None:
        """Test search with filters."""
        mock_response = mocker.Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {"results": []}

        mocker.patch.object(
            skald_client._client, "request", return_value=mock_response
        )

        await skald_client.search({
            "query": "test",
            "filters": [
                {
                    "field": "source",
                    "operator": "eq",
                    "value": "notion",
                    "filter_type": "native_field",
                }
            ],
        })

        call_args = skald_client._client.request.call_args
        assert len(call_args[1]["json"]["filters"]) == 1
        assert call_args[1]["json"]["filters"][0]["field"] == "source"


class TestChat:
    """Tests for chat operations."""

    async def test_chat_non_streaming(
        self, skald_client: Skald, mocker: MockerFixture
    ) -> None:
        """Test non-streaming chat."""
        mock_response_data = {
            "ok": True,
            "response": "This is the answer [[1]]",
            "intermediate_steps": [],
        }

        mock_response = mocker.Mock()
        mock_response.is_success = True
        mock_response.json.return_value = mock_response_data

        mocker.patch.object(
            skald_client._client, "request", return_value=mock_response
        )

        result = await skald_client.chat({"query": "What is the answer?"})

        assert result == "This is the answer [[1]]"
        call_args = skald_client._client.request.call_args
        assert call_args[1]["json"]["query"] == "What is the answer?"
        assert call_args[1]["json"]["stream"] is False

    async def test_chat_with_filters(
        self, skald_client: Skald, mocker: MockerFixture
    ) -> None:
        """Test chat with filters."""
        mock_response = mocker.Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {
            "ok": True,
            "response": "Answer",
            "intermediate_steps": [],
        }

        mocker.patch.object(
            skald_client._client, "request", return_value=mock_response
        )

        await skald_client.chat({
            "query": "test",
            "filters": [
                {
                    "field": "tags",
                    "operator": "in",
                    "value": ["tag1"],
                    "filter_type": "native_field",
                }
            ],
        })

        call_args = skald_client._client.request.call_args
        assert call_args[1]["json"]["filters"][0]["field"] == "tags"

    async def test_streamed_chat(
        self, skald_client: Skald, mocker: MockerFixture
    ) -> None:
        """Test streaming chat."""
        # Mock streaming response
        stream_data = [
            b'data: {"type":"token","content":"Hello"}\n',
            b'data: {"type":"token","content":" world"}\n',
            b'data: {"type":"done"}\n',
        ]

        mock_response = mocker.Mock()
        mock_response.is_success = True

        async def mock_aiter_bytes():
            for chunk in stream_data:
                yield chunk

        mock_response.aiter_bytes = mock_aiter_bytes

        mock_stream = mocker.MagicMock()
        mock_stream.__aenter__.return_value = mock_response
        mock_stream.__aexit__.return_value = None

        mocker.patch.object(skald_client._client, "stream", return_value=mock_stream)

        events = []
        async for event in skald_client.streamed_chat({"query": "test"}):
            events.append(event)

        assert len(events) == 3
        assert events[0] == {"type": "token", "content": "Hello"}
        assert events[1] == {"type": "token", "content": " world"}
        assert events[2] == {"type": "done"}

    async def test_streamed_chat_skips_ping(
        self, skald_client: Skald, mocker: MockerFixture
    ) -> None:
        """Test that streaming chat skips ping messages."""
        stream_data = [
            b'data: {"type":"token","content":"Hello"}\n',
            b': ping\n',
            b'data: {"type":"token","content":" world"}\n',
            b'data: {"type":"done"}\n',
        ]

        mock_response = mocker.Mock()
        mock_response.is_success = True

        async def mock_aiter_bytes():
            for chunk in stream_data:
                yield chunk

        mock_response.aiter_bytes = mock_aiter_bytes

        mock_stream = mocker.MagicMock()
        mock_stream.__aenter__.return_value = mock_response
        mock_stream.__aexit__.return_value = None

        mocker.patch.object(skald_client._client, "stream", return_value=mock_stream)

        events = []
        async for event in skald_client.streamed_chat({"query": "test"}):
            events.append(event)

        # Should only have 3 events (ping is skipped)
        assert len(events) == 3


class TestErrorHandling:
    """Tests for error handling."""

    async def test_api_error_handling(
        self, skald_client: Skald, mocker: MockerFixture
    ) -> None:
        """Test that API errors are properly raised."""
        mock_response = mocker.Mock()
        mock_response.is_success = False
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"

        mocker.patch.object(
            skald_client._client, "request", return_value=mock_response
        )

        with pytest.raises(Exception, match="Skald API error \\(401\\): Unauthorized"):
            await skald_client.create_memo({"title": "Test", "content": "Test"})

    async def test_streaming_error_handling(
        self, skald_client: Skald, mocker: MockerFixture
    ) -> None:
        """Test error handling in streaming operations."""
        mock_response = mocker.Mock()
        mock_response.is_success = False
        mock_response.status_code = 500

        # Make aread an async function
        async def mock_aread():
            return b"Internal Server Error"

        mock_response.aread = mock_aread

        mock_stream = mocker.MagicMock()
        mock_stream.__aenter__.return_value = mock_response
        mock_stream.__aexit__.return_value = None

        mocker.patch.object(skald_client._client, "stream", return_value=mock_stream)

        with pytest.raises(Exception, match="Skald API error \\(500\\)"):
            async for _ in skald_client.streamed_chat({"query": "test"}):
                pass

    async def test_invalid_json_in_stream_is_skipped(
        self, skald_client: Skald, mocker: MockerFixture
    ) -> None:
        """Test that invalid JSON lines in streams are silently skipped."""
        stream_data = [
            b'data: {"type":"token","content":"Hello"}\n',
            b'data: invalid json\n',
            b'data: {"type":"token","content":" world"}\n',
            b'data: {"type":"done"}\n',
        ]

        mock_response = mocker.Mock()
        mock_response.is_success = True

        async def mock_aiter_bytes():
            for chunk in stream_data:
                yield chunk

        mock_response.aiter_bytes = mock_aiter_bytes

        mock_stream = mocker.MagicMock()
        mock_stream.__aenter__.return_value = mock_response
        mock_stream.__aexit__.return_value = None

        mocker.patch.object(skald_client._client, "stream", return_value=mock_stream)

        events = []
        async for event in skald_client.streamed_chat({"query": "test"}):
            events.append(event)

        # Invalid JSON should be skipped
        assert len(events) == 3
        assert events[0]["content"] == "Hello"
        assert events[1]["content"] == " world"
