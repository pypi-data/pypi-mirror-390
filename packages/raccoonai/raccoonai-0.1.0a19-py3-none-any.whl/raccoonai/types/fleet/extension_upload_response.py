# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["ExtensionUploadResponse"]


class ExtensionUploadResponse(BaseModel):
    extension_id: str = FieldInfo(alias="extensionId")
    """Unique identifier for the extension."""

    filename: str
    """Name of the extension file."""
