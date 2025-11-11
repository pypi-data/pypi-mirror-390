# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["AppLinkedResponse"]


class AppLinkedResponse(BaseModel):
    linked_apps: List[str] = FieldInfo(alias="linkedApps")
    """List of linked application names."""
