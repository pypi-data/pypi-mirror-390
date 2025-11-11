# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["UserAllParams"]


class UserAllParams(TypedDict, total=False):
    email_id: Annotated[Optional[str], PropertyInfo(alias="emailId")]

    limit: Optional[int]

    page: Optional[int]

    raccoon_passcode: Annotated[Optional[str], PropertyInfo(alias="raccoonPasscode")]

    search_query: Annotated[Optional[str], PropertyInfo(alias="searchQuery")]

    sort_by: Annotated[Optional[Literal["createdAt", "name", "email", "raccoonPasscode"]], PropertyInfo(alias="sortBy")]

    sort_order: Annotated[Optional[Literal["ascend", "descend"]], PropertyInfo(alias="sortOrder")]
