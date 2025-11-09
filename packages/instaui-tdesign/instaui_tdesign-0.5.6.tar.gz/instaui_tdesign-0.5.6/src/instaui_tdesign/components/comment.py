from __future__ import annotations
import typing
from ._base_element import BaseElement
from typing_extensions import TypedDict, Unpack
from ._utils import handle_props


class Comment(BaseElement):
    def __init__(
        self,
        content: typing.Optional[str] = None,
        **kwargs: Unpack[TCommentProps],
    ):
        super().__init__("t-comment")

        self.props({"content": content})
        self.props(handle_props(kwargs))  # type: ignore


class TCommentProps(TypedDict, total=False):
    actions: typing.List
    author: str
    avatar: typing.Dict
    datetime: str
    quote: str
    reply: str
