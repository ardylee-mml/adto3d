# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["GenerateResponseObject"]


class GenerateResponseObject(BaseModel):
    balance: Optional[int] = None
    """The credit balance of your account after this request"""

    request_id: Optional[str] = FieldInfo(alias="requestId", default=None)
    """The request id"""

    status: Optional[str] = None
    """The status of the request"""
