# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["AppLinkedParams"]


class AppLinkedParams(TypedDict, total=False):
    raccoon_passcode: Required[Annotated[str, PropertyInfo(alias="raccoonPasscode")]]
