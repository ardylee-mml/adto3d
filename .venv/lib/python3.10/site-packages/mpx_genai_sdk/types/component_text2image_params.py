# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["ComponentText2imageParams"]


class ComponentText2imageParams(TypedDict, total=False):
    prompt: Required[str]
    """The prompt to use for the generation of the image"""

    aspect_ratio: Annotated[str, PropertyInfo(alias="aspectRatio")]
    """The aspect ratio of the image to use for the generation.

    Allowed values are (1:1, 16:9, 4:3, 3:4, 9:16, 1:2, 2:1)
    """

    lora_id: Annotated[str, PropertyInfo(alias="loraId")]
    """The lora id to use for the generation (default is empty string).

    These selected loras are optimized for the image to 3d component. select from
    (mpx_plush, mpx_iso, mpx_game) Cannot be used with loraWeights.
    """

    lora_scale: Annotated[float, PropertyInfo(alias="loraScale")]
    """The strength of the lora to use for the generation (default is 0.8).

    Cannot be used with loraId
    """

    lora_weights: Annotated[str, PropertyInfo(alias="loraWeights")]
    """The Url of the lora to use for the generation (default is empty string).

    Eg. https://huggingface.co/gokaygokay/Flux-Game-Assets-LoRA-v2 Cannot be used
    with loraId.
    """

    megapixels: float
    """The rough number of megapixels of the image to use for the generation.

    Allowed values are (1, 2, 4)
    """

    num_images: Annotated[float, PropertyInfo(alias="numImages")]
    """The number of images to generate (default is 1, max is 4)"""

    num_steps: Annotated[float, PropertyInfo(alias="numSteps")]
    """The number of steps to use for the generation (default is 4)"""

    output_format: Annotated[str, PropertyInfo(alias="outputFormat")]
    """The format of the image to use for the generation.

    Allowed values are (png, jpg, webp)
    """

    seed: float
    """The seed to use for the generation (default is random)"""
