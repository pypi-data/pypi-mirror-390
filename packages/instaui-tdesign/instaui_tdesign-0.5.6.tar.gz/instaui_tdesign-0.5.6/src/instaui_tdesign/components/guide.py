from __future__ import annotations
import typing
from ._base_element import BaseElement
from instaui.event.event_mixin import EventMixin
from typing_extensions import TypedDict, Unpack
from ._utils import handle_props, handle_event_from_props, try_setup_vmodel


class Guide(BaseElement):
    def __init__(
        self,
        *,
        current: int,
        steps: typing.List[TGuideStepValue],
        **kwargs: Unpack[TGuideProps],
    ):
        super().__init__("t-guide")
        self.props({"steps": steps})
        try_setup_vmodel(self, current, prop_name="current")
        self.props(handle_props(kwargs))  # type: ignore
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

    def on_finish(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "finish",
            handler,
            extends=extends,
        )
        return self

    def on_next_step_click(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "next-step-click",
            handler,
            extends=extends,
        )
        return self

    def on_prev_step_click(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "prev-step-click",
            handler,
            extends=extends,
        )
        return self

    def on_skip(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "skip",
            handler,
            extends=extends,
        )
        return self


class TGuideProps(TypedDict, total=False):
    counter: str
    default_current: int
    finish_button_props: typing.Dict
    hide_counter: bool
    hide_prev: bool
    hide_skip: bool
    highlight_padding: float
    mode: typing.Literal["popup", "dialog"]
    next_button_props: typing.Dict
    prev_button_props: typing.Dict
    show_overlay: bool
    skip_button_props: typing.Dict
    z_index: float
    on_change: EventMixin
    on_finish: EventMixin
    on_next_step_click: EventMixin
    on_prev_step_click: EventMixin
    on_skip: EventMixin


class TGuideStepValue(TypedDict, total=False):
    body: str
    content: str
    element: str
    highlight_content: str
    highlight_padding: float
    mode: typing.Literal["popup", "dialog"]
    next_button_props: typing.Dict
    offset: typing.List
    placement: typing.Union[TStepPopupPlacement, TStepDialogPlacement]
    popup_props: typing.Dict
    prev_button_props: typing.Dict
    show_overlay: bool
    skip_button_props: typing.Dict
    step_overlay_class: str
    title: str


TStepPopupPlacement = typing.Literal[
    "top",
    "left",
    "right",
    "bottom",
    "top-left",
    "top-right",
    "bottom-left",
    "bottom-right",
    "left-top",
    "left-bottom",
    "right-top",
    "right-bottom",
]
TStepDialogPlacement = typing.Literal["top", "center"]
