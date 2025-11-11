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
from ...types.fleet import session_all_params, session_create_params
from ..._base_client import make_request_options
from ...types.fleet.session_all_response import SessionAllResponse
from ...types.fleet.session_logs_response import SessionLogsResponse
from ...types.fleet.session_media_response import SessionMediaResponse
from ...types.fleet.session_create_response import SessionCreateResponse
from ...types.fleet.session_status_response import SessionStatusResponse
from ...types.fleet.session_terminate_response import SessionTerminateResponse

__all__ = ["SessionsResource", "AsyncSessionsResource"]


class SessionsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> SessionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/raccoonaihq/raccoonai-python#accessing-raw-response-data-eg-headers
        """
        return SessionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> SessionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/raccoonaihq/raccoonai-python#with_streaming_response
        """
        return SessionsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        advanced: Optional[session_create_params.Advanced] | Omit = omit,
        browser_type: Optional[Literal["chromium", "firefox", "webkit"]] | Omit = omit,
        headless: Optional[bool] | Omit = omit,
        raccoon_passcode: Optional[str] | Omit = omit,
        session_timeout: Optional[int] | Omit = omit,
        settings: Optional[session_create_params.Settings] | Omit = omit,
        url: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionCreateResponse:
        """
        Fleet Websocket Session Create Endpoint

        Args:
          advanced: Advanced configuration options for the session, such as ad-blocking and CAPTCHA
              solving.

          browser_type: The type of browser to use. Supported values include 'chromium', 'firefox', and
              'webkit'.

          headless: Whether to run the browser in headless mode.

          raccoon_passcode: The raccoon passcode associated with the end user on behalf of which the call is
              being made if any.

          session_timeout: The timeout for the browser session in seconds.

          settings: Configuration settings for the browser, such as viewport size and User-Agent
              string.

          url: The entrypoint url for the session.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/sessions/create",
            body=maybe_transform(
                {
                    "advanced": advanced,
                    "browser_type": browser_type,
                    "headless": headless,
                    "raccoon_passcode": raccoon_passcode,
                    "session_timeout": session_timeout,
                    "settings": settings,
                    "url": url,
                },
                session_create_params.SessionCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SessionCreateResponse,
        )

    def all(
        self,
        *,
        end_time: Optional[int] | Omit = omit,
        execution_type: Optional[List[Literal["default", "deepsearch", "fleet"]]] | Omit = omit,
        limit: Optional[int] | Omit = omit,
        page: Optional[int] | Omit = omit,
        raccoon_passcode: Optional[str] | Omit = omit,
        session_id: Optional[str] | Omit = omit,
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
    ) -> SessionAllResponse:
        """
        Get Sessions Endpoint

        Args:
          end_time: Filter sessions created before this Unix timestamp (in milliseconds).

          execution_type: Filter sessions by execution type (e.g., 'default', 'deepsearch').

          limit: Number of sessions per page (maximum 100).

          page: Page number for pagination.

          raccoon_passcode: Filter sessions by Raccoon passcode.

          session_id: Filter sessions by a specific session ID.

          sort_by: Field to sort sessions by (e.g., 'timestamp', 'executionTime').

          sort_order: Sort order ('ascend' or 'descend').

          start_time: Filter sessions created after this Unix timestamp (in milliseconds).

          task_id: Filter sessions by a specific task ID.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/sessions",
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
                        "session_id": session_id,
                        "sort_by": sort_by,
                        "sort_order": sort_order,
                        "start_time": start_time,
                        "task_id": task_id,
                    },
                    session_all_params.SessionAllParams,
                ),
            ),
            cast_to=SessionAllResponse,
        )

    def logs(
        self,
        session_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionLogsResponse:
        """
        Fleet Session Logs Endpoint

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        return self._get(
            f"/sessions/{session_id}/logs",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SessionLogsResponse,
        )

    def media(
        self,
        session_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionMediaResponse:
        """
        Get Session Media Endpoint

        Args:
          session_id: The ID of the session

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        return self._get(
            f"/sessions/{session_id}/media",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SessionMediaResponse,
        )

    def status(
        self,
        session_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionStatusResponse:
        """
        Fleet Session Status Endpoint

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        return self._get(
            f"/sessions/{session_id}/status",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SessionStatusResponse,
        )

    def terminate(
        self,
        session_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionTerminateResponse:
        """
        Fleet Session Terminate Endpoint

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        return self._delete(
            f"/sessions/{session_id}/terminate",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SessionTerminateResponse,
        )


class AsyncSessionsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncSessionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/raccoonaihq/raccoonai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncSessionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncSessionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/raccoonaihq/raccoonai-python#with_streaming_response
        """
        return AsyncSessionsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        advanced: Optional[session_create_params.Advanced] | Omit = omit,
        browser_type: Optional[Literal["chromium", "firefox", "webkit"]] | Omit = omit,
        headless: Optional[bool] | Omit = omit,
        raccoon_passcode: Optional[str] | Omit = omit,
        session_timeout: Optional[int] | Omit = omit,
        settings: Optional[session_create_params.Settings] | Omit = omit,
        url: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionCreateResponse:
        """
        Fleet Websocket Session Create Endpoint

        Args:
          advanced: Advanced configuration options for the session, such as ad-blocking and CAPTCHA
              solving.

          browser_type: The type of browser to use. Supported values include 'chromium', 'firefox', and
              'webkit'.

          headless: Whether to run the browser in headless mode.

          raccoon_passcode: The raccoon passcode associated with the end user on behalf of which the call is
              being made if any.

          session_timeout: The timeout for the browser session in seconds.

          settings: Configuration settings for the browser, such as viewport size and User-Agent
              string.

          url: The entrypoint url for the session.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/sessions/create",
            body=await async_maybe_transform(
                {
                    "advanced": advanced,
                    "browser_type": browser_type,
                    "headless": headless,
                    "raccoon_passcode": raccoon_passcode,
                    "session_timeout": session_timeout,
                    "settings": settings,
                    "url": url,
                },
                session_create_params.SessionCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SessionCreateResponse,
        )

    async def all(
        self,
        *,
        end_time: Optional[int] | Omit = omit,
        execution_type: Optional[List[Literal["default", "deepsearch", "fleet"]]] | Omit = omit,
        limit: Optional[int] | Omit = omit,
        page: Optional[int] | Omit = omit,
        raccoon_passcode: Optional[str] | Omit = omit,
        session_id: Optional[str] | Omit = omit,
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
    ) -> SessionAllResponse:
        """
        Get Sessions Endpoint

        Args:
          end_time: Filter sessions created before this Unix timestamp (in milliseconds).

          execution_type: Filter sessions by execution type (e.g., 'default', 'deepsearch').

          limit: Number of sessions per page (maximum 100).

          page: Page number for pagination.

          raccoon_passcode: Filter sessions by Raccoon passcode.

          session_id: Filter sessions by a specific session ID.

          sort_by: Field to sort sessions by (e.g., 'timestamp', 'executionTime').

          sort_order: Sort order ('ascend' or 'descend').

          start_time: Filter sessions created after this Unix timestamp (in milliseconds).

          task_id: Filter sessions by a specific task ID.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/sessions",
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
                        "session_id": session_id,
                        "sort_by": sort_by,
                        "sort_order": sort_order,
                        "start_time": start_time,
                        "task_id": task_id,
                    },
                    session_all_params.SessionAllParams,
                ),
            ),
            cast_to=SessionAllResponse,
        )

    async def logs(
        self,
        session_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionLogsResponse:
        """
        Fleet Session Logs Endpoint

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        return await self._get(
            f"/sessions/{session_id}/logs",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SessionLogsResponse,
        )

    async def media(
        self,
        session_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionMediaResponse:
        """
        Get Session Media Endpoint

        Args:
          session_id: The ID of the session

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        return await self._get(
            f"/sessions/{session_id}/media",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SessionMediaResponse,
        )

    async def status(
        self,
        session_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionStatusResponse:
        """
        Fleet Session Status Endpoint

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        return await self._get(
            f"/sessions/{session_id}/status",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SessionStatusResponse,
        )

    async def terminate(
        self,
        session_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionTerminateResponse:
        """
        Fleet Session Terminate Endpoint

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        return await self._delete(
            f"/sessions/{session_id}/terminate",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SessionTerminateResponse,
        )


class SessionsResourceWithRawResponse:
    def __init__(self, sessions: SessionsResource) -> None:
        self._sessions = sessions

        self.create = to_raw_response_wrapper(
            sessions.create,
        )
        self.all = to_raw_response_wrapper(
            sessions.all,
        )
        self.logs = to_raw_response_wrapper(
            sessions.logs,
        )
        self.media = to_raw_response_wrapper(
            sessions.media,
        )
        self.status = to_raw_response_wrapper(
            sessions.status,
        )
        self.terminate = to_raw_response_wrapper(
            sessions.terminate,
        )


class AsyncSessionsResourceWithRawResponse:
    def __init__(self, sessions: AsyncSessionsResource) -> None:
        self._sessions = sessions

        self.create = async_to_raw_response_wrapper(
            sessions.create,
        )
        self.all = async_to_raw_response_wrapper(
            sessions.all,
        )
        self.logs = async_to_raw_response_wrapper(
            sessions.logs,
        )
        self.media = async_to_raw_response_wrapper(
            sessions.media,
        )
        self.status = async_to_raw_response_wrapper(
            sessions.status,
        )
        self.terminate = async_to_raw_response_wrapper(
            sessions.terminate,
        )


class SessionsResourceWithStreamingResponse:
    def __init__(self, sessions: SessionsResource) -> None:
        self._sessions = sessions

        self.create = to_streamed_response_wrapper(
            sessions.create,
        )
        self.all = to_streamed_response_wrapper(
            sessions.all,
        )
        self.logs = to_streamed_response_wrapper(
            sessions.logs,
        )
        self.media = to_streamed_response_wrapper(
            sessions.media,
        )
        self.status = to_streamed_response_wrapper(
            sessions.status,
        )
        self.terminate = to_streamed_response_wrapper(
            sessions.terminate,
        )


class AsyncSessionsResourceWithStreamingResponse:
    def __init__(self, sessions: AsyncSessionsResource) -> None:
        self._sessions = sessions

        self.create = async_to_streamed_response_wrapper(
            sessions.create,
        )
        self.all = async_to_streamed_response_wrapper(
            sessions.all,
        )
        self.logs = async_to_streamed_response_wrapper(
            sessions.logs,
        )
        self.media = async_to_streamed_response_wrapper(
            sessions.media,
        )
        self.status = async_to_streamed_response_wrapper(
            sessions.status,
        )
        self.terminate = async_to_streamed_response_wrapper(
            sessions.terminate,
        )
