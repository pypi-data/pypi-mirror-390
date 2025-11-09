from __future__ import annotations
import typing

from instaui_tdesign.components._icon_param_utils import (
    make_prefix_icon,
    make_suffix_icon,
)
from ._base_element import BaseElement
from instaui.components.content import Content
from instaui.event.event_mixin import EventMixin
from typing_extensions import TypedDict, Unpack
from ._utils import handle_props, handle_event_from_props, try_setup_vmodel


class Select(BaseElement):
    def __init__(
        self,
        options: typing.Union[list, list[dict], None] = None,
        value: typing.Optional[typing.Any] = None,
        **kwargs: Unpack[TSelectProps],
    ):
        super().__init__("t-select")
        model_value = kwargs.pop("model_value", None)
        prefix_icon = kwargs.pop("prefix_icon", None)
        suffix_icon = kwargs.pop("suffix_icon", None)

        make_prefix_icon(self, prefix_icon)
        make_suffix_icon(self, suffix_icon)
        self.props({"options": options})
        try_setup_vmodel(self, value)

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

    def on_create(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "create",
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

    def on_remove(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "remove",
            handler,
            extends=extends,
        )
        return self

    def on_search(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "search",
            handler,
            extends=extends,
        )
        return self


class Option(BaseElement):
    def __init__(
        self,
        content: typing.Optional[str],
        **kwargs: Unpack[TOptionProps],
    ):
        super().__init__("t-option")

        if content is not None:
            with self:
                Content(content)

        self.props(handle_props(kwargs))  # type: ignore


class TSelectProps(TypedDict, total=False):
    model_value: typing.Any
    prefix_icon: str
    suffix_icon: str
    auto_width: bool
    autofocus: bool
    borderless: bool
    clearable: bool
    collapsed_items: str
    creatable: bool
    disabled: bool
    empty: str
    filter: str
    filterable: bool
    input_props: typing.Dict
    keys: typing.Dict
    label: str
    loading: bool
    loading_text: str
    max: float
    min_collapsed_num: float
    multiple: bool
    panel_bottom_content: str
    panel_top_content: str
    placeholder: str
    popup_props: typing.Dict
    popup_visible: bool
    default_popup_visible: bool
    readonly: bool
    reserve_keyword: bool
    scroll: typing.Dict
    select_input_props: typing.Dict
    show_arrow: bool
    size: typing.Literal["small", "medium", "large"]
    status: typing.Literal["default", "success", "warning", "error"]
    suffix: str
    tag_input_props: typing.Dict
    tag_props: typing.Dict
    tips: str
    default_value: typing.Literal["number"]
    value_display: str
    value_type: typing.Literal["value", "object"]
    on_blur: EventMixin
    on_change: EventMixin
    on_clear: EventMixin
    on_create: EventMixin
    on_enter: EventMixin
    on_focus: EventMixin
    on_input_change: EventMixin
    on_popup_visible_change: EventMixin
    on_remove: EventMixin
    on_search: EventMixin


class TOptionProps(TypedDict, total=False):
    check_all: bool
    disabled: bool
    label: str
    title: str
    value: typing.Union[bool, float, str]


class TOptionGroupProps(TypedDict, total=False):
    divider: bool
    label: str
