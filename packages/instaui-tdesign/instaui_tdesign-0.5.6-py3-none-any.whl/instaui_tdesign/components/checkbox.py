from __future__ import annotations
import typing
from ._base_element import BaseElement
from instaui.event.event_mixin import EventMixin
from typing_extensions import TypedDict, Unpack
from ._utils import handle_props, handle_event_from_props, try_setup_vmodel


class Checkbox(BaseElement):
    def __init__(
        self,
        checked: typing.Optional[bool] = None,
        *,
        label: typing.Optional[str] = None,
        checked_value: typing.Optional[bool] = None,
        **kwargs: Unpack[TCheckboxProps],
    ):
        super().__init__("t-checkbox")
        self.props({"label": label})

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


class CheckboxGroup(BaseElement):
    def __init__(
        self,
        options: typing.Optional[
            typing.List[typing.Union[str, TCheckboxOption]]
        ] = None,
        value: typing.Optional[typing.List[typing.Union[int, str, bool]]] = None,
        *,
        model_value: typing.Optional[typing.List[typing.Union[int, str, bool]]] = None,
        **kwargs: Unpack[TCheckboxGroupProps],
    ):
        super().__init__("t-checkbox-group")

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


class TCheckboxProps(TypedDict, total=False):
    check_all: bool
    default_checked: bool
    disabled: bool
    indeterminate: bool
    lazy_load: bool
    name: str
    readonly: bool
    title: str
    value: typing.Union[int, str, bool]
    on_change: EventMixin


class TCheckboxGroupProps(TypedDict, total=False):
    disabled: bool
    lazy_load: bool
    max: float
    name: str
    readonly: bool
    default_value: typing.List
    on_change: EventMixin


class TCheckboxOption(TypedDict, total=False):
    label: str
    checkAll: bool
    value: typing.Union[int, str]
