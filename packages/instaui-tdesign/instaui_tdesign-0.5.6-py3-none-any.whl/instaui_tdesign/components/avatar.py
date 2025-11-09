from __future__ import annotations
import typing

from instaui_tdesign.components._icon_param_utils import make_icon_for_str
from ._base_element import BaseElement
from instaui.event.event_mixin import EventMixin
from typing_extensions import TypedDict, Unpack
from ._utils import handle_props, handle_event_from_props


class Avatar(BaseElement):
    def __init__(
        self,
        **kwargs: Unpack[TAvatarProps],
    ):
        super().__init__("t-avatar")
        icon = kwargs.pop("icon", None)
        make_icon_for_str(self, icon)
        self.props(handle_props(kwargs))  # type: ignore
        handle_event_from_props(self, kwargs)  # type: ignore

    def on_error(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "error",
            handler,
            extends=extends,
        )
        return self


class AvatarGroup(BaseElement):
    def __init__(
        self,
        **kwargs: Unpack[TAvatarGroupProps],
    ):
        super().__init__("t-avatar-group")

        self.props(handle_props(kwargs))  # type: ignore


class TAvatarProps(TypedDict, total=False):
    icon: str
    alt: str
    content: str
    hide_on_load_failed: bool
    image: str
    image_props: typing.Dict
    shape: typing.Literal["circle", "round"]
    size: typing.Literal["small", "medium", "large", "24px", "38px"]
    on_error: EventMixin


class TAvatarGroupProps(TypedDict, total=False):
    cascading: typing.Literal["left-up", "right-up"]
    collapse_avatar: str
    max: float
    popup_props: typing.Dict
    size: typing.Literal["small", "medium", "large", "24px", "38px"]
