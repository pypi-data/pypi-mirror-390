from __future__ import annotations
import typing
from instaui.event.event_mixin import EventMixin
from typing_extensions import TypedDict, Unpack
from ._utils import handle_props, handle_event_from_props
from ._base_element import BaseElement


class Affix(BaseElement):
    def __init__(
        self,
        **kwargs: Unpack[TAffixProps],
    ):
        super().__init__("t-affix")

        self.props(handle_props(kwargs))  # type: ignore
        handle_event_from_props(self, kwargs)  # type: ignore

    def on_fixed_change(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "fixed-change",
            handler,
            extends=extends,
        )
        return self


class TAffixProps(TypedDict, total=False):
    container: str
    offset_bottom: float
    offset_top: float
    z_index: int
    on_fixed_change: EventMixin
