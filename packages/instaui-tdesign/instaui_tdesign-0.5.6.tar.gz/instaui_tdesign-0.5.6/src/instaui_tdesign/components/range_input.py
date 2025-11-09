from __future__ import annotations
import typing

from instaui_tdesign.components._icon_param_utils import (
    make_prefix_icon,
    make_suffix_icon,
)
from ._base_element import BaseElement
from instaui.event.event_mixin import EventMixin
from typing_extensions import TypedDict, Unpack
from ._utils import handle_props, handle_event_from_props, try_setup_vmodel

if typing.TYPE_CHECKING:
    from instaui.vars.types import TMaybeRef


class RangeInput(BaseElement):
    def __init__(
        self,
        value: typing.Optional[typing.List] = None,
        *,
        model_value: typing.Optional[typing.List] = None,
        prefix_icon: typing.Optional[str] = None,
        suffix_icon: typing.Optional[str] = None,
        **kwargs: Unpack[TRangeInputProps],
    ):
        super().__init__("t-range-input")

        try_setup_vmodel(self, value)
        make_prefix_icon(self, prefix_icon)
        make_suffix_icon(self, suffix_icon)
        self.props(handle_props(kwargs, model_value=model_value))  # type: ignore
        handle_event_from_props(self, kwargs)  # type: ignore

    def on_blur(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "blur",
            handler,
            extends=extends,
        )
        return self

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

    def on_clear(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "clear",
            handler,
            extends=extends,
        )
        return self

    def on_click(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "click",
            handler,
            extends=extends,
        )
        return self

    def on_enter(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "enter",
            handler,
            extends=extends,
        )
        return self

    def on_focus(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "focus",
            handler,
            extends=extends,
        )
        return self

    def on_mouseenter(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "mouseenter",
            handler,
            extends=extends,
        )
        return self

    def on_mouseleave(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "mouseleave",
            handler,
            extends=extends,
        )
        return self


class TRangeInputProps(TypedDict, total=False):
    active_index: float
    borderless: bool
    clearable: bool
    disabled: bool
    format: typing.Union[TMaybeRef[str, typing.List]]
    input_props: typing.Union[TMaybeRef[typing.Dict, typing.List]]
    label: str
    placeholder: typing.Literal["Array"]
    readonly: bool
    separator: str
    show_clear_icon_on_empty: bool
    size: typing.Literal["small", "medium", "large"]
    status: typing.Literal["default", "success", "warning", "error"]
    suffix: str
    tips: str
    default_value: typing.List
    on_blur: EventMixin
    on_change: EventMixin
    on_clear: EventMixin
    on_click: EventMixin
    on_enter: EventMixin
    on_focus: EventMixin
    on_mouseenter: EventMixin
    on_mouseleave: EventMixin


class TRangeInputPopupProps(TypedDict, total=False):
    auto_width: bool
    disabled: bool
    input_value: typing.List
    default_input_value: typing.List
    label: str
    panel: str
    popup_props: typing.Dict
    popup_visible: bool
    default_popup_visible: bool
    range_input_props: typing.Dict
    readonly: bool
    status: typing.Literal["default", "success", "warning", "error"]
    tips: str
    on_input_change: EventMixin
    on_popup_visible_change: EventMixin
