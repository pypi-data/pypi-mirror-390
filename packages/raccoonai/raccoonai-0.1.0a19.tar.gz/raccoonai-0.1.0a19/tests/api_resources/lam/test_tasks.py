# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from raccoonai import RaccoonAI, AsyncRaccoonAI
from tests.utils import assert_matches_type
from raccoonai.types.lam import TaskAllResponse, TaskMediaResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestTasks:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_all(self, client: RaccoonAI) -> None:
        task = client.lam.tasks.all()
        assert_matches_type(TaskAllResponse, task, path=["response"])

    @parametrize
    def test_method_all_with_all_params(self, client: RaccoonAI) -> None:
        task = client.lam.tasks.all(
            end_time=1678972800000,
            execution_type=["default", "deepsearch"],
            limit=20,
            page=1,
            raccoon_passcode="code123",
            sort_by="timestamp",
            sort_order="ascend",
            start_time=1678886400000,
            task_id="task_123",
        )
        assert_matches_type(TaskAllResponse, task, path=["response"])

    @parametrize
    def test_raw_response_all(self, client: RaccoonAI) -> None:
        response = client.lam.tasks.with_raw_response.all()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = response.parse()
        assert_matches_type(TaskAllResponse, task, path=["response"])

    @parametrize
    def test_streaming_response_all(self, client: RaccoonAI) -> None:
        with client.lam.tasks.with_streaming_response.all() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = response.parse()
            assert_matches_type(TaskAllResponse, task, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_media(self, client: RaccoonAI) -> None:
        task = client.lam.tasks.media(
            "taskId",
        )
        assert_matches_type(TaskMediaResponse, task, path=["response"])

    @parametrize
    def test_raw_response_media(self, client: RaccoonAI) -> None:
        response = client.lam.tasks.with_raw_response.media(
            "taskId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = response.parse()
        assert_matches_type(TaskMediaResponse, task, path=["response"])

    @parametrize
    def test_streaming_response_media(self, client: RaccoonAI) -> None:
        with client.lam.tasks.with_streaming_response.media(
            "taskId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = response.parse()
            assert_matches_type(TaskMediaResponse, task, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_media(self, client: RaccoonAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `task_id` but received ''"):
            client.lam.tasks.with_raw_response.media(
                "",
            )


class TestAsyncTasks:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_all(self, async_client: AsyncRaccoonAI) -> None:
        task = await async_client.lam.tasks.all()
        assert_matches_type(TaskAllResponse, task, path=["response"])

    @parametrize
    async def test_method_all_with_all_params(self, async_client: AsyncRaccoonAI) -> None:
        task = await async_client.lam.tasks.all(
            end_time=1678972800000,
            execution_type=["default", "deepsearch"],
            limit=20,
            page=1,
            raccoon_passcode="code123",
            sort_by="timestamp",
            sort_order="ascend",
            start_time=1678886400000,
            task_id="task_123",
        )
        assert_matches_type(TaskAllResponse, task, path=["response"])

    @parametrize
    async def test_raw_response_all(self, async_client: AsyncRaccoonAI) -> None:
        response = await async_client.lam.tasks.with_raw_response.all()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = await response.parse()
        assert_matches_type(TaskAllResponse, task, path=["response"])

    @parametrize
    async def test_streaming_response_all(self, async_client: AsyncRaccoonAI) -> None:
        async with async_client.lam.tasks.with_streaming_response.all() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = await response.parse()
            assert_matches_type(TaskAllResponse, task, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_media(self, async_client: AsyncRaccoonAI) -> None:
        task = await async_client.lam.tasks.media(
            "taskId",
        )
        assert_matches_type(TaskMediaResponse, task, path=["response"])

    @parametrize
    async def test_raw_response_media(self, async_client: AsyncRaccoonAI) -> None:
        response = await async_client.lam.tasks.with_raw_response.media(
            "taskId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = await response.parse()
        assert_matches_type(TaskMediaResponse, task, path=["response"])

    @parametrize
    async def test_streaming_response_media(self, async_client: AsyncRaccoonAI) -> None:
        async with async_client.lam.tasks.with_streaming_response.media(
            "taskId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = await response.parse()
            assert_matches_type(TaskMediaResponse, task, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_media(self, async_client: AsyncRaccoonAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `task_id` but received ''"):
            await async_client.lam.tasks.with_raw_response.media(
                "",
            )
