# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from raccoonai import RaccoonAI, AsyncRaccoonAI
from tests.utils import assert_matches_type
from raccoonai.types.fleet import (
    ExtensionAllResponse,
    ExtensionGetResponse,
    ExtensionUploadResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestExtensions:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_delete(self, client: RaccoonAI) -> None:
        extension = client.fleet.extensions.delete(
            "extensionId",
        )
        assert_matches_type(object, extension, path=["response"])

    @parametrize
    def test_raw_response_delete(self, client: RaccoonAI) -> None:
        response = client.fleet.extensions.with_raw_response.delete(
            "extensionId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        extension = response.parse()
        assert_matches_type(object, extension, path=["response"])

    @parametrize
    def test_streaming_response_delete(self, client: RaccoonAI) -> None:
        with client.fleet.extensions.with_streaming_response.delete(
            "extensionId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            extension = response.parse()
            assert_matches_type(object, extension, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_delete(self, client: RaccoonAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `extension_id` but received ''"):
            client.fleet.extensions.with_raw_response.delete(
                "",
            )

    @parametrize
    def test_method_all(self, client: RaccoonAI) -> None:
        extension = client.fleet.extensions.all()
        assert_matches_type(ExtensionAllResponse, extension, path=["response"])

    @parametrize
    def test_raw_response_all(self, client: RaccoonAI) -> None:
        response = client.fleet.extensions.with_raw_response.all()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        extension = response.parse()
        assert_matches_type(ExtensionAllResponse, extension, path=["response"])

    @parametrize
    def test_streaming_response_all(self, client: RaccoonAI) -> None:
        with client.fleet.extensions.with_streaming_response.all() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            extension = response.parse()
            assert_matches_type(ExtensionAllResponse, extension, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_get(self, client: RaccoonAI) -> None:
        extension = client.fleet.extensions.get(
            "extensionId",
        )
        assert_matches_type(ExtensionGetResponse, extension, path=["response"])

    @parametrize
    def test_raw_response_get(self, client: RaccoonAI) -> None:
        response = client.fleet.extensions.with_raw_response.get(
            "extensionId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        extension = response.parse()
        assert_matches_type(ExtensionGetResponse, extension, path=["response"])

    @parametrize
    def test_streaming_response_get(self, client: RaccoonAI) -> None:
        with client.fleet.extensions.with_streaming_response.get(
            "extensionId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            extension = response.parse()
            assert_matches_type(ExtensionGetResponse, extension, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_get(self, client: RaccoonAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `extension_id` but received ''"):
            client.fleet.extensions.with_raw_response.get(
                "",
            )

    @parametrize
    def test_method_upload(self, client: RaccoonAI) -> None:
        extension = client.fleet.extensions.upload(
            file=b"raw file contents",
        )
        assert_matches_type(ExtensionUploadResponse, extension, path=["response"])

    @parametrize
    def test_raw_response_upload(self, client: RaccoonAI) -> None:
        response = client.fleet.extensions.with_raw_response.upload(
            file=b"raw file contents",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        extension = response.parse()
        assert_matches_type(ExtensionUploadResponse, extension, path=["response"])

    @parametrize
    def test_streaming_response_upload(self, client: RaccoonAI) -> None:
        with client.fleet.extensions.with_streaming_response.upload(
            file=b"raw file contents",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            extension = response.parse()
            assert_matches_type(ExtensionUploadResponse, extension, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncExtensions:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_delete(self, async_client: AsyncRaccoonAI) -> None:
        extension = await async_client.fleet.extensions.delete(
            "extensionId",
        )
        assert_matches_type(object, extension, path=["response"])

    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncRaccoonAI) -> None:
        response = await async_client.fleet.extensions.with_raw_response.delete(
            "extensionId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        extension = await response.parse()
        assert_matches_type(object, extension, path=["response"])

    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncRaccoonAI) -> None:
        async with async_client.fleet.extensions.with_streaming_response.delete(
            "extensionId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            extension = await response.parse()
            assert_matches_type(object, extension, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_delete(self, async_client: AsyncRaccoonAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `extension_id` but received ''"):
            await async_client.fleet.extensions.with_raw_response.delete(
                "",
            )

    @parametrize
    async def test_method_all(self, async_client: AsyncRaccoonAI) -> None:
        extension = await async_client.fleet.extensions.all()
        assert_matches_type(ExtensionAllResponse, extension, path=["response"])

    @parametrize
    async def test_raw_response_all(self, async_client: AsyncRaccoonAI) -> None:
        response = await async_client.fleet.extensions.with_raw_response.all()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        extension = await response.parse()
        assert_matches_type(ExtensionAllResponse, extension, path=["response"])

    @parametrize
    async def test_streaming_response_all(self, async_client: AsyncRaccoonAI) -> None:
        async with async_client.fleet.extensions.with_streaming_response.all() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            extension = await response.parse()
            assert_matches_type(ExtensionAllResponse, extension, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_get(self, async_client: AsyncRaccoonAI) -> None:
        extension = await async_client.fleet.extensions.get(
            "extensionId",
        )
        assert_matches_type(ExtensionGetResponse, extension, path=["response"])

    @parametrize
    async def test_raw_response_get(self, async_client: AsyncRaccoonAI) -> None:
        response = await async_client.fleet.extensions.with_raw_response.get(
            "extensionId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        extension = await response.parse()
        assert_matches_type(ExtensionGetResponse, extension, path=["response"])

    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncRaccoonAI) -> None:
        async with async_client.fleet.extensions.with_streaming_response.get(
            "extensionId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            extension = await response.parse()
            assert_matches_type(ExtensionGetResponse, extension, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_get(self, async_client: AsyncRaccoonAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `extension_id` but received ''"):
            await async_client.fleet.extensions.with_raw_response.get(
                "",
            )

    @parametrize
    async def test_method_upload(self, async_client: AsyncRaccoonAI) -> None:
        extension = await async_client.fleet.extensions.upload(
            file=b"raw file contents",
        )
        assert_matches_type(ExtensionUploadResponse, extension, path=["response"])

    @parametrize
    async def test_raw_response_upload(self, async_client: AsyncRaccoonAI) -> None:
        response = await async_client.fleet.extensions.with_raw_response.upload(
            file=b"raw file contents",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        extension = await response.parse()
        assert_matches_type(ExtensionUploadResponse, extension, path=["response"])

    @parametrize
    async def test_streaming_response_upload(self, async_client: AsyncRaccoonAI) -> None:
        async with async_client.fleet.extensions.with_streaming_response.upload(
            file=b"raw file contents",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            extension = await response.parse()
            assert_matches_type(ExtensionUploadResponse, extension, path=["response"])

        assert cast(Any, response.is_closed) is True
