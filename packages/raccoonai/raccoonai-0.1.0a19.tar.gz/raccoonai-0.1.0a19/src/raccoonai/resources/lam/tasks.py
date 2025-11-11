# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Optional
from typing_extensions import Literal

import httpx

from ..._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...types.lam import task_all_params
from ..._base_client import make_request_options
from ...types.lam.task_all_response import TaskAllResponse
from ...types.lam.task_media_response import TaskMediaResponse

__all__ = ["TasksResource", "AsyncTasksResource"]


class TasksResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> TasksResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/raccoonaihq/raccoonai-python#accessing-raw-response-data-eg-headers
        """
        return TasksResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> TasksResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/raccoonaihq/raccoonai-python#with_streaming_response
        """
        return TasksResourceWithStreamingResponse(self)

    def all(
        self,
        *,
        end_time: Optional[int] | Omit = omit,
        execution_type: Optional[List[Literal["default", "deepsearch", "fleet"]]] | Omit = omit,
        limit: Optional[int] | Omit = omit,
        page: Optional[int] | Omit = omit,
        raccoon_passcode: Optional[str] | Omit = omit,
        sort_by: Optional[Literal["timestamp", "executionTime", "taskId", "status", "executionType"]] | Omit = omit,
        sort_order: Optional[Literal["ascend", "descend"]] | Omit = omit,
        start_time: Optional[int] | Omit = omit,
        task_id: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TaskAllResponse:
        """
        Get Tasks Endpoint

        Args:
          end_time: Filter tasks created before this Unix timestamp (in milliseconds).

          execution_type: Filter tasks by execution type (e.g., 'default', 'deepsearch').

          limit: Number of tasks per page (maximum 100).

          page: Page number for pagination.

          raccoon_passcode: Filter tasks by Raccoon passcode.

          sort_by: Field to sort tasks by (e.g., 'timestamp', 'executionTime').

          sort_order: Sort order ('ascend' or 'descend').

          start_time: Filter tasks created after this Unix timestamp (in milliseconds).

          task_id: Filter tasks by a specific task ID.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/lam/tasks",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "end_time": end_time,
                        "execution_type": execution_type,
                        "limit": limit,
                        "page": page,
                        "raccoon_passcode": raccoon_passcode,
                        "sort_by": sort_by,
                        "sort_order": sort_order,
                        "start_time": start_time,
                        "task_id": task_id,
                    },
                    task_all_params.TaskAllParams,
                ),
            ),
            cast_to=TaskAllResponse,
        )

    def media(
        self,
        task_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TaskMediaResponse:
        """
        Get Task Media Endpoint

        Args:
          task_id: The ID of the task

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not task_id:
            raise ValueError(f"Expected a non-empty value for `task_id` but received {task_id!r}")
        return self._get(
            f"/lam/tasks/{task_id}/media",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TaskMediaResponse,
        )


class AsyncTasksResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncTasksResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/raccoonaihq/raccoonai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncTasksResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncTasksResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/raccoonaihq/raccoonai-python#with_streaming_response
        """
        return AsyncTasksResourceWithStreamingResponse(self)

    async def all(
        self,
        *,
        end_time: Optional[int] | Omit = omit,
        execution_type: Optional[List[Literal["default", "deepsearch", "fleet"]]] | Omit = omit,
        limit: Optional[int] | Omit = omit,
        page: Optional[int] | Omit = omit,
        raccoon_passcode: Optional[str] | Omit = omit,
        sort_by: Optional[Literal["timestamp", "executionTime", "taskId", "status", "executionType"]] | Omit = omit,
        sort_order: Optional[Literal["ascend", "descend"]] | Omit = omit,
        start_time: Optional[int] | Omit = omit,
        task_id: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TaskAllResponse:
        """
        Get Tasks Endpoint

        Args:
          end_time: Filter tasks created before this Unix timestamp (in milliseconds).

          execution_type: Filter tasks by execution type (e.g., 'default', 'deepsearch').

          limit: Number of tasks per page (maximum 100).

          page: Page number for pagination.

          raccoon_passcode: Filter tasks by Raccoon passcode.

          sort_by: Field to sort tasks by (e.g., 'timestamp', 'executionTime').

          sort_order: Sort order ('ascend' or 'descend').

          start_time: Filter tasks created after this Unix timestamp (in milliseconds).

          task_id: Filter tasks by a specific task ID.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/lam/tasks",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "end_time": end_time,
                        "execution_type": execution_type,
                        "limit": limit,
                        "page": page,
                        "raccoon_passcode": raccoon_passcode,
                        "sort_by": sort_by,
                        "sort_order": sort_order,
                        "start_time": start_time,
                        "task_id": task_id,
                    },
                    task_all_params.TaskAllParams,
                ),
            ),
            cast_to=TaskAllResponse,
        )

    async def media(
        self,
        task_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TaskMediaResponse:
        """
        Get Task Media Endpoint

        Args:
          task_id: The ID of the task

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not task_id:
            raise ValueError(f"Expected a non-empty value for `task_id` but received {task_id!r}")
        return await self._get(
            f"/lam/tasks/{task_id}/media",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TaskMediaResponse,
        )


class TasksResourceWithRawResponse:
    def __init__(self, tasks: TasksResource) -> None:
        self._tasks = tasks

        self.all = to_raw_response_wrapper(
            tasks.all,
        )
        self.media = to_raw_response_wrapper(
            tasks.media,
        )


class AsyncTasksResourceWithRawResponse:
    def __init__(self, tasks: AsyncTasksResource) -> None:
        self._tasks = tasks

        self.all = async_to_raw_response_wrapper(
            tasks.all,
        )
        self.media = async_to_raw_response_wrapper(
            tasks.media,
        )


class TasksResourceWithStreamingResponse:
    def __init__(self, tasks: TasksResource) -> None:
        self._tasks = tasks

        self.all = to_streamed_response_wrapper(
            tasks.all,
        )
        self.media = to_streamed_response_wrapper(
            tasks.media,
        )


class AsyncTasksResourceWithStreamingResponse:
    def __init__(self, tasks: AsyncTasksResource) -> None:
        self._tasks = tasks

        self.all = async_to_streamed_response_wrapper(
            tasks.all,
        )
        self.media = async_to_streamed_response_wrapper(
            tasks.media,
        )
