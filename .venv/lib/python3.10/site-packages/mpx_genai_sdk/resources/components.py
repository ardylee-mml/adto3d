# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import component_optimize_params, component_text2image_params
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
from ..types.shared.create_response_object import CreateResponseObject
from ..types.shared.generate_response_object import GenerateResponseObject

__all__ = ["ComponentsResource", "AsyncComponentsResource"]


class ComponentsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ComponentsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/masterpiecevr/mpx-sdk-python#accessing-raw-response-data-eg-headers
        """
        return ComponentsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ComponentsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/masterpiecevr/mpx-sdk-python#with_streaming_response
        """
        return ComponentsResourceWithStreamingResponse(self)

    def optimize(
        self,
        *,
        asset_request_id: str,
        object_type: str,
        output_file_format: str,
        target_ratio: float,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CreateResponseObject:
        """
        This function optionally reduces the polycount of your model and/or returns a
        different file format. eg. convert from GLB to USDZ.

        The **assetRequestId** can be a requestId from a **Generate** request or an
        assetId from an **assets/create** request. If you are converting a model you
        uploaded, please ensure that the model has been uploaded before calling this
        endpoint.

        The **targetRatio** is the ratio of the original polycount that you want to
        reduce to. eg. 0.5 will reduce the polycount by 50%.

        The **outputFileFormat** is the file format you want the model returned in.
        Currently, we support FBX, GLB and USDZ.

        The **objectType** is the type of model you are uploading. Currently, we support
        'object', 'animal' and 'humanoid'.

        Args:
          asset_request_id: The requestId from the /assets/create endpoint that the model was uploaded to

          object_type: The type of model you are uploading. Currently, we support 'object', 'animal'
              and 'humanoid'.

          output_file_format: The file format you want the model returned in. Currently, we support FBX, GLB
              and USDZ.

          target_ratio: The ratio of the original polycount that you want to reduce to. eg. 0.5 will
              reduce the polycount by 50%.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/components/optimize",
            body=maybe_transform(
                {
                    "asset_request_id": asset_request_id,
                    "object_type": object_type,
                    "output_file_format": output_file_format,
                    "target_ratio": target_ratio,
                },
                component_optimize_params.ComponentOptimizeParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CreateResponseObject,
        )

    def text2image(
        self,
        *,
        prompt: str,
        aspect_ratio: str | NotGiven = NOT_GIVEN,
        lora_id: str | NotGiven = NOT_GIVEN,
        lora_scale: float | NotGiven = NOT_GIVEN,
        lora_weights: str | NotGiven = NOT_GIVEN,
        megapixels: float | NotGiven = NOT_GIVEN,
        num_images: float | NotGiven = NOT_GIVEN,
        num_steps: float | NotGiven = NOT_GIVEN,
        output_format: str | NotGiven = NOT_GIVEN,
        seed: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GenerateResponseObject:
        """This function creates one to four images that you can use for further
        processing.

        You can use the generated image(s) as input for image to 3d. Use the
        status endpoint to check the status of the request. Download the image(s) from
        the outputUrl and then upload to the assets/create endpoint to use with other
        components/functions.

        Args:
          prompt: The prompt to use for the generation of the image

          aspect_ratio: The aspect ratio of the image to use for the generation. Allowed values are
              (1:1, 16:9, 4:3, 3:4, 9:16, 1:2, 2:1)

          lora_id: The lora id to use for the generation (default is empty string). These selected
              loras are optimized for the image to 3d component. select from (mpx_plush,
              mpx_iso, mpx_game) Cannot be used with loraWeights.

          lora_scale: The strength of the lora to use for the generation (default is 0.8). Cannot be
              used with loraId

          lora_weights: The Url of the lora to use for the generation (default is empty string). Eg.
              https://huggingface.co/gokaygokay/Flux-Game-Assets-LoRA-v2 Cannot be used with
              loraId.

          megapixels: The rough number of megapixels of the image to use for the generation. Allowed
              values are (1, 2, 4)

          num_images: The number of images to generate (default is 1, max is 4)

          num_steps: The number of steps to use for the generation (default is 4)

          output_format: The format of the image to use for the generation. Allowed values are (png, jpg,
              webp)

          seed: The seed to use for the generation (default is random)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/components/text2image",
            body=maybe_transform(
                {
                    "prompt": prompt,
                    "aspect_ratio": aspect_ratio,
                    "lora_id": lora_id,
                    "lora_scale": lora_scale,
                    "lora_weights": lora_weights,
                    "megapixels": megapixels,
                    "num_images": num_images,
                    "num_steps": num_steps,
                    "output_format": output_format,
                    "seed": seed,
                },
                component_text2image_params.ComponentText2imageParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GenerateResponseObject,
        )


class AsyncComponentsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncComponentsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/masterpiecevr/mpx-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncComponentsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncComponentsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/masterpiecevr/mpx-sdk-python#with_streaming_response
        """
        return AsyncComponentsResourceWithStreamingResponse(self)

    async def optimize(
        self,
        *,
        asset_request_id: str,
        object_type: str,
        output_file_format: str,
        target_ratio: float,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CreateResponseObject:
        """
        This function optionally reduces the polycount of your model and/or returns a
        different file format. eg. convert from GLB to USDZ.

        The **assetRequestId** can be a requestId from a **Generate** request or an
        assetId from an **assets/create** request. If you are converting a model you
        uploaded, please ensure that the model has been uploaded before calling this
        endpoint.

        The **targetRatio** is the ratio of the original polycount that you want to
        reduce to. eg. 0.5 will reduce the polycount by 50%.

        The **outputFileFormat** is the file format you want the model returned in.
        Currently, we support FBX, GLB and USDZ.

        The **objectType** is the type of model you are uploading. Currently, we support
        'object', 'animal' and 'humanoid'.

        Args:
          asset_request_id: The requestId from the /assets/create endpoint that the model was uploaded to

          object_type: The type of model you are uploading. Currently, we support 'object', 'animal'
              and 'humanoid'.

          output_file_format: The file format you want the model returned in. Currently, we support FBX, GLB
              and USDZ.

          target_ratio: The ratio of the original polycount that you want to reduce to. eg. 0.5 will
              reduce the polycount by 50%.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/components/optimize",
            body=await async_maybe_transform(
                {
                    "asset_request_id": asset_request_id,
                    "object_type": object_type,
                    "output_file_format": output_file_format,
                    "target_ratio": target_ratio,
                },
                component_optimize_params.ComponentOptimizeParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CreateResponseObject,
        )

    async def text2image(
        self,
        *,
        prompt: str,
        aspect_ratio: str | NotGiven = NOT_GIVEN,
        lora_id: str | NotGiven = NOT_GIVEN,
        lora_scale: float | NotGiven = NOT_GIVEN,
        lora_weights: str | NotGiven = NOT_GIVEN,
        megapixels: float | NotGiven = NOT_GIVEN,
        num_images: float | NotGiven = NOT_GIVEN,
        num_steps: float | NotGiven = NOT_GIVEN,
        output_format: str | NotGiven = NOT_GIVEN,
        seed: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GenerateResponseObject:
        """This function creates one to four images that you can use for further
        processing.

        You can use the generated image(s) as input for image to 3d. Use the
        status endpoint to check the status of the request. Download the image(s) from
        the outputUrl and then upload to the assets/create endpoint to use with other
        components/functions.

        Args:
          prompt: The prompt to use for the generation of the image

          aspect_ratio: The aspect ratio of the image to use for the generation. Allowed values are
              (1:1, 16:9, 4:3, 3:4, 9:16, 1:2, 2:1)

          lora_id: The lora id to use for the generation (default is empty string). These selected
              loras are optimized for the image to 3d component. select from (mpx_plush,
              mpx_iso, mpx_game) Cannot be used with loraWeights.

          lora_scale: The strength of the lora to use for the generation (default is 0.8). Cannot be
              used with loraId

          lora_weights: The Url of the lora to use for the generation (default is empty string). Eg.
              https://huggingface.co/gokaygokay/Flux-Game-Assets-LoRA-v2 Cannot be used with
              loraId.

          megapixels: The rough number of megapixels of the image to use for the generation. Allowed
              values are (1, 2, 4)

          num_images: The number of images to generate (default is 1, max is 4)

          num_steps: The number of steps to use for the generation (default is 4)

          output_format: The format of the image to use for the generation. Allowed values are (png, jpg,
              webp)

          seed: The seed to use for the generation (default is random)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/components/text2image",
            body=await async_maybe_transform(
                {
                    "prompt": prompt,
                    "aspect_ratio": aspect_ratio,
                    "lora_id": lora_id,
                    "lora_scale": lora_scale,
                    "lora_weights": lora_weights,
                    "megapixels": megapixels,
                    "num_images": num_images,
                    "num_steps": num_steps,
                    "output_format": output_format,
                    "seed": seed,
                },
                component_text2image_params.ComponentText2imageParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GenerateResponseObject,
        )


class ComponentsResourceWithRawResponse:
    def __init__(self, components: ComponentsResource) -> None:
        self._components = components

        self.optimize = to_raw_response_wrapper(
            components.optimize,
        )
        self.text2image = to_raw_response_wrapper(
            components.text2image,
        )


class AsyncComponentsResourceWithRawResponse:
    def __init__(self, components: AsyncComponentsResource) -> None:
        self._components = components

        self.optimize = async_to_raw_response_wrapper(
            components.optimize,
        )
        self.text2image = async_to_raw_response_wrapper(
            components.text2image,
        )


class ComponentsResourceWithStreamingResponse:
    def __init__(self, components: ComponentsResource) -> None:
        self._components = components

        self.optimize = to_streamed_response_wrapper(
            components.optimize,
        )
        self.text2image = to_streamed_response_wrapper(
            components.text2image,
        )


class AsyncComponentsResourceWithStreamingResponse:
    def __init__(self, components: AsyncComponentsResource) -> None:
        self._components = components

        self.optimize = async_to_streamed_response_wrapper(
            components.optimize,
        )
        self.text2image = async_to_streamed_response_wrapper(
            components.text2image,
        )
