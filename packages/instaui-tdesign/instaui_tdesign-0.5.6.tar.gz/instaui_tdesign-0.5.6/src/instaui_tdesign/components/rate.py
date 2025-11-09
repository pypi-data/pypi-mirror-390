from __future__ import annotations
import typing

from instaui_tdesign.components._icon_param_utils import make_icon_for_str
from ._base_element import BaseElement
from instaui.event.event_mixin import EventMixin
from typing_extensions import TypedDict, Unpack
from ._utils import handle_props, handle_event_from_props, try_setup_vmodel


class Rate(BaseElement):
    def __init__(
        self,
        value: typing.Optional[float] = None,
        *,
        count: typing.Optional[float] = None,
        default_value: typing.Optional[float] = None,
        model_value: typing.Optional[float] = None,
        icon: typing.Optional[str] = None,
        **kwargs: Unpack[TRateProps],
    ):
        super().__init__("t-rate")

        self.props({"count": count, "default-value": default_value})
        try_setup_vmodel(self, value)
        make_icon_for_str(self, icon)
        self.props(handle_props(kwargs, model_value=model_value))  # type: ignore
        handle_event_from_props(self, kwargs)  # type: ignore

    def on_change(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "change",
            handler,
            extends=extends,
        )
        return self


class TRateProps(TypedDict, total=False):
    allow_half: bool
    clearable: bool
    color: typing.Literal["Array"]
    disabled: bool
    gap: float
    show_text: bool
    size: str
    texts: typing.List
    on_change: EventMixin
