# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["LamRunResponse"]


class LamRunResponse(BaseModel):
    data: List[object]
    """The extracted data as a list of objects when the status is DONE.

    Each object represents an extracted entity.
    """

    livestream_url: str
    """The Livestream URL"""

    message: str
    """A message providing the thought summary if the status is processing currently."""

    properties: object
    """Additional metadata or details related to the run task."""

    task_status: Literal["STARTING", "PROCESSING", "DONE", "HUMAN_INTERACTION", "FAILURE"]
    """The current status of the extraction task.

    For example: 'STARTING', 'PROCESSING', 'DONE', 'HUMAN_INTERACTION', or
    'FAILURE'.
    """
