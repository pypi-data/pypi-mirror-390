# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable, Optional
from typing_extensions import Literal, Required, TypeAlias, TypedDict

__all__ = [
    "LamRunParamsBase",
    "Advanced",
    "AdvancedProxy",
    "AdvancedProxyProxySettings",
    "LamRunParamsNonStreaming",
    "LamRunParamsStreaming",
]


class LamRunParamsBase(TypedDict, total=False):
    query: Required[str]
    """The input query string for the request. This is typically the main prompt."""

    raccoon_passcode: Required[str]
    """
    The raccoon passcode associated with the end user on behalf of which the call is
    being made.
    """

    advanced: Optional[Advanced]
    """
    Advanced configuration options for the session, such as ad-blocking and CAPTCHA
    solving.
    """

    app_url: Optional[str]
    """This is the entrypoint URL for the web agent."""

    chat_history: Optional[Iterable[object]]
    """
    The history of the conversation as a list of messages or objects you might use
    while building a chat app to give the model context of the past conversation.
    """

    max_count: Optional[int]
    """The maximum number of results to extract."""

    mode: Optional[Literal["deepsearch", "default"]]
    """Mode of execution."""

    schema: object
    """The expected schema for the response.

    This is a dictionary where the keys describe the fields and the values describe
    their purposes.
    """


class AdvancedProxyProxySettings(TypedDict, total=False):
    city: Optional[str]
    """Target city."""

    country: Optional[str]
    """Target country (2-letter ISO code)."""

    state: Optional[str]
    """Target state (2-letter code)."""

    zip: Optional[int]
    """Target postal code."""


AdvancedProxy: TypeAlias = Union[AdvancedProxyProxySettings, bool]


class Advanced(TypedDict, total=False):
    block_ads: Optional[bool]
    """Whether to block advertisements during the browser session."""

    extension_ids: Optional[Iterable[object]]
    """list of extension ids"""

    proxy: AdvancedProxy
    """Proxy details for the browser session.

    Automatically defaults to True if solve_captchas is on.
    """

    solve_captchas: Optional[bool]
    """Whether to attempt automatic CAPTCHA solving."""


class LamRunParamsNonStreaming(LamRunParamsBase, total=False):
    stream: Optional[Literal[False]]
    """Whether the response should be streamed back or not."""


class LamRunParamsStreaming(LamRunParamsBase):
    stream: Required[Literal[True]]
    """Whether the response should be streamed back or not."""


LamRunParams = Union[LamRunParamsNonStreaming, LamRunParamsStreaming]
