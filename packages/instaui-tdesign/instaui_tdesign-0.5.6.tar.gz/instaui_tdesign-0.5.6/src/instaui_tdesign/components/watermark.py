from __future__ import annotations
import typing
from ._base_element import BaseElement
from typing_extensions import TypedDict, Unpack
from ._utils import handle_props

if typing.TYPE_CHECKING:
    from instaui.vars.types import TMaybeRef


class Watermark(BaseElement):
    def __init__(
        self,
        content: str,
        **kwargs: Unpack[TWatermarkProps],
    ):
        super().__init__("t-watermark")
        self.props({"content": content})
        self.props(handle_props(kwargs))  # type: ignore


class TWatermarkProps(TypedDict, total=False):
    alpha: float
    height: float
    is_repeat: bool
    line_space: float
    movable: bool
    move_interval: float
    offset: typing.List
    removable: bool
    rotate: float
    watermark_content: TMaybeRef[typing.Union[typing.Dict, typing.List]]
    width: float
    x: float
    y: float
    z_index: int
