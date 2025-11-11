# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["SessionCreateResponse"]


class SessionCreateResponse(BaseModel):
    livestream_url: str
    """The Livestream URL"""

    session_id: str
    """A unique identifier for the created session."""

    status: Literal["starting", "running", "terminated", "completed", "unknown", "success", "failure"]
    """The current status of the session."""

    websocket_url: str
    """The WebSocket URL for interacting with the session."""
