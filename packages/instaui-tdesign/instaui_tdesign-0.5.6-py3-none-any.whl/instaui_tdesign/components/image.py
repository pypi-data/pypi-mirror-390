from __future__ import annotations
import typing
from ._base_element import BaseElement
from instaui.event.event_mixin import EventMixin
from typing_extensions import TypedDict, Unpack
from ._utils import handle_props, handle_event_from_props

if typing.TYPE_CHECKING:
    from instaui.vars.types import TMaybeRef


class Image(BaseElement):
    def __init__(
        self,
        src: str,
        **kwargs: Unpack[TImageProps],
    ):
        super().__init__("t-image")
        self.props({"src": src})
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

    def on_load(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "load",
            handler,
            extends=extends,
        )
        return self


class TImageProps(TypedDict, total=False):
    alt: str
    error: str
    fallback: str
    fit: typing.Literal["contain", "cover", "fill", "none", "scale-down"]
    gallery: bool
    lazy: bool
    loading: str
    overlay_content: str
    overlay_trigger: typing.Literal["always", "hover"]
    placeholder: str
    position: str
    referrerpolicy: TMaybeRef[
        typing.Literal[
            "no-referrer",
            "no-referrer-when-downgrade",
            "origin",
            "origin-when-cross-origin",
            "same-origin",
            "strict-origin",
            "strict-origin-when-cross-origin",
            "unsafe-url",
        ]
    ]
    shape: typing.Literal["circle", "round", "square"]
    srcset: typing.Dict
    on_error: EventMixin
    on_load: EventMixin
