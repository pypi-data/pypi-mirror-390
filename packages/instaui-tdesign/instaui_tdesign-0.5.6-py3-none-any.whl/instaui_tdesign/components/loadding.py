from __future__ import annotations
import typing
from ._base_element import BaseElement
from typing_extensions import TypedDict, Unpack
from ._utils import handle_props


class Loading(BaseElement):
    def __init__(
        self,
        indicator: typing.Optional[bool] = None,
        *,
        text: typing.Optional[typing.Any] = None,
        **kwargs: Unpack[TLoadingProps],
    ):
        super().__init__("t-loading")
        self.props({"text": text, "indicator": indicator})
        self.props(handle_props(kwargs))  # type: ignore


class TLoadingProps(TypedDict, total=False):
    attach: str
    content: str
    delay: float
    fullscreen: bool
    inherit_color: bool
    loading: bool
    prevent_scroll_through: bool
    show_overlay: bool
    size: str
    z_index: float
