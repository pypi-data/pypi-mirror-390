# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["UserStatusResponse"]


class UserStatusResponse(BaseModel):
    app_name: str = FieldInfo(alias="appName")
    """The name of the app for which the authentication status is checked"""

    status: Literal["unliked", "active"]
    """Authentication status."""
