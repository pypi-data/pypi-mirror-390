# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
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
from ...types.tail import user_all_params, user_create_params, user_status_params
from ..._base_client import make_request_options
from ...types.tail.user_all_response import UserAllResponse
from ...types.tail.user_create_response import UserCreateResponse
from ...types.tail.user_status_response import UserStatusResponse

__all__ = ["UsersResource", "AsyncUsersResource"]


class UsersResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> UsersResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/raccoonaihq/raccoonai-python#accessing-raw-response-data-eg-headers
        """
        return UsersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> UsersResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/raccoonaihq/raccoonai-python#with_streaming_response
        """
        return UsersResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        email: str,
        name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> UserCreateResponse:
        """
        Create User Endpoint

        Args:
          email: specify email of user.

          name: specify name of user.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/tail/users/create",
            body=maybe_transform(
                {
                    "email": email,
                    "name": name,
                },
                user_create_params.UserCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UserCreateResponse,
        )

    def all(
        self,
        *,
        email_id: Optional[str] | Omit = omit,
        limit: Optional[int] | Omit = omit,
        page: Optional[int] | Omit = omit,
        raccoon_passcode: Optional[str] | Omit = omit,
        search_query: Optional[str] | Omit = omit,
        sort_by: Optional[Literal["createdAt", "name", "email", "raccoonPasscode"]] | Omit = omit,
        sort_order: Optional[Literal["ascend", "descend"]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> UserAllResponse:
        """
        Get Users Endpoint

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/tail/users",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "email_id": email_id,
                        "limit": limit,
                        "page": page,
                        "raccoon_passcode": raccoon_passcode,
                        "search_query": search_query,
                        "sort_by": sort_by,
                        "sort_order": sort_order,
                    },
                    user_all_params.UserAllParams,
                ),
            ),
            cast_to=UserAllResponse,
        )

    def status(
        self,
        *,
        app_name: str,
        raccoon_passcode: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> UserStatusResponse:
        """
        Get Auth Status Endpoint

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/tail/app/auth-status",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "app_name": app_name,
                        "raccoon_passcode": raccoon_passcode,
                    },
                    user_status_params.UserStatusParams,
                ),
            ),
            cast_to=UserStatusResponse,
        )


class AsyncUsersResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncUsersResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/raccoonaihq/raccoonai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncUsersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncUsersResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/raccoonaihq/raccoonai-python#with_streaming_response
        """
        return AsyncUsersResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        email: str,
        name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> UserCreateResponse:
        """
        Create User Endpoint

        Args:
          email: specify email of user.

          name: specify name of user.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/tail/users/create",
            body=await async_maybe_transform(
                {
                    "email": email,
                    "name": name,
                },
                user_create_params.UserCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UserCreateResponse,
        )

    async def all(
        self,
        *,
        email_id: Optional[str] | Omit = omit,
        limit: Optional[int] | Omit = omit,
        page: Optional[int] | Omit = omit,
        raccoon_passcode: Optional[str] | Omit = omit,
        search_query: Optional[str] | Omit = omit,
        sort_by: Optional[Literal["createdAt", "name", "email", "raccoonPasscode"]] | Omit = omit,
        sort_order: Optional[Literal["ascend", "descend"]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> UserAllResponse:
        """
        Get Users Endpoint

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/tail/users",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "email_id": email_id,
                        "limit": limit,
                        "page": page,
                        "raccoon_passcode": raccoon_passcode,
                        "search_query": search_query,
                        "sort_by": sort_by,
                        "sort_order": sort_order,
                    },
                    user_all_params.UserAllParams,
                ),
            ),
            cast_to=UserAllResponse,
        )

    async def status(
        self,
        *,
        app_name: str,
        raccoon_passcode: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> UserStatusResponse:
        """
        Get Auth Status Endpoint

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/tail/app/auth-status",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "app_name": app_name,
                        "raccoon_passcode": raccoon_passcode,
                    },
                    user_status_params.UserStatusParams,
                ),
            ),
            cast_to=UserStatusResponse,
        )


class UsersResourceWithRawResponse:
    def __init__(self, users: UsersResource) -> None:
        self._users = users

        self.create = to_raw_response_wrapper(
            users.create,
        )
        self.all = to_raw_response_wrapper(
            users.all,
        )
        self.status = to_raw_response_wrapper(
            users.status,
        )


class AsyncUsersResourceWithRawResponse:
    def __init__(self, users: AsyncUsersResource) -> None:
        self._users = users

        self.create = async_to_raw_response_wrapper(
            users.create,
        )
        self.all = async_to_raw_response_wrapper(
            users.all,
        )
        self.status = async_to_raw_response_wrapper(
            users.status,
        )


class UsersResourceWithStreamingResponse:
    def __init__(self, users: UsersResource) -> None:
        self._users = users

        self.create = to_streamed_response_wrapper(
            users.create,
        )
        self.all = to_streamed_response_wrapper(
            users.all,
        )
        self.status = to_streamed_response_wrapper(
            users.status,
        )


class AsyncUsersResourceWithStreamingResponse:
    def __init__(self, users: AsyncUsersResource) -> None:
        self._users = users

        self.create = async_to_streamed_response_wrapper(
            users.create,
        )
        self.all = async_to_streamed_response_wrapper(
            users.all,
        )
        self.status = async_to_streamed_response_wrapper(
            users.status,
        )
