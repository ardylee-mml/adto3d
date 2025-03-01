# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options

__all__ = ["ConnectionTestResource", "AsyncConnectionTestResource"]


class ConnectionTestResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ConnectionTestResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/masterpiecevr/mpx-sdk-python#accessing-raw-response-data-eg-headers
        """
        return ConnectionTestResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ConnectionTestResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/masterpiecevr/mpx-sdk-python#with_streaming_response
        """
        return ConnectionTestResourceWithStreamingResponse(self)

    def retrieve(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> str:
        """
        Use this endpoint to test your connection to our servers and ensure that the API
        Key for your application is valid. If everything works correctly, you will get a
        happy text response!
        """
        extra_headers = {"Accept": "text/plain", **(extra_headers or {})}
        return self._get(
            "/connection/test",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=str,
        )


class AsyncConnectionTestResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncConnectionTestResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/masterpiecevr/mpx-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncConnectionTestResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncConnectionTestResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/masterpiecevr/mpx-sdk-python#with_streaming_response
        """
        return AsyncConnectionTestResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> str:
        """
        Use this endpoint to test your connection to our servers and ensure that the API
        Key for your application is valid. If everything works correctly, you will get a
        happy text response!
        """
        extra_headers = {"Accept": "text/plain", **(extra_headers or {})}
        return await self._get(
            "/connection/test",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=str,
        )


class ConnectionTestResourceWithRawResponse:
    def __init__(self, connection_test: ConnectionTestResource) -> None:
        self._connection_test = connection_test

        self.retrieve = to_raw_response_wrapper(
            connection_test.retrieve,
        )


class AsyncConnectionTestResourceWithRawResponse:
    def __init__(self, connection_test: AsyncConnectionTestResource) -> None:
        self._connection_test = connection_test

        self.retrieve = async_to_raw_response_wrapper(
            connection_test.retrieve,
        )


class ConnectionTestResourceWithStreamingResponse:
    def __init__(self, connection_test: ConnectionTestResource) -> None:
        self._connection_test = connection_test

        self.retrieve = to_streamed_response_wrapper(
            connection_test.retrieve,
        )


class AsyncConnectionTestResourceWithStreamingResponse:
    def __init__(self, connection_test: AsyncConnectionTestResource) -> None:
        self._connection_test = connection_test

        self.retrieve = async_to_streamed_response_wrapper(
            connection_test.retrieve,
        )
