from __future__ import annotations
import typing
from ._base_element import BaseElement
from instaui.event.event_mixin import EventMixin
from typing_extensions import TypedDict, Unpack
from ._utils import handle_props, handle_event_from_props, try_setup_vmodel

if typing.TYPE_CHECKING:
    from instaui.vars.types import TMaybeRef


class Transfer(BaseElement):
    def __init__(
        self,
        value: typing.Optional[typing.List] = None,
        *,
        model_value: typing.Optional[typing.List] = None,
        **kwargs: Unpack[TTransferProps],
    ):
        super().__init__("t-transfer")

        try_setup_vmodel(self, value)

        self.props(handle_props(kwargs, model_value=model_value))  # type: ignore
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

    def on_checked_change(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "checked-change",
            handler,
            extends=extends,
        )
        return self

    def on_page_change(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "page-change",
            handler,
            extends=extends,
        )
        return self

    def on_scroll(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "scroll",
            handler,
            extends=extends,
        )
        return self

    def on_search(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "search",
            handler,
            extends=extends,
        )
        return self


class TTransferProps(TypedDict, total=False):
    checkbox_props: typing.Dict
    checked: typing.List
    data: typing.List
    direction: typing.Literal["left", "right", "both"]
    disabled: typing.Union[bool, typing.List]
    empty: str
    footer: typing.Union[bool, typing.List]
    keys: typing.Dict
    operation: typing.Union[bool, typing.List]
    pagination: typing.Union[TMaybeRef[typing.Dict, typing.List]]
    search: TMaybeRef[typing.Union[bool, typing.Dict, typing.List]]
    show_check_all: typing.Union[TMaybeRef[bool, typing.List]]
    target_draggable: bool
    target_sort: typing.Literal["original", "push", "unshift"]
    title: typing.Union[bool, typing.List]
    transfer_item: str
    tree: str
    default_value: typing.List
    on_change: EventMixin
    on_checked_change: EventMixin
    on_page_change: EventMixin
    on_scroll: EventMixin
    on_search: EventMixin
