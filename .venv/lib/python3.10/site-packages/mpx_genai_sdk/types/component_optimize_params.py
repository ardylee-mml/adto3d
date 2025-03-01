# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["ComponentOptimizeParams"]


class ComponentOptimizeParams(TypedDict, total=False):
    asset_request_id: Required[Annotated[str, PropertyInfo(alias="assetRequestId")]]
    """The requestId from the /assets/create endpoint that the model was uploaded to"""

    object_type: Required[Annotated[str, PropertyInfo(alias="objectType")]]
    """The type of model you are uploading.

    Currently, we support 'object', 'animal' and 'humanoid'.
    """

    output_file_format: Required[Annotated[str, PropertyInfo(alias="outputFileFormat")]]
    """The file format you want the model returned in.

    Currently, we support FBX, GLB and USDZ.
    """

    target_ratio: Required[Annotated[float, PropertyInfo(alias="targetRatio")]]
    """The ratio of the original polycount that you want to reduce to.

    eg. 0.5 will reduce the polycount by 50%.
    """
