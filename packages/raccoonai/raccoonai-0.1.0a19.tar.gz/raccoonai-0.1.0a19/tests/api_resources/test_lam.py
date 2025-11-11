# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from raccoonai import RaccoonAI, AsyncRaccoonAI
from tests.utils import assert_matches_type
from raccoonai.types import LamRunResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestLam:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_run_overload_1(self, client: RaccoonAI) -> None:
        lam = client.lam.run(
            query="Find YCombinator startups who got funded in W24.",
            raccoon_passcode="<end-user-raccoon-passcode>",
        )
        assert_matches_type(LamRunResponse, lam, path=["response"])

    @parametrize
    def test_method_run_with_all_params_overload_1(self, client: RaccoonAI) -> None:
        lam = client.lam.run(
            query="Find YCombinator startups who got funded in W24.",
            raccoon_passcode="<end-user-raccoon-passcode>",
            advanced={
                "block_ads": True,
                "extension_ids": ["df2399ea-a938-438f-9d4b-ef3bc95cf8af"],
                "proxy": {
                    "city": "sanfrancisco",
                    "country": "us",
                    "state": "ca",
                    "zip": 94102,
                },
                "solve_captchas": True,
            },
            app_url="https://www.ycombinator.com/companies",
            chat_history=[{}],
            max_count=5,
            mode="deepsearch",
            schema={
                "address": {
                    "city": "What city is the company located in?",
                    "country": "Which country is the company located in?",
                },
                "funding_season": "The funding season like W24 as a string",
                "name": "Name of the company as a string",
            },
            stream=False,
        )
        assert_matches_type(LamRunResponse, lam, path=["response"])

    @parametrize
    def test_raw_response_run_overload_1(self, client: RaccoonAI) -> None:
        response = client.lam.with_raw_response.run(
            query="Find YCombinator startups who got funded in W24.",
            raccoon_passcode="<end-user-raccoon-passcode>",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        lam = response.parse()
        assert_matches_type(LamRunResponse, lam, path=["response"])

    @parametrize
    def test_streaming_response_run_overload_1(self, client: RaccoonAI) -> None:
        with client.lam.with_streaming_response.run(
            query="Find YCombinator startups who got funded in W24.",
            raccoon_passcode="<end-user-raccoon-passcode>",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            lam = response.parse()
            assert_matches_type(LamRunResponse, lam, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_run_overload_2(self, client: RaccoonAI) -> None:
        lam_stream = client.lam.run(
            query="Find YCombinator startups who got funded in W24.",
            raccoon_passcode="<end-user-raccoon-passcode>",
            stream=True,
        )
        lam_stream.response.close()

    @parametrize
    def test_method_run_with_all_params_overload_2(self, client: RaccoonAI) -> None:
        lam_stream = client.lam.run(
            query="Find YCombinator startups who got funded in W24.",
            raccoon_passcode="<end-user-raccoon-passcode>",
            stream=True,
            advanced={
                "block_ads": True,
                "extension_ids": ["df2399ea-a938-438f-9d4b-ef3bc95cf8af"],
                "proxy": {
                    "city": "sanfrancisco",
                    "country": "us",
                    "state": "ca",
                    "zip": 94102,
                },
                "solve_captchas": True,
            },
            app_url="https://www.ycombinator.com/companies",
            chat_history=[{}],
            max_count=5,
            mode="deepsearch",
            schema={
                "address": {
                    "city": "What city is the company located in?",
                    "country": "Which country is the company located in?",
                },
                "funding_season": "The funding season like W24 as a string",
                "name": "Name of the company as a string",
            },
        )
        lam_stream.response.close()

    @parametrize
    def test_raw_response_run_overload_2(self, client: RaccoonAI) -> None:
        response = client.lam.with_raw_response.run(
            query="Find YCombinator startups who got funded in W24.",
            raccoon_passcode="<end-user-raccoon-passcode>",
            stream=True,
        )

        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        stream = response.parse()
        stream.close()

    @parametrize
    def test_streaming_response_run_overload_2(self, client: RaccoonAI) -> None:
        with client.lam.with_streaming_response.run(
            query="Find YCombinator startups who got funded in W24.",
            raccoon_passcode="<end-user-raccoon-passcode>",
            stream=True,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            stream = response.parse()
            stream.close()

        assert cast(Any, response.is_closed) is True


class TestAsyncLam:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_run_overload_1(self, async_client: AsyncRaccoonAI) -> None:
        lam = await async_client.lam.run(
            query="Find YCombinator startups who got funded in W24.",
            raccoon_passcode="<end-user-raccoon-passcode>",
        )
        assert_matches_type(LamRunResponse, lam, path=["response"])

    @parametrize
    async def test_method_run_with_all_params_overload_1(self, async_client: AsyncRaccoonAI) -> None:
        lam = await async_client.lam.run(
            query="Find YCombinator startups who got funded in W24.",
            raccoon_passcode="<end-user-raccoon-passcode>",
            advanced={
                "block_ads": True,
                "extension_ids": ["df2399ea-a938-438f-9d4b-ef3bc95cf8af"],
                "proxy": {
                    "city": "sanfrancisco",
                    "country": "us",
                    "state": "ca",
                    "zip": 94102,
                },
                "solve_captchas": True,
            },
            app_url="https://www.ycombinator.com/companies",
            chat_history=[{}],
            max_count=5,
            mode="deepsearch",
            schema={
                "address": {
                    "city": "What city is the company located in?",
                    "country": "Which country is the company located in?",
                },
                "funding_season": "The funding season like W24 as a string",
                "name": "Name of the company as a string",
            },
            stream=False,
        )
        assert_matches_type(LamRunResponse, lam, path=["response"])

    @parametrize
    async def test_raw_response_run_overload_1(self, async_client: AsyncRaccoonAI) -> None:
        response = await async_client.lam.with_raw_response.run(
            query="Find YCombinator startups who got funded in W24.",
            raccoon_passcode="<end-user-raccoon-passcode>",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        lam = await response.parse()
        assert_matches_type(LamRunResponse, lam, path=["response"])

    @parametrize
    async def test_streaming_response_run_overload_1(self, async_client: AsyncRaccoonAI) -> None:
        async with async_client.lam.with_streaming_response.run(
            query="Find YCombinator startups who got funded in W24.",
            raccoon_passcode="<end-user-raccoon-passcode>",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            lam = await response.parse()
            assert_matches_type(LamRunResponse, lam, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_run_overload_2(self, async_client: AsyncRaccoonAI) -> None:
        lam_stream = await async_client.lam.run(
            query="Find YCombinator startups who got funded in W24.",
            raccoon_passcode="<end-user-raccoon-passcode>",
            stream=True,
        )
        await lam_stream.response.aclose()

    @parametrize
    async def test_method_run_with_all_params_overload_2(self, async_client: AsyncRaccoonAI) -> None:
        lam_stream = await async_client.lam.run(
            query="Find YCombinator startups who got funded in W24.",
            raccoon_passcode="<end-user-raccoon-passcode>",
            stream=True,
            advanced={
                "block_ads": True,
                "extension_ids": ["df2399ea-a938-438f-9d4b-ef3bc95cf8af"],
                "proxy": {
                    "city": "sanfrancisco",
                    "country": "us",
                    "state": "ca",
                    "zip": 94102,
                },
                "solve_captchas": True,
            },
            app_url="https://www.ycombinator.com/companies",
            chat_history=[{}],
            max_count=5,
            mode="deepsearch",
            schema={
                "address": {
                    "city": "What city is the company located in?",
                    "country": "Which country is the company located in?",
                },
                "funding_season": "The funding season like W24 as a string",
                "name": "Name of the company as a string",
            },
        )
        await lam_stream.response.aclose()

    @parametrize
    async def test_raw_response_run_overload_2(self, async_client: AsyncRaccoonAI) -> None:
        response = await async_client.lam.with_raw_response.run(
            query="Find YCombinator startups who got funded in W24.",
            raccoon_passcode="<end-user-raccoon-passcode>",
            stream=True,
        )

        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        stream = await response.parse()
        await stream.close()

    @parametrize
    async def test_streaming_response_run_overload_2(self, async_client: AsyncRaccoonAI) -> None:
        async with async_client.lam.with_streaming_response.run(
            query="Find YCombinator startups who got funded in W24.",
            raccoon_passcode="<end-user-raccoon-passcode>",
            stream=True,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            stream = await response.parse()
            await stream.close()

        assert cast(Any, response.is_closed) is True
