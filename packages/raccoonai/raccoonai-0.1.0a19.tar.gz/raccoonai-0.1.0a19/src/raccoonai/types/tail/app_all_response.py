# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["AppAllResponse", "AvailableApp"]


class AvailableApp(BaseModel):
    app_name: str = FieldInfo(alias="appName")
    """Unique identifier for the application."""

    category: str
    """Category of the application (e.g., 'Productivity', 'Social')."""

    display_name: str = FieldInfo(alias="displayName")
    """Display name of the application."""

    status: Literal["Active", "In Review", "Not Accepted"]
    """Status of the application."""

    app_description: Optional[str] = FieldInfo(alias="appDescription", default=None)
    """A brief description of the application."""

    app_url: Optional[str] = FieldInfo(alias="appUrl", default=None)
    """URL of the application."""

    icon: Optional[str] = None
    """URL of the application icon."""


class AppAllResponse(BaseModel):
    available_apps: List[AvailableApp] = FieldInfo(alias="availableApps")
    """List of available applications."""
