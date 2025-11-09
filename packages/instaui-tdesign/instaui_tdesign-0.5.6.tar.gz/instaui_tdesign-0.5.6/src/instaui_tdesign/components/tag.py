from __future__ import annotations
import typing

from instaui_tdesign.components._icon_param_utils import make_icon_for_str
from ._base_element import BaseElement
from instaui.event.event_mixin import EventMixin
from typing_extensions import TypedDict, Unpack
from ._utils import handle_props, handle_event_from_props

if typing.TYPE_CHECKING:
    from instaui.vars.types import TMaybeRef


class Tag(BaseElement):
    def __init__(
        self,
        content: typing.Optional[str] = None,
        *,
        icon: typing.Optional[str] = None,
        **kwargs: Unpack[TTagProps],
    ):
        super().__init__("t-tag")
        self.props({"content": content})

        make_icon_for_str(self, icon)
        self.props(handle_props(kwargs))  # type: ignore
        handle_event_from_props(self, kwargs)  # type: ignore

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


class TTagProps(TypedDict, total=False):
    closable: bool
    color: str
    disabled: bool
    max_width: typing.Union[float, str]
    shape: typing.Literal["square", "round", "mark"]
    size: typing.Literal["small", "medium", "large"]
    theme: TMaybeRef[
        typing.Literal["default", "primary", "warning", "danger", "success"]
    ]
    title: str
    variant: typing.Literal["dark", "light", "outline", "light-outline"]
    on_click: EventMixin
    on_close: EventMixin


class TCheckTagProps(TypedDict, total=False):
    checked: bool
    default_checked: bool
    checked_props: typing.Dict
    content: typing.Literal["number"]
    default: typing.Literal["TNode"]
    disabled: bool
    size: typing.Literal["small", "medium", "large"]
    unchecked_props: typing.Dict
    value: typing.Union[TMaybeRef[float, str]]
    on_change: EventMixin
    on_click: EventMixin


class TCheckTagGroupProps(TypedDict, total=False):
    checked_props: typing.Dict
    multiple: bool
    options: typing.List
    unchecked_props: typing.Dict
    value: typing.List
    default_value: typing.List
    on_change: EventMixin
