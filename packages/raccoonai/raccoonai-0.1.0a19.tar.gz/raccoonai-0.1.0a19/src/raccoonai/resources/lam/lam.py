# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable, Optional
from typing_extensions import Literal, overload

import httpx

from .tasks import (
    TasksResource,
    AsyncTasksResource,
    TasksResourceWithRawResponse,
    AsyncTasksResourceWithRawResponse,
    TasksResourceWithStreamingResponse,
    AsyncTasksResourceWithStreamingResponse,
)
from ...types import lam_run_params
from ..._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ..._utils import required_args, maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._streaming import Stream, AsyncStream
from ..._base_client import make_request_options
from ...types.lam_run_response import LamRunResponse

__all__ = ["LamResource", "AsyncLamResource"]


class LamResource(SyncAPIResource):
    @cached_property
    def tasks(self) -> TasksResource:
        return TasksResource(self._client)

    @cached_property
    def with_raw_response(self) -> LamResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/raccoonaihq/raccoonai-python#accessing-raw-response-data-eg-headers
        """
        return LamResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> LamResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/raccoonaihq/raccoonai-python#with_streaming_response
        """
        return LamResourceWithStreamingResponse(self)

    @overload
    def run(
        self,
        *,
        query: str,
        raccoon_passcode: str,
        advanced: Optional[lam_run_params.Advanced] | Omit = omit,
        app_url: Optional[str] | Omit = omit,
        chat_history: Optional[Iterable[object]] | Omit = omit,
        max_count: Optional[int] | Omit = omit,
        mode: Optional[Literal["deepsearch", "default"]] | Omit = omit,
        schema: object | Omit = omit,
        stream: Optional[Literal[False]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> LamRunResponse:
        """Lam Run Endpoint

        Args:
          query: The input query string for the request.

        This is typically the main prompt.

          raccoon_passcode: The raccoon passcode associated with the end user on behalf of which the call is
              being made.

          advanced: Advanced configuration options for the session, such as ad-blocking and CAPTCHA
              solving.

          app_url: This is the entrypoint URL for the web agent.

          chat_history: The history of the conversation as a list of messages or objects you might use
              while building a chat app to give the model context of the past conversation.

          max_count: The maximum number of results to extract.

          mode: Mode of execution.

          schema: The expected schema for the response. This is a dictionary where the keys
              describe the fields and the values describe their purposes.

          stream: Whether the response should be streamed back or not.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def run(
        self,
        *,
        query: str,
        raccoon_passcode: str,
        stream: Literal[True],
        advanced: Optional[lam_run_params.Advanced] | Omit = omit,
        app_url: Optional[str] | Omit = omit,
        chat_history: Optional[Iterable[object]] | Omit = omit,
        max_count: Optional[int] | Omit = omit,
        mode: Optional[Literal["deepsearch", "default"]] | Omit = omit,
        schema: object | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Stream[LamRunResponse]:
        """Lam Run Endpoint

        Args:
          query: The input query string for the request.

        This is typically the main prompt.

          raccoon_passcode: The raccoon passcode associated with the end user on behalf of which the call is
              being made.

          stream: Whether the response should be streamed back or not.

          advanced: Advanced configuration options for the session, such as ad-blocking and CAPTCHA
              solving.

          app_url: This is the entrypoint URL for the web agent.

          chat_history: The history of the conversation as a list of messages or objects you might use
              while building a chat app to give the model context of the past conversation.

          max_count: The maximum number of results to extract.

          mode: Mode of execution.

          schema: The expected schema for the response. This is a dictionary where the keys
              describe the fields and the values describe their purposes.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def run(
        self,
        *,
        query: str,
        raccoon_passcode: str,
        stream: bool,
        advanced: Optional[lam_run_params.Advanced] | Omit = omit,
        app_url: Optional[str] | Omit = omit,
        chat_history: Optional[Iterable[object]] | Omit = omit,
        max_count: Optional[int] | Omit = omit,
        mode: Optional[Literal["deepsearch", "default"]] | Omit = omit,
        schema: object | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> LamRunResponse | Stream[LamRunResponse]:
        """Lam Run Endpoint

        Args:
          query: The input query string for the request.

        This is typically the main prompt.

          raccoon_passcode: The raccoon passcode associated with the end user on behalf of which the call is
              being made.

          stream: Whether the response should be streamed back or not.

          advanced: Advanced configuration options for the session, such as ad-blocking and CAPTCHA
              solving.

          app_url: This is the entrypoint URL for the web agent.

          chat_history: The history of the conversation as a list of messages or objects you might use
              while building a chat app to give the model context of the past conversation.

          max_count: The maximum number of results to extract.

          mode: Mode of execution.

          schema: The expected schema for the response. This is a dictionary where the keys
              describe the fields and the values describe their purposes.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["query", "raccoon_passcode"], ["query", "raccoon_passcode", "stream"])
    def run(
        self,
        *,
        query: str,
        raccoon_passcode: str,
        advanced: Optional[lam_run_params.Advanced] | Omit = omit,
        app_url: Optional[str] | Omit = omit,
        chat_history: Optional[Iterable[object]] | Omit = omit,
        max_count: Optional[int] | Omit = omit,
        mode: Optional[Literal["deepsearch", "default"]] | Omit = omit,
        schema: object | Omit = omit,
        stream: Optional[Literal[False]] | Literal[True] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> LamRunResponse | Stream[LamRunResponse]:
        return self._post(
            "/lam/run",
            body=maybe_transform(
                {
                    "query": query,
                    "raccoon_passcode": raccoon_passcode,
                    "advanced": advanced,
                    "app_url": app_url,
                    "chat_history": chat_history,
                    "max_count": max_count,
                    "mode": mode,
                    "schema": schema,
                    "stream": stream,
                },
                lam_run_params.LamRunParamsStreaming if stream else lam_run_params.LamRunParamsNonStreaming,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LamRunResponse,
            stream=stream or False,
            stream_cls=Stream[LamRunResponse],
        )


class AsyncLamResource(AsyncAPIResource):
    @cached_property
    def tasks(self) -> AsyncTasksResource:
        return AsyncTasksResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncLamResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/raccoonaihq/raccoonai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncLamResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncLamResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/raccoonaihq/raccoonai-python#with_streaming_response
        """
        return AsyncLamResourceWithStreamingResponse(self)

    @overload
    async def run(
        self,
        *,
        query: str,
        raccoon_passcode: str,
        advanced: Optional[lam_run_params.Advanced] | Omit = omit,
        app_url: Optional[str] | Omit = omit,
        chat_history: Optional[Iterable[object]] | Omit = omit,
        max_count: Optional[int] | Omit = omit,
        mode: Optional[Literal["deepsearch", "default"]] | Omit = omit,
        schema: object | Omit = omit,
        stream: Optional[Literal[False]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> LamRunResponse:
        """Lam Run Endpoint

        Args:
          query: The input query string for the request.

        This is typically the main prompt.

          raccoon_passcode: The raccoon passcode associated with the end user on behalf of which the call is
              being made.

          advanced: Advanced configuration options for the session, such as ad-blocking and CAPTCHA
              solving.

          app_url: This is the entrypoint URL for the web agent.

          chat_history: The history of the conversation as a list of messages or objects you might use
              while building a chat app to give the model context of the past conversation.

          max_count: The maximum number of results to extract.

          mode: Mode of execution.

          schema: The expected schema for the response. This is a dictionary where the keys
              describe the fields and the values describe their purposes.

          stream: Whether the response should be streamed back or not.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def run(
        self,
        *,
        query: str,
        raccoon_passcode: str,
        stream: Literal[True],
        advanced: Optional[lam_run_params.Advanced] | Omit = omit,
        app_url: Optional[str] | Omit = omit,
        chat_history: Optional[Iterable[object]] | Omit = omit,
        max_count: Optional[int] | Omit = omit,
        mode: Optional[Literal["deepsearch", "default"]] | Omit = omit,
        schema: object | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncStream[LamRunResponse]:
        """Lam Run Endpoint

        Args:
          query: The input query string for the request.

        This is typically the main prompt.

          raccoon_passcode: The raccoon passcode associated with the end user on behalf of which the call is
              being made.

          stream: Whether the response should be streamed back or not.

          advanced: Advanced configuration options for the session, such as ad-blocking and CAPTCHA
              solving.

          app_url: This is the entrypoint URL for the web agent.

          chat_history: The history of the conversation as a list of messages or objects you might use
              while building a chat app to give the model context of the past conversation.

          max_count: The maximum number of results to extract.

          mode: Mode of execution.

          schema: The expected schema for the response. This is a dictionary where the keys
              describe the fields and the values describe their purposes.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def run(
        self,
        *,
        query: str,
        raccoon_passcode: str,
        stream: bool,
        advanced: Optional[lam_run_params.Advanced] | Omit = omit,
        app_url: Optional[str] | Omit = omit,
        chat_history: Optional[Iterable[object]] | Omit = omit,
        max_count: Optional[int] | Omit = omit,
        mode: Optional[Literal["deepsearch", "default"]] | Omit = omit,
        schema: object | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> LamRunResponse | AsyncStream[LamRunResponse]:
        """Lam Run Endpoint

        Args:
          query: The input query string for the request.

        This is typically the main prompt.

          raccoon_passcode: The raccoon passcode associated with the end user on behalf of which the call is
              being made.

          stream: Whether the response should be streamed back or not.

          advanced: Advanced configuration options for the session, such as ad-blocking and CAPTCHA
              solving.

          app_url: This is the entrypoint URL for the web agent.

          chat_history: The history of the conversation as a list of messages or objects you might use
              while building a chat app to give the model context of the past conversation.

          max_count: The maximum number of results to extract.

          mode: Mode of execution.

          schema: The expected schema for the response. This is a dictionary where the keys
              describe the fields and the values describe their purposes.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["query", "raccoon_passcode"], ["query", "raccoon_passcode", "stream"])
    async def run(
        self,
        *,
        query: str,
        raccoon_passcode: str,
        advanced: Optional[lam_run_params.Advanced] | Omit = omit,
        app_url: Optional[str] | Omit = omit,
        chat_history: Optional[Iterable[object]] | Omit = omit,
        max_count: Optional[int] | Omit = omit,
        mode: Optional[Literal["deepsearch", "default"]] | Omit = omit,
        schema: object | Omit = omit,
        stream: Optional[Literal[False]] | Literal[True] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> LamRunResponse | AsyncStream[LamRunResponse]:
        return await self._post(
            "/lam/run",
            body=await async_maybe_transform(
                {
                    "query": query,
                    "raccoon_passcode": raccoon_passcode,
                    "advanced": advanced,
                    "app_url": app_url,
                    "chat_history": chat_history,
                    "max_count": max_count,
                    "mode": mode,
                    "schema": schema,
                    "stream": stream,
                },
                lam_run_params.LamRunParamsStreaming if stream else lam_run_params.LamRunParamsNonStreaming,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LamRunResponse,
            stream=stream or False,
            stream_cls=AsyncStream[LamRunResponse],
        )


class LamResourceWithRawResponse:
    def __init__(self, lam: LamResource) -> None:
        self._lam = lam

        self.run = to_raw_response_wrapper(
            lam.run,
        )

    @cached_property
    def tasks(self) -> TasksResourceWithRawResponse:
        return TasksResourceWithRawResponse(self._lam.tasks)


class AsyncLamResourceWithRawResponse:
    def __init__(self, lam: AsyncLamResource) -> None:
        self._lam = lam

        self.run = async_to_raw_response_wrapper(
            lam.run,
        )

    @cached_property
    def tasks(self) -> AsyncTasksResourceWithRawResponse:
        return AsyncTasksResourceWithRawResponse(self._lam.tasks)


class LamResourceWithStreamingResponse:
    def __init__(self, lam: LamResource) -> None:
        self._lam = lam

        self.run = to_streamed_response_wrapper(
            lam.run,
        )

    @cached_property
    def tasks(self) -> TasksResourceWithStreamingResponse:
        return TasksResourceWithStreamingResponse(self._lam.tasks)


class AsyncLamResourceWithStreamingResponse:
    def __init__(self, lam: AsyncLamResource) -> None:
        self._lam = lam

        self.run = async_to_streamed_response_wrapper(
            lam.run,
        )

    @cached_property
    def tasks(self) -> AsyncTasksResourceWithStreamingResponse:
        return AsyncTasksResourceWithStreamingResponse(self._lam.tasks)
