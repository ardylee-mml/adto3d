# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["StatusResponseObject", "Outputs"]


class Outputs(BaseModel):
    fbx: Optional[str] = None
    """The URL of FBX output model. Only available if status is complete"""

    glb: Optional[str] = None
    """The URL of GLB output model. Only available if status is complete"""

    thumbnail: Optional[str] = None
    """The URL of thumbnail image. Only available if status is complete"""

    usdz: Optional[str] = None
    """The URL of USDZ output model. Only available if status is complete"""


class StatusResponseObject(BaseModel):
    outputs: Optional[Outputs] = None
    """The outputs of the request. Only available if status is complete"""

    output_url: Optional[str] = FieldInfo(alias="outputUrl", default=None)
    """The URL of the output model. Only available if status is complete"""

    processing_time_s: Optional[float] = FieldInfo(alias="processingTime_s", default=None)
    """The processing time in seconds. Only available if status is complete"""

    progress: Optional[float] = None
    """The progress of the request. Only available if status is pending | processing"""

    request_id: Optional[str] = FieldInfo(alias="requestId", default=None)
    """The request id"""

    status: Optional[str] = None
    """The status of the request"""
