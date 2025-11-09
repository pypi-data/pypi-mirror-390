from __future__ import annotations
import typing
from ._base_element import BaseElement
from typing_extensions import TypedDict, Unpack
from ._utils import handle_props, handle_event_from_props


class Card(BaseElement):
    def __init__(
        self,
        content: typing.Optional[str] = None,
        **kwargs: Unpack[TCardProps],
    ):
        super().__init__("t-card")

        self.props({"content": content})
        self.props(handle_props(kwargs))  # type: ignore
        handle_event_from_props(self, kwargs)  # type: ignore


class TCardProps(TypedDict, total=False):
    actions: str
    avatar: str
    bordered: bool
    body_style: typing.Dict
    cover: str
    description: str
    footer: str
    header: str
    header_bordered: bool
    hover_shadow: bool
    loading: typing.Union[bool, str]
    loading_props: typing.Dict
    shadow: bool
    size: typing.Literal["medium", "small"]
    status: str
    subtitle: str
    theme: typing.Literal["normal", "poster1", "poster2"]
    title: str
