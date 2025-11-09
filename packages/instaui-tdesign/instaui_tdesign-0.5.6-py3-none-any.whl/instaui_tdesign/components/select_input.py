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


class SelectInput(BaseElement):
    def __init__(
        self,
        value: typing.Optional[typing.Union[str, int, float, bool]] = None,
        *,
        model_value: typing.Optional[typing.Union[str, int, float, bool]] = None,
        prefix_icon: typing.Optional[str] = None,
        suffix_icon: typing.Optional[str] = None,
        **kwargs: Unpack[TSelectInputProps],
    ):
        super().__init__("t-select-input")

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

    def on_input_change(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "input-change",
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

    def on_paste(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "paste",
            handler,
            extends=extends,
        )
        return self

    def on_popup_visible_change(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "popup-visible-change",
            handler,
            extends=extends,
        )
        return self

    def on_tag_change(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "tag-change",
            handler,
            extends=extends,
        )
        return self


class TSelectInputProps(TypedDict, total=False):
    allow_input: bool
    auto_width: bool
    autofocus: bool
    borderless: bool
    clearable: bool
    collapsed_items: str
    disabled: bool
    input_props: typing.Dict
    input_value: typing.Union[float, str]
    default_input_value: typing.Union[float, str]
    keys: typing.Dict
    label: str
    loading: bool
    min_collapsed_num: float
    multiple: bool
    panel: str
    placeholder: str
    popup_props: typing.Dict
    popup_visible: bool
    default_popup_visible: bool
    readonly: bool
    reserve_keyword: bool
    size: typing.Literal["small", "medium", "large"]
    status: typing.Literal["default", "success", "warning", "error"]
    suffix: str
    tag: str
    tag_input_props: typing.Dict
    tag_props: typing.Dict
    tips: str
    value_display: str
    on_blur: EventMixin
    on_clear: EventMixin
    on_enter: EventMixin
    on_focus: EventMixin
    on_input_change: EventMixin
    on_mouseenter: EventMixin
    on_mouseleave: EventMixin
    on_paste: EventMixin
    on_popup_visible_change: EventMixin
    on_tag_change: EventMixin
