from __future__ import annotations
import typing
from ._base_element import BaseElement
from typing_extensions import TypedDict, Unpack
from ._utils import handle_props
from .popup import TPopupProps, TPopupPlacementValue

if typing.TYPE_CHECKING:
    from instaui.vars.types import TMaybeRef


class Tooltip(BaseElement):
    def __init__(
        self,
        content: str,
        **kwargs: Unpack[TTooltipProps],
    ):
        super().__init__("t-tooltip")
        self.props({"content": content})
        self.props(handle_props(kwargs))  # type: ignore


class TooltipLite(BaseElement):
    def __init__(
        self,
        content: str,
        **kwargs: Unpack[TTooltipLiteProps],
    ):
        super().__init__("t-tooltip-lite")
        self.props({"content": content})
        self.props(handle_props(kwargs))  # type: ignore


class TTooltipProps(TPopupProps, total=False):
    delay: float
    destroy_on_close: bool
    duration: float
    placement: TPopupPlacementValue
    show_arrow: bool
    theme: TMaybeRef[
        typing.Literal["default", "primary", "success", "danger", "warning", "light"]
    ]


class TTooltipLiteProps(TypedDict, total=False):
    placement: typing.Literal["top", "bottom"]
    show_arrow: bool
    show_shadow: bool
    theme: typing.Literal["light", "default"]
    trigger_element: typing.Literal["TNode"]
