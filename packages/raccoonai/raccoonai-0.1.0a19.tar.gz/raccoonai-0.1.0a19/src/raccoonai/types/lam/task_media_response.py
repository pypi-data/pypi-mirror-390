# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["TaskMediaResponse", "Media", "MediaAction", "MediaRecording"]


class MediaAction(BaseModel):
    action: str
    """The type of action performed, e.g., 'click'."""

    index: int
    """The sequential index of the action."""

    screenshot: str
    """URL of the screenshot taken at the time of the action."""


class MediaRecording(BaseModel):
    page_title: str = FieldInfo(alias="pageTitle")
    """The title of the webpage where the recording took place."""

    page_url: str = FieldInfo(alias="pageUrl")
    """The URL of the webpage where the recording took place."""

    url: str
    """URL of the recording file."""


class Media(BaseModel):
    actions: List[MediaAction]
    """A list of actions performed, not applicable to fleet sessions."""

    recordings: List[MediaRecording]
    """A list of recordings associated."""

    session_id: str = FieldInfo(alias="sessionId")
    """A unique identifier for the session."""


class TaskMediaResponse(BaseModel):
    media: List[Media]
    """A list of media data, including actions and recordings."""

    task_id: str = FieldInfo(alias="taskId")
    """A unique identifier for the task."""
