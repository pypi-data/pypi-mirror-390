from __future__ import annotations
import typing
from ._base_element import BaseElement
from instaui.event.event_mixin import EventMixin
from typing_extensions import TypedDict, Unpack

from ._utils import handle_props, handle_event_from_props, try_setup_vmodel


class Radio(BaseElement):
    def __init__(
        self,
        checked: typing.Optional[bool] = None,
        **kwargs: Unpack[TRadioProps],
    ):
        super().__init__("t-radio")
        allow_uncheck = kwargs.pop("allow_uncheck", None)
        checked_value = kwargs.pop("checked_value", None)

        self.props({"allow-uncheck": allow_uncheck})
        try_setup_vmodel(self, checked)

        self.props(handle_props(kwargs, model_value=checked_value))  # type: ignore
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


class RadioGroup(BaseElement):
    def __init__(
        self,
        options: typing.Optional[
            typing.Sequence[typing.Union[str, int, bool, dict]]
        ] = None,
        value: typing.Optional[typing.Union[bool, int, str]] = None,
        **kwargs: Unpack[TRadioGroupProps],
    ):
        super().__init__("t-radio-group")
        model_value = kwargs.pop("model_value", None)
        self.props({"options": options})
        try_setup_vmodel(self, value)
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


class TRadioProps(TypedDict, total=False):
    checked_value: bool
    allow_uncheck: bool
    default_checked: bool
    disabled: bool
    label: str
    name: str
    readonly: bool
    value: typing.Union[bool, float, str]
    on_change: EventMixin
    on_click: EventMixin


class TRadioGroupProps(TypedDict, total=False):
    model_value: typing.Union[bool, int, str]
    allow_uncheck: bool
    disabled: bool
    name: str
    readonly: bool
    size: typing.Literal["small", "medium", "large"]
    theme: typing.Literal["radio", "button"]
    default_value: typing.Union[bool, int, str]
    variant: typing.Literal["outline", "primary-filled", "default-filled"]
    on_change: EventMixin
