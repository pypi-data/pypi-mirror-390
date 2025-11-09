from __future__ import annotations
import typing
from ._base_element import BaseElement
from instaui.event.event_mixin import EventMixin
from typing_extensions import TypedDict, Unpack
from ._utils import handle_props, handle_event_from_props, try_setup_vmodel


class Textarea(BaseElement):
    def __init__(
        self,
        value: typing.Optional[str] = None,
        *,
        model_value: typing.Optional[str] = None,
        **kwargs: Unpack[TTextareaProps],
    ):
        super().__init__("t-textarea")

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

    def on_keydown(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "keydown",
            handler,
            extends=extends,
        )
        return self

    def on_keypress(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "keypress",
            handler,
            extends=extends,
        )
        return self

    def on_keyup(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "keyup",
            handler,
            extends=extends,
        )
        return self

    def on_validate(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "validate",
            handler,
            extends=extends,
        )
        return self


class TTextareaProps(TypedDict, total=False):
    allow_input_over_max: bool
    autofocus: bool
    autosize: typing.Union[bool, typing.Dict]
    disabled: bool
    maxcharacter: float
    maxlength: int
    name: str
    placeholder: str
    readonly: bool
    status: typing.Literal["default", "success", "warning", "error"]
    tips: str
    default_value: str
    on_blur: EventMixin
    on_change: EventMixin
    on_focus: EventMixin
    on_keydown: EventMixin
    on_keypress: EventMixin
    on_keyup: EventMixin
    on_validate: EventMixin
