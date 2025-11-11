# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from raccoonai import RaccoonAI, AsyncRaccoonAI
from tests.utils import assert_matches_type
from raccoonai.types.tail import (
    UserAllResponse,
    UserCreateResponse,
    UserStatusResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestUsers:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: RaccoonAI) -> None:
        user = client.tail.users.create(
            email="john.doe@example.com",
            name="john",
        )
        assert_matches_type(UserCreateResponse, user, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: RaccoonAI) -> None:
        response = client.tail.users.with_raw_response.create(
            email="john.doe@example.com",
            name="john",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = response.parse()
        assert_matches_type(UserCreateResponse, user, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: RaccoonAI) -> None:
        with client.tail.users.with_streaming_response.create(
            email="john.doe@example.com",
            name="john",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = response.parse()
            assert_matches_type(UserCreateResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_all(self, client: RaccoonAI) -> None:
        user = client.tail.users.all()
        assert_matches_type(UserAllResponse, user, path=["response"])

    @parametrize
    def test_method_all_with_all_params(self, client: RaccoonAI) -> None:
        user = client.tail.users.all(
            email_id="emailId",
            limit=1,
            page=1,
            raccoon_passcode="raccoonPasscode",
            search_query="searchQuery",
            sort_by="createdAt",
            sort_order="ascend",
        )
        assert_matches_type(UserAllResponse, user, path=["response"])

    @parametrize
    def test_raw_response_all(self, client: RaccoonAI) -> None:
        response = client.tail.users.with_raw_response.all()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = response.parse()
        assert_matches_type(UserAllResponse, user, path=["response"])

    @parametrize
    def test_streaming_response_all(self, client: RaccoonAI) -> None:
        with client.tail.users.with_streaming_response.all() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = response.parse()
            assert_matches_type(UserAllResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_status(self, client: RaccoonAI) -> None:
        user = client.tail.users.status(
            app_name="appName",
            raccoon_passcode="raccoonPasscode",
        )
        assert_matches_type(UserStatusResponse, user, path=["response"])

    @parametrize
    def test_raw_response_status(self, client: RaccoonAI) -> None:
        response = client.tail.users.with_raw_response.status(
            app_name="appName",
            raccoon_passcode="raccoonPasscode",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = response.parse()
        assert_matches_type(UserStatusResponse, user, path=["response"])

    @parametrize
    def test_streaming_response_status(self, client: RaccoonAI) -> None:
        with client.tail.users.with_streaming_response.status(
            app_name="appName",
            raccoon_passcode="raccoonPasscode",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = response.parse()
            assert_matches_type(UserStatusResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncUsers:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncRaccoonAI) -> None:
        user = await async_client.tail.users.create(
            email="john.doe@example.com",
            name="john",
        )
        assert_matches_type(UserCreateResponse, user, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncRaccoonAI) -> None:
        response = await async_client.tail.users.with_raw_response.create(
            email="john.doe@example.com",
            name="john",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = await response.parse()
        assert_matches_type(UserCreateResponse, user, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncRaccoonAI) -> None:
        async with async_client.tail.users.with_streaming_response.create(
            email="john.doe@example.com",
            name="john",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = await response.parse()
            assert_matches_type(UserCreateResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_all(self, async_client: AsyncRaccoonAI) -> None:
        user = await async_client.tail.users.all()
        assert_matches_type(UserAllResponse, user, path=["response"])

    @parametrize
    async def test_method_all_with_all_params(self, async_client: AsyncRaccoonAI) -> None:
        user = await async_client.tail.users.all(
            email_id="emailId",
            limit=1,
            page=1,
            raccoon_passcode="raccoonPasscode",
            search_query="searchQuery",
            sort_by="createdAt",
            sort_order="ascend",
        )
        assert_matches_type(UserAllResponse, user, path=["response"])

    @parametrize
    async def test_raw_response_all(self, async_client: AsyncRaccoonAI) -> None:
        response = await async_client.tail.users.with_raw_response.all()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = await response.parse()
        assert_matches_type(UserAllResponse, user, path=["response"])

    @parametrize
    async def test_streaming_response_all(self, async_client: AsyncRaccoonAI) -> None:
        async with async_client.tail.users.with_streaming_response.all() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = await response.parse()
            assert_matches_type(UserAllResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_status(self, async_client: AsyncRaccoonAI) -> None:
        user = await async_client.tail.users.status(
            app_name="appName",
            raccoon_passcode="raccoonPasscode",
        )
        assert_matches_type(UserStatusResponse, user, path=["response"])

    @parametrize
    async def test_raw_response_status(self, async_client: AsyncRaccoonAI) -> None:
        response = await async_client.tail.users.with_raw_response.status(
            app_name="appName",
            raccoon_passcode="raccoonPasscode",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = await response.parse()
        assert_matches_type(UserStatusResponse, user, path=["response"])

    @parametrize
    async def test_streaming_response_status(self, async_client: AsyncRaccoonAI) -> None:
        async with async_client.tail.users.with_streaming_response.status(
            app_name="appName",
            raccoon_passcode="raccoonPasscode",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = await response.parse()
            assert_matches_type(UserStatusResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True
