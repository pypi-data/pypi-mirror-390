from __future__ import annotations
import typing
from ._base_element import BaseElement
from typing_extensions import TypedDict, Unpack
from ._utils import handle_props


class Statistic(BaseElement):
    def __init__(
        self,
        *,
        title: typing.Optional[str] = None,
        value: typing.Optional[float] = None,
        unit: typing.Optional[str] = None,
        trend: typing.Optional[typing.Literal["increase", "decrease"]] = None,
        **kwargs: Unpack[TStatisticProps],
    ):
        super().__init__("t-statistic")
        self.props({"title": title, "value": value, "unit": unit, "trend": trend})
        self.props(handle_props(kwargs))  # type: ignore


class TStatisticProps(TypedDict, total=False):
    animation: typing.Dict
    animation_start: bool
    color: typing.Literal["black", "blue", "red", "orange", "green"]
    decimal_places: float
    extra: str
    format: str
    loading: bool
    prefix: str
    separator: str
    suffix: str
    trend_placement: typing.Literal["left", "right"]
