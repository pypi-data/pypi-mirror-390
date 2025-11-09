from __future__ import annotations
import typing

from instaui_tdesign.components._icon_param_utils import make_icon_for_bool_or_str
from ._base_element import BaseElement
from instaui.event.event_mixin import EventMixin
from typing_extensions import TypedDict, Unpack
from ._utils import handle_props, handle_event_from_props, try_setup_vmodel


class Collapse(BaseElement):
    def __init__(
        self,
        value: typing.Optional[typing.List] = None,
        *,
        expand_icon: typing.Optional[typing.Union[bool, str]] = None,
        **kwargs: Unpack[TCollapseProps],
    ):
        super().__init__("t-collapse")
        try_setup_vmodel(self, value)

        make_icon_for_bool_or_str(self, "expandIcon", expand_icon)

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


class CollapsePanel(BaseElement):
    def __init__(
        self,
        header: typing.Optional[str] = None,
        **kwargs: Unpack[TCollapsePanelProps],
    ):
        super().__init__("t-collapse-panel")
        self.props(
            {
                "header": header,
            }
        )
        expand_icon = kwargs.pop("expand_icon", None)
        make_icon_for_bool_or_str(self, "expandIcon", expand_icon)
        self.props(handle_props(kwargs))  # type: ignore
        handle_event_from_props(self, kwargs)  # type: ignore


class TCollapseProps(TypedDict, total=False):
    borderless: bool
    default_expand_all: bool
    disabled: bool
    expand_icon_placement: typing.Literal["left", "right"]
    expand_mutex: bool
    expand_on_row_click: bool
    default_value: typing.List
    on_change: EventMixin


class TCollapsePanelProps(TypedDict, total=False):
    expand_icon: typing.Union[bool, str]
    content: str
    destroy_on_collapse: bool
    disabled: bool
    header_right_content: str
    value: typing.Union[int, str]
