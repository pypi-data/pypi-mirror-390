from __future__ import annotations
import typing

from instaui_tdesign.components._icon_param_utils import make_icon_for_str
from ._base_element import BaseElement
from instaui.components.content import Content
from instaui.event.event_mixin import EventMixin
from typing_extensions import TypedDict, Unpack
from ._utils import handle_props, handle_event_from_props

if typing.TYPE_CHECKING:
    from instaui.vars.types import TMaybeRef


class Button(BaseElement):
    def __init__(
        self,
        content: typing.Optional[str] = None,
        **kwargs: Unpack[TButtonProps],
    ):
        """Create a button element.

        Args:
            content (Optional[str], optional): _description_. Defaults to None.
        """

        super().__init__("t-button")
        icon = kwargs.pop("icon", None)

        if content is not None:
            with self:
                Content(content)

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


class TButtonProps(TypedDict, total=False):
    icon: str
    block: bool
    disabled: bool
    form: str
    ghost: bool
    href: str
    loading: bool
    shape: typing.Literal["rectangle", "square", "round", "circle"]
    loading_props: typing.Dict
    size: typing.Literal["small", "medium", "large"]
    suffix: str
    tag: typing.Literal["button", "a", "div"]
    theme: TMaybeRef[
        typing.Literal["default", "primary", "danger", "warning", "success"]
    ]
    type: typing.Literal["submit", "reset", "button"]
    variant: typing.Literal["base", "outline", "dashed", "text"]
    on_click: EventMixin
