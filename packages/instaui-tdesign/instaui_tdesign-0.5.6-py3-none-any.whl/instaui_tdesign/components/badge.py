from __future__ import annotations
import typing
from ._base_element import BaseElement
from typing_extensions import TypedDict, Unpack
from ._utils import handle_props, handle_event_from_props


class Badge(BaseElement):
    def __init__(
        self,
        content: typing.Optional[str] = None,
        **kwargs: Unpack[TBadgeProps],
    ):
        super().__init__("t-badge")
        self.props({"content": content})

        self.props(handle_props(kwargs))  # type: ignore
        handle_event_from_props(self, kwargs)  # type: ignore


class TBadgeProps(TypedDict, total=False):
    color: str
    count: typing.Union[int, str]
    dot: bool
    max_count: float
    offset: typing.List
    shape: typing.Literal["circle", "round"]
    show_zero: bool
    size: typing.Literal["small", "medium"]
