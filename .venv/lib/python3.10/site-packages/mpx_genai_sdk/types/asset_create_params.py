# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["AssetCreateParams"]


class AssetCreateParams(TypedDict, total=False):
    description: Required[str]
    """The description of the asset"""

    name: Required[str]
    """The name of the asset"""

    type: Required[str]
    """The mime type of the asset (eg.

    model/gltf-binary for GLB files, image/png for PNG files)
    """
