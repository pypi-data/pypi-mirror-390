import os
from unittest.mock import Mock, patch

import httpx
import pytest

from unsplash_client.client import UnsplashClient
from unsplash_client.exceptions import (
    UnsplashAuthenticationException,
    UnsplashClientException,
    UnsplashNotFoundException,
    UnsplashRateLimitException,
    UnsplashServerException,
)
from unsplash_client.search.models import (
    ContentFilter,
    OrderBy,
    Orientation,
    UnsplashSearchParams,
)


@pytest.fixture
def sample_params() -> UnsplashSearchParams:
    return UnsplashSearchParams(
        query="test",
        per_page=10,
        orientation=Orientation.LANDSCAPE,
        content_filter=ContentFilter.HIGH,
        page=1,
        order_by=OrderBy.RELEVANT,
    )


class TestUnsplashClientInit:
    def test_init_with_access_key(self) -> None:
        client = UnsplashClient(access_key="test_key")
        assert client.access_key == "test_key"
        assert client._base_url == "https://api.unsplash.com"

    def test_init_without_access_key_uses_env(self) -> None:
        with patch.dict(os.environ, {"UNSPLASH_API_KEY": "env_key"}):
            client = UnsplashClient()
            assert client.access_key == "env_key"

    def test_init_without_access_key_and_no_env(self) -> None:
        with (
            patch.dict(os.environ, {}, clear=True),
            pytest.raises(UnsplashAuthenticationException),
        ):
            UnsplashClient()

    def test_raises_exception_when_no_access_key(self) -> None:
        with (
            patch.dict(os.environ, {}, clear=True),
            pytest.raises(UnsplashAuthenticationException) as exc_info,
        ):
            UnsplashClient()

        error_message = str(exc_info.value).lower()
        assert "api key" in error_message or "access key" in error_message


class TestResolveSearchParams:
    def test_with_unsplash_params_object(
        self, sample_params: UnsplashSearchParams
    ) -> None:
        client = UnsplashClient(access_key="test_key")

        result = client._resolve_search_params(sample_params)

        assert result == sample_params
        assert result.query == "test"
        assert result.per_page == 10

    def test_with_string_query(self) -> None:
        client = UnsplashClient(access_key="test_key")

        result = client._resolve_search_params("sunset")

        assert result.query == "sunset"
        assert result.per_page == 10  # default value
        assert result.orientation == Orientation.LANDSCAPE

    def test_with_string_query_and_kwargs(self) -> None:
        client = UnsplashClient(access_key="test_key")

        result = client._resolve_search_params(
            "beach", per_page=20, orientation=Orientation.PORTRAIT
        )

        assert result.query == "beach"
        assert result.per_page == 20
        assert result.orientation == Orientation.PORTRAIT

    def test_with_query_kwarg(self) -> None:
        client = UnsplashClient(access_key="test_key")

        result = client._resolve_search_params(query="mountains", per_page=15)

        assert result.query == "mountains"
        assert result.per_page == 15

    def test_with_query_kwarg_only(self) -> None:
        client = UnsplashClient(access_key="test_key")

        result = client._resolve_search_params(query="nature")

        assert result.query == "nature"
        assert result.per_page == 10  # default

    def test_raises_error_when_no_query_or_params(self) -> None:
        client = UnsplashClient(access_key="test_key")

        with pytest.raises(ValueError) as exc_info:
            client._resolve_search_params()

        assert "Either 'params' or 'query' must be provided" in str(exc_info.value)

    def test_raises_error_with_only_kwargs(self) -> None:
        client = UnsplashClient(access_key="test_key")

        with pytest.raises(ValueError) as exc_info:
            client._resolve_search_params(per_page=20, orientation=Orientation.PORTRAIT)

        assert "Either 'params' or 'query' must be provided" in str(exc_info.value)


class TestHandleHttpStatusError:
    @pytest.mark.asyncio
    async def test_401_unauthorized(self, sample_params: UnsplashSearchParams) -> None:
        client = UnsplashClient(access_key="test_key")

        mock_response = Mock()
        mock_response.status_code = 401
        error = httpx.HTTPStatusError(
            "Unauthorized", request=Mock(), response=mock_response
        )

        with pytest.raises(UnsplashAuthenticationException) as exc_info:
            client._handle_http_status_error(sample_params, error)

        assert exc_info.value.query == "test"
        assert "access key" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_404_not_found(self, sample_params: UnsplashSearchParams) -> None:
        client = UnsplashClient(access_key="test_key")

        mock_response = Mock()
        mock_response.status_code = 404
        error = httpx.HTTPStatusError(
            "Not Found", request=Mock(), response=mock_response
        )

        with pytest.raises(UnsplashNotFoundException):
            client._handle_http_status_error(sample_params, error)

    @pytest.mark.asyncio
    async def test_429_with_retry_after(
        self, sample_params: UnsplashSearchParams
    ) -> None:
        client = UnsplashClient(access_key="test_key")

        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {"Retry-After": "60"}
        error = httpx.HTTPStatusError(
            "Rate Limited", request=Mock(), response=mock_response
        )

        with pytest.raises(UnsplashRateLimitException) as exc_info:
            client._handle_http_status_error(sample_params, error)

        assert exc_info.value.retry_after == 60

    @pytest.mark.asyncio
    async def test_429_without_retry_after(
        self, sample_params: UnsplashSearchParams
    ) -> None:
        client = UnsplashClient(access_key="test_key")

        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {}
        error = httpx.HTTPStatusError(
            "Rate Limited", request=Mock(), response=mock_response
        )

        with pytest.raises(UnsplashRateLimitException) as exc_info:
            client._handle_http_status_error(sample_params, error)

        assert exc_info.value.retry_after is None

    @pytest.mark.asyncio
    @pytest.mark.parametrize("status_code", [500, 502, 503, 504])
    async def test_5xx_server_errors(
        self, sample_params: UnsplashSearchParams, status_code: int
    ) -> None:
        client = UnsplashClient(access_key="test_key")

        mock_response = Mock()
        mock_response.status_code = status_code
        error = httpx.HTTPStatusError(
            "Server Error", request=Mock(), response=mock_response
        )

        with pytest.raises(UnsplashServerException) as exc_info:
            client._handle_http_status_error(sample_params, error)

        assert exc_info.value.status_code == status_code

    @pytest.mark.asyncio
    @pytest.mark.parametrize("status_code", [400, 403, 422])
    async def test_4xx_client_errors(
        self, sample_params: UnsplashSearchParams, status_code: int
    ) -> None:
        client = UnsplashClient(access_key="test_key")

        mock_response = Mock()
        mock_response.status_code = status_code
        error = httpx.HTTPStatusError(
            "Client Error", request=Mock(), response=mock_response
        )

        with pytest.raises(UnsplashClientException) as exc_info:
            client._handle_http_status_error(sample_params, error)

        assert exc_info.value.status_code == status_code
