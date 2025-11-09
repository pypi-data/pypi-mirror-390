from __future__ import annotations
import typing
from ._base_element import BaseElement
from instaui.event.event_mixin import EventMixin
from typing_extensions import TypedDict, Unpack
from ._utils import handle_props, handle_event_from_props

if typing.TYPE_CHECKING:
    from instaui.vars.types import TMaybeRef


class Timeline(BaseElement):
    def __init__(
        self,
        **kwargs: Unpack[TTimelineProps],
    ):
        super().__init__("t-timeline")
        self.props(handle_props(kwargs))  # type: ignore


class TimelineItem(BaseElement):
    def __init__(
        self,
        content: typing.Optional[str] = None,
        *,
        label: typing.Optional[str] = None,
        label_align: typing.Optional[
            typing.Literal["left", "right", "top", "bottom"]
        ] = None,
        **kwargs: Unpack[TTimelineItemProps],
    ):
        super().__init__("t-timeline")
        self.props({"content": content, "label": label, "label-align": label_align})
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


class TTimelineProps(TypedDict, total=False):
    label_align: TMaybeRef[
        typing.Literal["left", "right", "alternate", "top", "bottom"]
    ]
    layout: typing.Literal["horizontal", "vertical"]
    mode: typing.Literal["alternate", "same"]
    reverse: bool
    theme: typing.Literal["default", "dot"]


class TTimelineItemProps(TypedDict, total=False):
    dot: str
    dot_color: str
    loading: bool
    on_click: EventMixin
