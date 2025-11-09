from __future__ import annotations
import typing
from ._base_element import BaseElement
from instaui.event.event_mixin import EventMixin
from typing_extensions import TypedDict, Unpack
from ._utils import handle_props, handle_event_from_props, try_setup_vmodel


class Drawer(BaseElement):
    def __init__(
        self,
        visible: bool,
        *,
        header: typing.Optional[str] = None,
        body: typing.Optional[str] = None,
        **kwargs: Unpack[TDrawerProps],
    ):
        super().__init__("t-drawer")
        self.props({"header": header, "body": body})
        try_setup_vmodel(self, visible, prop_name="visible")
        self.props(handle_props(kwargs))  # type: ignore
        handle_event_from_props(self, kwargs)  # type: ignore

    def on_before_close(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "before-close",
            handler,
            extends=extends,
        )
        return self

    def on_before_open(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "before-open",
            handler,
            extends=extends,
        )
        return self

    def on_cancel(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "cancel",
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

    def on_close_btn_click(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "close-btn-click",
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

    def on_esc_keydown(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "esc-keydown",
            handler,
            extends=extends,
        )
        return self

    def on_overlay_click(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "overlay-click",
            handler,
            extends=extends,
        )
        return self

    def on_size_drag_end(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "size-drag-end",
            handler,
            extends=extends,
        )
        return self


class TDrawerProps(TypedDict, total=False):
    attach: str
    cancel_btn: typing.Union[str, typing.Dict]
    close_btn: typing.Literal["boolean"]
    close_on_esc_keydown: bool
    close_on_overlay_click: bool
    confirm_btn: typing.Dict
    destroy_on_close: bool
    drawer_class_name: str
    footer: typing.Union[bool, str]
    lazy: bool
    mode: typing.Literal["overlay", "push"]
    placement: typing.Literal["left", "right", "top", "bottom"]
    prevent_scroll_through: bool
    show_in_attached_element: bool
    show_overlay: bool
    size: str
    size_draggable: typing.Union[bool, typing.Dict]
    z_index: float
    on_before_close: EventMixin
    on_before_open: EventMixin
    on_cancel: EventMixin
    on_close: EventMixin
    on_close_btn_click: EventMixin
    on_confirm: EventMixin
    on_esc_keydown: EventMixin
    on_overlay_click: EventMixin
    on_size_drag_end: EventMixin
