# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from .sessions import (
    SessionsResource,
    AsyncSessionsResource,
    SessionsResourceWithRawResponse,
    AsyncSessionsResourceWithRawResponse,
    SessionsResourceWithStreamingResponse,
    AsyncSessionsResourceWithStreamingResponse,
)
from ..._compat import cached_property
from .extensions import (
    ExtensionsResource,
    AsyncExtensionsResource,
    ExtensionsResourceWithRawResponse,
    AsyncExtensionsResourceWithRawResponse,
    ExtensionsResourceWithStreamingResponse,
    AsyncExtensionsResourceWithStreamingResponse,
)
from ..._resource import SyncAPIResource, AsyncAPIResource

__all__ = ["FleetResource", "AsyncFleetResource"]


class FleetResource(SyncAPIResource):
    @cached_property
    def sessions(self) -> SessionsResource:
        return SessionsResource(self._client)

    @cached_property
    def extensions(self) -> ExtensionsResource:
        return ExtensionsResource(self._client)

    @cached_property
    def with_raw_response(self) -> FleetResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/raccoonaihq/raccoonai-python#accessing-raw-response-data-eg-headers
        """
        return FleetResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> FleetResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/raccoonaihq/raccoonai-python#with_streaming_response
        """
        return FleetResourceWithStreamingResponse(self)


class AsyncFleetResource(AsyncAPIResource):
    @cached_property
    def sessions(self) -> AsyncSessionsResource:
        return AsyncSessionsResource(self._client)

    @cached_property
    def extensions(self) -> AsyncExtensionsResource:
        return AsyncExtensionsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncFleetResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/raccoonaihq/raccoonai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncFleetResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncFleetResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/raccoonaihq/raccoonai-python#with_streaming_response
        """
        return AsyncFleetResourceWithStreamingResponse(self)


class FleetResourceWithRawResponse:
    def __init__(self, fleet: FleetResource) -> None:
        self._fleet = fleet

    @cached_property
    def sessions(self) -> SessionsResourceWithRawResponse:
        return SessionsResourceWithRawResponse(self._fleet.sessions)

    @cached_property
    def extensions(self) -> ExtensionsResourceWithRawResponse:
        return ExtensionsResourceWithRawResponse(self._fleet.extensions)


class AsyncFleetResourceWithRawResponse:
    def __init__(self, fleet: AsyncFleetResource) -> None:
        self._fleet = fleet

    @cached_property
    def sessions(self) -> AsyncSessionsResourceWithRawResponse:
        return AsyncSessionsResourceWithRawResponse(self._fleet.sessions)

    @cached_property
    def extensions(self) -> AsyncExtensionsResourceWithRawResponse:
        return AsyncExtensionsResourceWithRawResponse(self._fleet.extensions)


class FleetResourceWithStreamingResponse:
    def __init__(self, fleet: FleetResource) -> None:
        self._fleet = fleet

    @cached_property
    def sessions(self) -> SessionsResourceWithStreamingResponse:
        return SessionsResourceWithStreamingResponse(self._fleet.sessions)

    @cached_property
    def extensions(self) -> ExtensionsResourceWithStreamingResponse:
        return ExtensionsResourceWithStreamingResponse(self._fleet.extensions)


class AsyncFleetResourceWithStreamingResponse:
    def __init__(self, fleet: AsyncFleetResource) -> None:
        self._fleet = fleet

    @cached_property
    def sessions(self) -> AsyncSessionsResourceWithStreamingResponse:
        return AsyncSessionsResourceWithStreamingResponse(self._fleet.sessions)

    @cached_property
    def extensions(self) -> AsyncExtensionsResourceWithStreamingResponse:
        return AsyncExtensionsResourceWithStreamingResponse(self._fleet.extensions)
