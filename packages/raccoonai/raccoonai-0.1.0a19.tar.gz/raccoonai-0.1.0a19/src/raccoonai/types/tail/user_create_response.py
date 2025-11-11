# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["UserCreateResponse"]


class UserCreateResponse(BaseModel):
    email: str
    """Email of the created user."""

    name: str
    """Name of the created user."""

    raccoon_passcode: str = FieldInfo(alias="raccoonPasscode")
    """Raccoon passcode associated with the user."""

    success: bool
    """If user was created successfully."""
