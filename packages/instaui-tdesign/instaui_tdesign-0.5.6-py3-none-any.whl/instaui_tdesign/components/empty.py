from __future__ import annotations
import typing
from ._base_element import BaseElement
from typing_extensions import TypedDict, Unpack
from ._utils import handle_props

if typing.TYPE_CHECKING:
    from instaui.vars.types import TMaybeRef


class Empty(BaseElement):
    def __init__(
        self,
        description: typing.Optional[str] = None,
        *,
        title: typing.Optional[str] = None,
        **kwargs: Unpack[TEmptyProps],
    ):
        super().__init__("t-empty")
        self.props({"description": description, "title": title})
        self.props(handle_props(kwargs))  # type: ignore

    def action_slot(self):
        return self.add_slot("action")


class TEmptyProps(TypedDict, total=False):
    image: typing.Dict
    image_style: typing.Dict
    size: typing.Literal["small", "medium", "large"]
    type: TMaybeRef[
        typing.Literal["empty", "success", "fail", "network-error", "maintenance"]
    ]
