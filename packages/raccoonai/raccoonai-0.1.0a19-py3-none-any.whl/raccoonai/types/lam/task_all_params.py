# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Optional
from typing_extensions import Literal, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["TaskAllParams"]


class TaskAllParams(TypedDict, total=False):
    end_time: Optional[int]
    """Filter tasks created before this Unix timestamp (in milliseconds)."""

    execution_type: Annotated[
        Optional[List[Literal["default", "deepsearch", "fleet"]]], PropertyInfo(alias="executionType")
    ]
    """Filter tasks by execution type (e.g., 'default', 'deepsearch')."""

    limit: Optional[int]
    """Number of tasks per page (maximum 100)."""

    page: Optional[int]
    """Page number for pagination."""

    raccoon_passcode: Optional[str]
    """Filter tasks by Raccoon passcode."""

    sort_by: Optional[Literal["timestamp", "executionTime", "taskId", "status", "executionType"]]
    """Field to sort tasks by (e.g., 'timestamp', 'executionTime')."""

    sort_order: Optional[Literal["ascend", "descend"]]
    """Sort order ('ascend' or 'descend')."""

    start_time: Optional[int]
    """Filter tasks created after this Unix timestamp (in milliseconds)."""

    task_id: Optional[str]
    """Filter tasks by a specific task ID."""
