from __future__ import annotations
import typing
from ._base_element import BaseElement
from instaui.event.event_mixin import EventMixin
from typing_extensions import TypedDict, Unpack
from ._utils import handle_props, handle_event_from_props, try_setup_vmodel

if typing.TYPE_CHECKING:
    from instaui.vars.types import TMaybeRef


class TimePicker(BaseElement):
    def __init__(
        self,
        value: typing.Optional[str] = None,
        *,
        model_value: typing.Optional[str] = None,
        **kwargs: Unpack[TTimePickerProps],
    ):
        super().__init__("t-time-picker")

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

    def on_close(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "close",
            handler,
            extends=extends,
        )
        return self

    def on_confirm(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "confirm",
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

    def on_input(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "input",
            handler,
            extends=extends,
        )
        return self

    def on_open(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "open",
            handler,
            extends=extends,
        )
        return self

    def on_pick(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "pick",
            handler,
            extends=extends,
        )
        return self


class TimeRangePicker(BaseElement):
    def __init__(
        self,
        value: typing.Optional[typing.List] = None,
        *,
        model_value: typing.Optional[typing.List] = None,
        **kwargs: Unpack[TTimeRangePickerProps],
    ):
        super().__init__("t-time-range-picker")

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

    def on_input(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "input",
            handler,
            extends=extends,
        )
        return self

    def on_pick(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "pick",
            handler,
            extends=extends,
        )
        return self


class TTimePickerProps(TypedDict, total=False):
    allow_input: bool
    borderless: bool
    clearable: bool
    disable_time: str
    disabled: bool
    format: str
    hide_disabled_time: bool
    input_props: typing.Dict
    label: str
    placeholder: str
    popup_props: typing.Dict
    presets: typing.Dict
    readonly: bool
    select_input_props: typing.Dict
    size: typing.Literal["small", "medium", "large"]
    status: typing.Literal["default", "success", "warning", "error"]
    steps: typing.List
    tips: str
    default_value: str
    value_display: str
    on_blur: EventMixin
    on_change: EventMixin
    on_clear: EventMixin
    on_close: EventMixin
    on_confirm: EventMixin
    on_focus: EventMixin
    on_input: EventMixin
    on_open: EventMixin
    on_pick: EventMixin


class TTimeRangePickerProps(TypedDict, total=False):
    allow_input: bool
    auto_swap: bool
    borderless: bool
    clearable: bool
    disable_time: str
    disabled: typing.Union[TMaybeRef[bool, typing.List]]
    format: str
    hide_disabled_time: bool
    label: typing.Literal["TNode"]
    placeholder: typing.Literal["Array"]
    popup_props: typing.Dict
    presets: typing.Dict
    range_input_props: typing.Dict
    size: typing.Literal["small", "medium", "large"]
    status: typing.Literal["default", "success", "warning", "error"]
    steps: typing.List
    tips: typing.Literal["TNode"]
    default_value: typing.List
    on_blur: EventMixin
    on_change: EventMixin
    on_focus: EventMixin
    on_input: EventMixin
    on_pick: EventMixin
