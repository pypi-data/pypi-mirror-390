from __future__ import annotations
import typing
from instaui import custom
from ._base_element import BaseElement
from typing_extensions import TypedDict, Unpack
from ._utils import handle_props


class Descriptions(BaseElement):
    def __init__(
        self,
        **kwargs: Unpack[TDescriptionsProps],
    ):
        super().__init__("t-descriptions")
        custom.configure_slot_without_slot_prop(self, slot_names=["default"])
        self.props(handle_props(kwargs))  # type: ignore

    @classmethod  # type: ignore
    def from_dict(
        cls,
        data: dict[str, str],
        **kwargs: Unpack[TDescriptionsProps],  # type: ignore
    ) -> Descriptions:
        items = [{"content": v, "label": k} for k, v in data.items()]
        kwargs.pop("items", None)
        bordered = kwargs.pop("bordered", True)
        colon = kwargs.pop("colon", True)

        return cls(items=items, bordered=bordered, colon=colon, **kwargs)  # type: ignore


class DescriptionsItem(BaseElement):
    def __init__(
        self,
        content: typing.Optional[str] = None,
        **kwargs: Unpack[TDescriptionsItemProps],
    ):
        super().__init__("t-descriptions-item")
        self.props({"content": content})
        self.props(handle_props(kwargs))  # type: ignore


class TDescriptionsProps(TypedDict, total=False):
    bordered: bool
    colon: bool
    column: int
    content_style: typing.Dict
    item_layout: typing.Literal["horizontal", "vertical"]
    items: typing.List
    label_style: typing.Dict
    layout: typing.Literal["horizontal", "vertical"]
    size: typing.Literal["small", "medium", "large"]
    table_layout: typing.Literal["fixed", "auto"]
    title: str


class TDescriptionsItemProps(TypedDict, total=False):
    label: str
    span: int
