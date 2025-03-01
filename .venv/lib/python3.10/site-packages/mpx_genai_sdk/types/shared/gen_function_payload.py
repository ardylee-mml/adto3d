# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.


from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["GenFunctionPayload"]


class GenFunctionPayload(BaseModel):
    is_creative: bool = FieldInfo(alias="isCreative")
    """Whether to use a creative approach for the generation.

    If true, the function will use the base_mesh_gen component to generate a more
    creative mesh. If false, the function will use the base_mesh_select component to
    generate a more conservative mesh.
    """

    mesh_prompt: str = FieldInfo(alias="meshPrompt")
    """The prompt to use for the generation of the mesh"""

    mesh_variability: float = FieldInfo(alias="meshVariability")
    """The variability of the mesh to use for the generation"""

    paint_prompt_neg: str = FieldInfo(alias="paintPromptNeg")
    """The negative prompt to use to describe the textures"""

    paint_prompt_pos: str = FieldInfo(alias="paintPromptPos")
    """The positive prompt to use to describe the textures"""
