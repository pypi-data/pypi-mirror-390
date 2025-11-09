from __future__ import annotations
import typing
from ._base_element import BaseElement
from instaui.event.event_mixin import EventMixin
from typing_extensions import TypedDict, Unpack
from ._utils import handle_props, handle_event_from_props, try_setup_vmodel

if typing.TYPE_CHECKING:
    from instaui.vars.types import TMaybeRef


class Dialog(BaseElement):
    def __init__(
        self,
        visible: bool,
        *,
        header: typing.Optional[str] = None,
        body: typing.Optional[str] = None,
        theme: typing.Optional[
            typing.Literal["default", "info", "warning", "danger", "success"]
        ] = None,
        **kwargs: Unpack[TDialogProps],
    ):
        super().__init__("t-dialog")

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

    def on_closed(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "closed",
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

    def on_opened(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "opened",
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


class TDialogCardProps(TypedDict, total=False):
    body: typing.Literal["TNode"]
    cancel_btn: typing.Literal["ButtonProps"]
    close_btn: typing.Literal["ButtonProps"]
    confirm_btn: typing.Literal["ButtonProps"]
    confirm_loading: bool
    footer: typing.Union[TMaybeRef[bool, str]]
    header: typing.Literal["boolean"]
    theme: typing.Literal["default", "info", "warning", "danger", "success"]
    on_cancel: EventMixin
    on_close_btn_click: EventMixin
    on_confirm: EventMixin


class TDialogProps(TypedDict, total=False):
    attach: str
    cancel_btn: typing.Literal["ButtonProps"]
    close_btn: typing.Literal["boolean"]
    close_on_esc_keydown: bool
    close_on_overlay_click: bool
    confirm_btn: typing.Literal["ButtonProps"]
    confirm_loading: bool
    confirm_on_enter: bool
    destroy_on_close: bool
    dialog_class_name: str
    dialog_style: typing.Dict
    draggable: bool
    footer: typing.Union[bool, str]
    lazy: bool
    mode: typing.Literal["modal", "modeless", "normal", "full-screen"]
    placement: typing.Literal["top", "center"]
    prevent_scroll_through: bool
    show_in_attached_element: bool
    show_overlay: bool
    top: typing.Union[float, str]
    width: typing.Union[float, str]
    z_index: float
    on_before_close: EventMixin
    on_before_open: EventMixin
    on_cancel: EventMixin
    on_close: EventMixin
    on_close_btn_click: EventMixin
    on_closed: EventMixin
    on_confirm: EventMixin
    on_esc_keydown: EventMixin
    on_opened: EventMixin
    on_overlay_click: EventMixin
