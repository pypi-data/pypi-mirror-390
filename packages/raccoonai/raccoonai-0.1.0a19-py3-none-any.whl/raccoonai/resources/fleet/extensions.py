# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Mapping, cast

import httpx

from ..._types import Body, Query, Headers, NotGiven, FileTypes, not_given
from ..._utils import extract_files, maybe_transform, deepcopy_minimal, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...types.fleet import extension_upload_params
from ..._base_client import make_request_options
from ...types.fleet.extension_all_response import ExtensionAllResponse
from ...types.fleet.extension_get_response import ExtensionGetResponse
from ...types.fleet.extension_upload_response import ExtensionUploadResponse

__all__ = ["ExtensionsResource", "AsyncExtensionsResource"]


class ExtensionsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ExtensionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/raccoonaihq/raccoonai-python#accessing-raw-response-data-eg-headers
        """
        return ExtensionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ExtensionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/raccoonaihq/raccoonai-python#with_streaming_response
        """
        return ExtensionsResourceWithStreamingResponse(self)

    def delete(
        self,
        extension_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Delete Extension Endpoint

        Args:
          extension_id: The ID of the extension to delete

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not extension_id:
            raise ValueError(f"Expected a non-empty value for `extension_id` but received {extension_id!r}")
        return self._delete(
            f"/extensions/{extension_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def all(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ExtensionAllResponse:
        """List Extensions Endpoint"""
        return self._get(
            "/extensions",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ExtensionAllResponse,
        )

    def get(
        self,
        extension_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ExtensionGetResponse:
        """
        Get Extension Endpoint

        Args:
          extension_id: The ID of the extension

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not extension_id:
            raise ValueError(f"Expected a non-empty value for `extension_id` but received {extension_id!r}")
        return self._get(
            f"/extensions/{extension_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ExtensionGetResponse,
        )

    def upload(
        self,
        *,
        file: FileTypes,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ExtensionUploadResponse:
        """
        Upload Extension Endpoint

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_minimal({"file": file})
        files = extract_files(cast(Mapping[str, object], body), paths=[["file"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return self._post(
            "/extensions",
            body=maybe_transform(body, extension_upload_params.ExtensionUploadParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ExtensionUploadResponse,
        )


class AsyncExtensionsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncExtensionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/raccoonaihq/raccoonai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncExtensionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncExtensionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/raccoonaihq/raccoonai-python#with_streaming_response
        """
        return AsyncExtensionsResourceWithStreamingResponse(self)

    async def delete(
        self,
        extension_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Delete Extension Endpoint

        Args:
          extension_id: The ID of the extension to delete

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not extension_id:
            raise ValueError(f"Expected a non-empty value for `extension_id` but received {extension_id!r}")
        return await self._delete(
            f"/extensions/{extension_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def all(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ExtensionAllResponse:
        """List Extensions Endpoint"""
        return await self._get(
            "/extensions",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ExtensionAllResponse,
        )

    async def get(
        self,
        extension_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ExtensionGetResponse:
        """
        Get Extension Endpoint

        Args:
          extension_id: The ID of the extension

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not extension_id:
            raise ValueError(f"Expected a non-empty value for `extension_id` but received {extension_id!r}")
        return await self._get(
            f"/extensions/{extension_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ExtensionGetResponse,
        )

    async def upload(
        self,
        *,
        file: FileTypes,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ExtensionUploadResponse:
        """
        Upload Extension Endpoint

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_minimal({"file": file})
        files = extract_files(cast(Mapping[str, object], body), paths=[["file"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return await self._post(
            "/extensions",
            body=await async_maybe_transform(body, extension_upload_params.ExtensionUploadParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ExtensionUploadResponse,
        )


class ExtensionsResourceWithRawResponse:
    def __init__(self, extensions: ExtensionsResource) -> None:
        self._extensions = extensions

        self.delete = to_raw_response_wrapper(
            extensions.delete,
        )
        self.all = to_raw_response_wrapper(
            extensions.all,
        )
        self.get = to_raw_response_wrapper(
            extensions.get,
        )
        self.upload = to_raw_response_wrapper(
            extensions.upload,
        )


class AsyncExtensionsResourceWithRawResponse:
    def __init__(self, extensions: AsyncExtensionsResource) -> None:
        self._extensions = extensions

        self.delete = async_to_raw_response_wrapper(
            extensions.delete,
        )
        self.all = async_to_raw_response_wrapper(
            extensions.all,
        )
        self.get = async_to_raw_response_wrapper(
            extensions.get,
        )
        self.upload = async_to_raw_response_wrapper(
            extensions.upload,
        )


class ExtensionsResourceWithStreamingResponse:
    def __init__(self, extensions: ExtensionsResource) -> None:
        self._extensions = extensions

        self.delete = to_streamed_response_wrapper(
            extensions.delete,
        )
        self.all = to_streamed_response_wrapper(
            extensions.all,
        )
        self.get = to_streamed_response_wrapper(
            extensions.get,
        )
        self.upload = to_streamed_response_wrapper(
            extensions.upload,
        )


class AsyncExtensionsResourceWithStreamingResponse:
    def __init__(self, extensions: AsyncExtensionsResource) -> None:
        self._extensions = extensions

        self.delete = async_to_streamed_response_wrapper(
            extensions.delete,
        )
        self.all = async_to_streamed_response_wrapper(
            extensions.all,
        )
        self.get = async_to_streamed_response_wrapper(
            extensions.get,
        )
        self.upload = async_to_streamed_response_wrapper(
            extensions.upload,
        )
