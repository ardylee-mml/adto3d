# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["FunctionCreateGeneralParams"]


class FunctionCreateGeneralParams(TypedDict, total=False):
    prompt: Required[str]
    """The prompt to use for the generation"""
