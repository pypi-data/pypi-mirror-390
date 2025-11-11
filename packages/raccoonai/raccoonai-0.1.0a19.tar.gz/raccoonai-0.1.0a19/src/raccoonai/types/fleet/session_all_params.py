# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Optional
from typing_extensions import Literal, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["SessionAllParams"]


class SessionAllParams(TypedDict, total=False):
    end_time: Optional[int]
    """Filter sessions created before this Unix timestamp (in milliseconds)."""

    execution_type: Annotated[
        Optional[List[Literal["default", "deepsearch", "fleet"]]], PropertyInfo(alias="executionType")
    ]
    """Filter sessions by execution type (e.g., 'default', 'deepsearch')."""

    limit: Optional[int]
    """Number of sessions per page (maximum 100)."""

    page: Optional[int]
    """Page number for pagination."""

    raccoon_passcode: Optional[str]
    """Filter sessions by Raccoon passcode."""

    session_id: Optional[str]
    """Filter sessions by a specific session ID."""

    sort_by: Optional[Literal["timestamp", "executionTime", "taskId", "status", "executionType"]]
    """Field to sort sessions by (e.g., 'timestamp', 'executionTime')."""

    sort_order: Optional[Literal["ascend", "descend"]]
    """Sort order ('ascend' or 'descend')."""

    start_time: Optional[int]
    """Filter sessions created after this Unix timestamp (in milliseconds)."""

    task_id: Optional[str]
    """Filter sessions by a specific task ID."""
