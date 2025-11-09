from __future__ import annotations
import typing
from ._base_element import BaseElement
from instaui.event.event_mixin import EventMixin
from typing_extensions import TypedDict, Unpack
from ._utils import handle_props, handle_event_from_props, try_setup_vmodel


class Swiper(BaseElement):
    def __init__(
        self,
        *,
        duration: typing.Optional[float] = None,
        interval: typing.Optional[float] = None,
        current: typing.Optional[int] = None,
        current_value: typing.Optional[int] = None,
        **kwargs: Unpack[TSwiperProps],
    ):
        super().__init__("t-swiper")
        self.props({"duration": duration, "interval": interval})
        try_setup_vmodel(self, current, prop_name="current")
        self.props(handle_props(kwargs, model_value=current_value))  # type: ignore
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


class SwiperItem(BaseElement):
    def __init__(
        self,
    ):
        super().__init__("t-swiper-item")


class TSwiperProps(TypedDict, total=False):
    animation: typing.Literal["slide", "fade"]
    autoplay: bool
    default_current: int
    direction: typing.Literal["horizontal", "vertical"]
    height: float
    loop: bool
    navigation: typing.Union[str, typing.Dict]
    stop_on_hover: bool
    theme: typing.Literal["light", "dark"]
    trigger: typing.Literal["hover", "click"]
    type: typing.Literal["default", "card"]
    card_scale: float
    on_change: EventMixin
