# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import function_imageto3d_params, function_create_general_params
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import (
    maybe_transform,
    async_maybe_transform,
)
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.shared.generate_response_object import GenerateResponseObject

__all__ = ["FunctionsResource", "AsyncFunctionsResource"]


class FunctionsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> FunctionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/masterpiecevr/mpx-sdk-python#accessing-raw-response-data-eg-headers
        """
        return FunctionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> FunctionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/masterpiecevr/mpx-sdk-python#with_streaming_response
        """
        return FunctionsResourceWithStreamingResponse(self)

    def create_general(
        self,
        *,
        prompt: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GenerateResponseObject:
        """
        This function generates anything from just a single prompt! Once you make this
        function request, make note of the returned requestId. Then call the status
        endpoint to get the current status of the request. Currently, requests can take
        \\~~2-5mins to complete.

        Args:
          prompt: The prompt to use for the generation

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/functions/general",
            body=maybe_transform({"prompt": prompt}, function_create_general_params.FunctionCreateGeneralParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GenerateResponseObject,
        )

    def imageto3d(
        self,
        *,
        image_request_id: str | NotGiven = NOT_GIVEN,
        image_url: str | NotGiven = NOT_GIVEN,
        seed: float | NotGiven = NOT_GIVEN,
        texture_size: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GenerateResponseObject:
        """This function generates a 3D model (GLB, FBX, USDZ) from an image.

        You can
        upload your own image or provide a URL to an image. To upload your own image,
        first call the **assets/create** endpoint to create an assetId for the image,
        then upload the image to our servers using the returned URL. Once you make this
        function request, make note of the returned requestId. Then call the status
        endpoint to get the current status of the request. Currently, requests can take
        \\~~1-2mins to complete.

        Args:
          image_request_id: The requestId from the /assets/create endpoint that the image was uploaded to.
              Do not use this if you have an imageUrl.

          image_url: The URL of the image to use for the generation. Use this instead of
              imageRequestId if you did not upload the image to our servers using the
              /assets/create endpoint.

          seed: Seed used to generate the 3D model

          texture_size: Size of the texture to use for the model. Higher values will result in more
              detailed models but will take longer to process. Must be one of 256, 512, 1024,
              2048

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/functions/imageto3d",
            body=maybe_transform(
                {
                    "image_request_id": image_request_id,
                    "image_url": image_url,
                    "seed": seed,
                    "texture_size": texture_size,
                },
                function_imageto3d_params.FunctionImageto3dParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GenerateResponseObject,
        )


class AsyncFunctionsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncFunctionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/masterpiecevr/mpx-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncFunctionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncFunctionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/masterpiecevr/mpx-sdk-python#with_streaming_response
        """
        return AsyncFunctionsResourceWithStreamingResponse(self)

    async def create_general(
        self,
        *,
        prompt: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GenerateResponseObject:
        """
        This function generates anything from just a single prompt! Once you make this
        function request, make note of the returned requestId. Then call the status
        endpoint to get the current status of the request. Currently, requests can take
        \\~~2-5mins to complete.

        Args:
          prompt: The prompt to use for the generation

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/functions/general",
            body=await async_maybe_transform(
                {"prompt": prompt}, function_create_general_params.FunctionCreateGeneralParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GenerateResponseObject,
        )

    async def imageto3d(
        self,
        *,
        image_request_id: str | NotGiven = NOT_GIVEN,
        image_url: str | NotGiven = NOT_GIVEN,
        seed: float | NotGiven = NOT_GIVEN,
        texture_size: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GenerateResponseObject:
        """This function generates a 3D model (GLB, FBX, USDZ) from an image.

        You can
        upload your own image or provide a URL to an image. To upload your own image,
        first call the **assets/create** endpoint to create an assetId for the image,
        then upload the image to our servers using the returned URL. Once you make this
        function request, make note of the returned requestId. Then call the status
        endpoint to get the current status of the request. Currently, requests can take
        \\~~1-2mins to complete.

        Args:
          image_request_id: The requestId from the /assets/create endpoint that the image was uploaded to.
              Do not use this if you have an imageUrl.

          image_url: The URL of the image to use for the generation. Use this instead of
              imageRequestId if you did not upload the image to our servers using the
              /assets/create endpoint.

          seed: Seed used to generate the 3D model

          texture_size: Size of the texture to use for the model. Higher values will result in more
              detailed models but will take longer to process. Must be one of 256, 512, 1024,
              2048

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/functions/imageto3d",
            body=await async_maybe_transform(
                {
                    "image_request_id": image_request_id,
                    "image_url": image_url,
                    "seed": seed,
                    "texture_size": texture_size,
                },
                function_imageto3d_params.FunctionImageto3dParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GenerateResponseObject,
        )


class FunctionsResourceWithRawResponse:
    def __init__(self, functions: FunctionsResource) -> None:
        self._functions = functions

        self.create_general = to_raw_response_wrapper(
            functions.create_general,
        )
        self.imageto3d = to_raw_response_wrapper(
            functions.imageto3d,
        )


class AsyncFunctionsResourceWithRawResponse:
    def __init__(self, functions: AsyncFunctionsResource) -> None:
        self._functions = functions

        self.create_general = async_to_raw_response_wrapper(
            functions.create_general,
        )
        self.imageto3d = async_to_raw_response_wrapper(
            functions.imageto3d,
        )


class FunctionsResourceWithStreamingResponse:
    def __init__(self, functions: FunctionsResource) -> None:
        self._functions = functions

        self.create_general = to_streamed_response_wrapper(
            functions.create_general,
        )
        self.imageto3d = to_streamed_response_wrapper(
            functions.imageto3d,
        )


class AsyncFunctionsResourceWithStreamingResponse:
    def __init__(self, functions: AsyncFunctionsResource) -> None:
        self._functions = functions

        self.create_general = async_to_streamed_response_wrapper(
            functions.create_general,
        )
        self.imageto3d = async_to_streamed_response_wrapper(
            functions.imageto3d,
        )
