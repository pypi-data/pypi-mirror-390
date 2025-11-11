# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["SessionStatusResponse"]


class SessionStatusResponse(BaseModel):
    session_id: str
    """A unique identifier for the session."""

    status: Literal["starting", "running", "terminated", "completed", "unknown"]
    """The current status of the session."""
