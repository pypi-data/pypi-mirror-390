# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["UserAllResponse", "Meta", "User"]


class Meta(BaseModel):
    current_page: int = FieldInfo(alias="currentPage")
    """The current page number."""

    total_pages: int = FieldInfo(alias="totalPages")
    """Total number of pages available."""

    total_records: int = FieldInfo(alias="totalRecords")
    """Total number of records across all pages."""


class User(BaseModel):
    avatar: str
    """URL of the user's avatar image."""

    created_at: int = FieldInfo(alias="createdAt")
    """Unix timestamp (in milliseconds) indicating when the user account was created."""

    email: str
    """User's email address."""

    name: str
    """User's full name."""

    raccoon_passcode: str = FieldInfo(alias="raccoonPasscode")
    """Passcode associated with the user."""


class UserAllResponse(BaseModel):
    admin_raccoon_passcode: str = FieldInfo(alias="adminRaccoonPasscode")
    """Admin Raccoon passcode."""

    meta: Meta
    """Metadata about the user list."""

    users: List[User]
    """List of users."""
