# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["UserCreateParams"]


class UserCreateParams(TypedDict, total=False):
    email: Required[str]
    """specify email of user."""

    name: Required[str]
    """specify name of user."""
