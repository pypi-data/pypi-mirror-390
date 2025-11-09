from __future__ import annotations
import typing
from ._base_element import BaseElement
from typing_extensions import TypedDict, Unpack
from ._utils import handle_props

if typing.TYPE_CHECKING:
    from instaui.vars.types import TMaybeRef


class Skeleton(BaseElement):
    def __init__(
        self,
        **kwargs: Unpack[TSkeletonProps],
    ):
        super().__init__("t-skeleton")
        self.props(handle_props(kwargs))  # type: ignore


class TSkeletonProps(TypedDict, total=False):
    animation: typing.Literal["gradient", "flashed", "none"]
    delay: float
    loading: bool
    row_col: typing.List
    theme: TMaybeRef[
        typing.Literal["text", "avatar", "paragraph", "avatar-text", "tab", "article"]
    ]
