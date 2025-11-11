# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from raccoonai import RaccoonAI, AsyncRaccoonAI
from tests.utils import assert_matches_type
from raccoonai.types.tail import AppAllResponse, AppLinkedResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestApps:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_all(self, client: RaccoonAI) -> None:
        app = client.tail.apps.all()
        assert_matches_type(AppAllResponse, app, path=["response"])

    @parametrize
    def test_raw_response_all(self, client: RaccoonAI) -> None:
        response = client.tail.apps.with_raw_response.all()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        app = response.parse()
        assert_matches_type(AppAllResponse, app, path=["response"])

    @parametrize
    def test_streaming_response_all(self, client: RaccoonAI) -> None:
        with client.tail.apps.with_streaming_response.all() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            app = response.parse()
            assert_matches_type(AppAllResponse, app, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_linked(self, client: RaccoonAI) -> None:
        app = client.tail.apps.linked(
            raccoon_passcode="raccoonPasscode",
        )
        assert_matches_type(AppLinkedResponse, app, path=["response"])

    @parametrize
    def test_raw_response_linked(self, client: RaccoonAI) -> None:
        response = client.tail.apps.with_raw_response.linked(
            raccoon_passcode="raccoonPasscode",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        app = response.parse()
        assert_matches_type(AppLinkedResponse, app, path=["response"])

    @parametrize
    def test_streaming_response_linked(self, client: RaccoonAI) -> None:
        with client.tail.apps.with_streaming_response.linked(
            raccoon_passcode="raccoonPasscode",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            app = response.parse()
            assert_matches_type(AppLinkedResponse, app, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncApps:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_all(self, async_client: AsyncRaccoonAI) -> None:
        app = await async_client.tail.apps.all()
        assert_matches_type(AppAllResponse, app, path=["response"])

    @parametrize
    async def test_raw_response_all(self, async_client: AsyncRaccoonAI) -> None:
        response = await async_client.tail.apps.with_raw_response.all()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        app = await response.parse()
        assert_matches_type(AppAllResponse, app, path=["response"])

    @parametrize
    async def test_streaming_response_all(self, async_client: AsyncRaccoonAI) -> None:
        async with async_client.tail.apps.with_streaming_response.all() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            app = await response.parse()
            assert_matches_type(AppAllResponse, app, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_linked(self, async_client: AsyncRaccoonAI) -> None:
        app = await async_client.tail.apps.linked(
            raccoon_passcode="raccoonPasscode",
        )
        assert_matches_type(AppLinkedResponse, app, path=["response"])

    @parametrize
    async def test_raw_response_linked(self, async_client: AsyncRaccoonAI) -> None:
        response = await async_client.tail.apps.with_raw_response.linked(
            raccoon_passcode="raccoonPasscode",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        app = await response.parse()
        assert_matches_type(AppLinkedResponse, app, path=["response"])

    @parametrize
    async def test_streaming_response_linked(self, async_client: AsyncRaccoonAI) -> None:
        async with async_client.tail.apps.with_streaming_response.linked(
            raccoon_passcode="raccoonPasscode",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            app = await response.parse()
            assert_matches_type(AppLinkedResponse, app, path=["response"])

        assert cast(Any, response.is_closed) is True
