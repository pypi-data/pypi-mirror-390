from __future__ import annotations
import typing
from ._base_element import BaseElement
from instaui.event.event_mixin import EventMixin
from typing_extensions import TypedDict, Unpack
from ._utils import handle_props, handle_event_from_props


class Calendar(BaseElement):
    def __init__(
        self,
        value: typing.Optional[typing.Union[str, typing.List[str]]] = None,
        **kwargs: Unpack[TCalendarProps],
    ):
        super().__init__("t-calendar")

        self.props({"value": value})
        self.props(handle_props(kwargs))  # type: ignore
        handle_event_from_props(self, kwargs)  # type: ignore

    def on_cell_click(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "cell-click",
            handler,
            extends=extends,
        )
        return self

    def on_cell_double_click(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "cell-double-click",
            handler,
            extends=extends,
        )
        return self

    def on_cell_right_click(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "cell-right-click",
            handler,
            extends=extends,
        )
        return self

    def on_controller_change(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "controller-change",
            handler,
            extends=extends,
        )
        return self

    def on_month_change(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "month-change",
            handler,
            extends=extends,
        )
        return self


class TCalendarProps(TypedDict, total=False):
    cell: str
    cell_append: str
    controller_config: typing.Union[bool, typing.Dict]
    fill_with_zero: bool
    first_day_of_week: float
    format: str
    head: str
    is_show_weekend_default: bool
    mode: typing.Literal["month", "year"]
    month: typing.Union[float, str]
    multiple: bool
    prevent_cell_contextmenu: bool
    range: typing.List
    theme: typing.Literal["full", "card"]
    week: typing.Union[str, typing.List]
    year: typing.Union[float, str]
    on_cell_click: EventMixin
    on_cell_double_click: EventMixin
    on_cell_right_click: EventMixin
    on_controller_change: EventMixin
    on_month_change: EventMixin
