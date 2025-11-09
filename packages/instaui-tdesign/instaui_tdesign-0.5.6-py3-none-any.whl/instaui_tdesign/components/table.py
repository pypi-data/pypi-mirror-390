from __future__ import annotations
import typing
from instaui.components.slot import Slot

from instaui_tdesign.components._icon_param_utils import (
    make_icon_for_bool_or_str,
    make_icon_for_str,
)
from ._base_element import BaseElement
from instaui.event.event_mixin import EventMixin
from typing_extensions import TypedDict, Unpack, Self
from instaui.common.binding_track_mixin import is_binding_tracker
from ._utils import handle_props, handle_event_from_props

if typing.TYPE_CHECKING:
    from instaui.vars.types import TMaybeRef

# region pandas protocol


@typing.runtime_checkable
class PandasDataFrameProtocol(typing.Protocol):
    def to_dict(self, orient: typing.Any) -> list: ...

    @property
    def columns(self) -> typing.Iterable: ...


# endregion


# region polars protocol


@typing.runtime_checkable
class PolarsDataFrameProtocol(typing.Protocol):
    @property
    def columns(self) -> list[str]: ...

    def to_dicts(self) -> list: ...


# endregion


class BaseTable(BaseElement):
    def __init__(
        self,
        data: typing.Union[
            list,
            PandasDataFrameProtocol,
            PolarsDataFrameProtocol,
            None,
        ] = None,
        columns: typing.Optional[list[TBaseTableCol]] = None,
        row_key: typing.Optional[str] = None,
        **kwargs: Unpack[TBaseTableProps],
    ):
        super().__init__("t-base-table")
        _common_table_props_update(kwargs)  # type: ignore
        if isinstance(data, PolarsDataFrameProtocol):
            data = _polars_to_data(data)
        elif isinstance(data, PandasDataFrameProtocol):
            data = _pandas_to_data(data)

        self.props({"data": data, "columns": columns, "row-key": row_key})

        self.props(handle_props(kwargs))  # type: ignore
        handle_event_from_props(self, kwargs)  # type: ignore

    def on_active_change(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[list] = None,
    ):
        self.on(
            "active-change",
            handler,
            extends=extends,
        )
        return self

    def on_active_row_action(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[list] = None,
    ):
        self.on(
            "active-row-action",
            handler,
            extends=extends,
        )
        return self

    def on_cell_click(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[list] = None,
    ):
        self.on(
            "cell-click",
            handler,
            extends=extends,
        )
        return self

    def on_column_resize_change(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[list] = None,
    ):
        self.on(
            "column-resize-change",
            handler,
            extends=extends,
        )
        return self

    def on_page_change(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[list] = None,
    ):
        self.on(
            "page-change",
            handler,
            extends=extends,
        )
        return self

    def on_row_click(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[list] = None,
    ):
        self.on(
            "row-click",
            handler,
            extends=extends,
        )
        return self

    def on_row_dblclick(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[list] = None,
    ):
        self.on(
            "row-dblclick",
            handler,
            extends=extends,
        )
        return self

    def on_row_mousedown(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[list] = None,
    ):
        self.on(
            "row-mousedown",
            handler,
            extends=extends,
        )
        return self

    def on_row_mouseenter(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[list] = None,
    ):
        self.on(
            "row-mouseenter",
            handler,
            extends=extends,
        )
        return self

    def on_row_mouseleave(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[list] = None,
    ):
        self.on(
            "row-mouseleave",
            handler,
            extends=extends,
        )
        return self

    def on_row_mouseover(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[list] = None,
    ):
        self.on(
            "row-mouseover",
            handler,
            extends=extends,
        )
        return self

    def on_row_mouseup(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[list] = None,
    ):
        self.on(
            "row-mouseup",
            handler,
            extends=extends,
        )
        return self

    def on_scroll(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[list] = None,
    ):
        self.on(
            "scroll",
            handler,
            extends=extends,
        )
        return self

    def on_scroll_x(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[list] = None,
    ):
        self.on(
            "scroll-x",
            handler,
            extends=extends,
        )
        return self

    def on_scroll_y(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[list] = None,
    ):
        self.on(
            "scroll-y",
            handler,
            extends=extends,
        )
        return self


class Table(BaseElement):
    def __init__(
        self,
        data: typing.Union[
            list,
            PandasDataFrameProtocol,
            PolarsDataFrameProtocol,
            None,
        ] = None,
        columns: typing.Optional[
            typing.Sequence[typing.Union[TPrimaryTableCol, dict]]
        ] = None,
        extra_columns: typing.Optional[
            typing.Sequence[typing.Union[TPrimaryTableCol, dict]]
        ] = None,
        row_key: typing.Optional[str] = None,
        **kwargs: Unpack[TPrimaryTableProps],
    ):
        """Initialize a Table component for displaying and interacting with tabular data.

        Args:
            data (Union[list, PandasDataFrameProtocol, PolarsDataFrameProtocol, None]):
                Table data source. Can be:
                - List of dictionaries
                - Pandas DataFrame
                - Polars DataFrame
                - None for empty table
            columns (Optional[Sequence[Union[TPrimaryTableCol, dict]]]):
                Column definitions. Each column can be a TPrimaryTableCol or dict.
                If None, columns will be inferred from data.
            extra_columns (Optional[Sequence[Union[TPrimaryTableCol, dict]]]):
                Additional columns to be displayed.
            row_key (Optional[str]):
                Unique key field name for each row. Required for row operations.
            **kwargs: Additional table props from TPrimaryTableProps.

        Example:
        .. code-block:: python
            # Basic table with list data
            data = [{"name": "foo", "value": 1}, {"name": "bar", "value": 2}]
            td.table(data, row_key="name")

            # Table with custom columns
            columns = [{"colKey": "name", "label": "Name"}, {"colKey": "value", "label": "Value"}]
            td.table(data, columns=columns, row_key="name")

            # Table from pandas DataFrame
            import pandas as pd
            df = pd.DataFrame({"name": ["foo", "bar"], "value": [1, 2]})
            td.table(df, row_key="name")

            # Table with cell slot
            data = [
                {"name": "foo"},
            ]

            with td.table(data).add_cell_slot("name") as slot:
                td.button("Click me").on_click(
                    td.notify_plugin.info(content=ui.str_format("Clicked {0}", slot.current))
                )
        """
        super().__init__("t-table")
        expand_icon = kwargs.pop("expand_icon", None)
        filter_icon = kwargs.pop("filter_icon", None)
        sort_icon = kwargs.pop("sort_icon", None)

        _common_table_props_update(kwargs)  # type: ignore
        if isinstance(data, PolarsDataFrameProtocol):
            data = _polars_to_data(data)
        elif isinstance(data, PandasDataFrameProtocol):
            data = _pandas_to_data(data)
        self.props(
            {
                "data": data,
                "columns": columns,
                "row-key": row_key,
                "extraColumns": extra_columns,
            }
        )
        make_icon_for_bool_or_str(self, "expandIcon", expand_icon)
        make_icon_for_str(self, filter_icon, slot_name="filterIcon")
        make_icon_for_str(self, sort_icon, slot_name="sortIcon")
        self.props(handle_props(kwargs))  # type: ignore
        handle_event_from_props(self, kwargs)  # type: ignore

    def add_header_slot(self, name: str):
        """
        Add a header slot to the table.

        Args:
            name (str): The name key to add the slot to.
        """
        return TableHeaderSlot(self.add_slot(f"header-cell-{name}"))

    def add_cell_slot(self, name: str):
        """
        Add a cell slot to the table.

        Args:
            name (str): The name key to add the slot to.
        """
        return TableCellSlot(self.add_slot(f"body-cell-{name}"))

    def on_async_loading_click(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[list] = None,
    ):
        self.on(
            "async-loading-click",
            handler,
            extends=extends,
        )
        return self

    @classmethod
    def from_pandas(
        cls,
        data: typing.Union[PandasDataFrameProtocol, dict],
        *,
        extra_columns: typing.Optional[
            dict[str, typing.Union[dict, typing.Callable[[str], dict]]]
        ] = None,
        **kwargs: Unpack[TPrimaryTableProps],
    ) -> Self:
        if isinstance(data, PandasDataFrameProtocol):
            extra_columns = extra_columns or {}
            columns = []

            for col in data.columns:
                extra = extra_columns.get(col, {})
                if callable(extra):
                    extra = extra(col)
                columns.append({"colKey": col, "label": col} | extra)

            return cls(data=data.to_dict(orient="records"), columns=columns, **kwargs)  # type: ignore

        if is_binding_tracker(data) or isinstance(data, dict):
            return cls(data=data["data"], columns=data["columns"], **kwargs)

        raise ValueError("Unsupported data type")

    @classmethod
    def from_polars(
        cls,
        data: typing.Union[PolarsDataFrameProtocol, dict],
        *,
        extra_columns: typing.Optional[
            dict[str, typing.Union[dict, typing.Callable[[str], dict]]]
        ] = None,
        **kwargs: Unpack[TPrimaryTableProps],
    ) -> Self:
        if isinstance(data, PolarsDataFrameProtocol):
            extra_columns = extra_columns or {}
            columns = []

            for col in data.columns:
                extra = extra_columns.get(col, {})
                if callable(extra):
                    extra = extra(col)
                columns.append({"colKey": col, "label": col} | extra)

            return cls(data=data.to_dicts(), columns=columns, **kwargs)  # type: ignore

        if is_binding_tracker(data) or isinstance(data, dict):
            return cls(data=data["data"], columns=data["columns"], **kwargs)

        raise ValueError("Unsupported data type")

    def on_cell_click(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[list] = None,
    ):
        self.on(
            "cell-click",
            handler,
            extends=extends,
        )
        return self

    def on_change(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[list] = None,
    ):
        self.on(
            "change",
            handler,
            extends=extends,
        )
        return self

    def on_column_change(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[list] = None,
    ):
        self.on(
            "column-change",
            handler,
            extends=extends,
        )
        return self

    def on_column_controller_visible_change(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[list] = None,
    ):
        self.on(
            "column-controller-visible-change",
            handler,
            extends=extends,
        )
        return self

    def on_data_change(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[list] = None,
    ):
        self.on(
            "data-change",
            handler,
            extends=extends,
        )
        return self

    def on_display_columns_change(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[list] = None,
    ):
        self.on(
            "display-columns-change",
            handler,
            extends=extends,
        )
        return self

    def on_drag_sort(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[list] = None,
    ):
        self.on(
            "drag-sort",
            handler,
            extends=extends,
        )
        return self

    def on_expand_change(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[list] = None,
    ):
        self.on(
            "expand-change",
            handler,
            extends=extends,
        )
        return self

    def on_filter_change(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[list] = None,
    ):
        self.on(
            "filter-change",
            handler,
            extends=extends,
        )
        return self

    def on_row_edit(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[list] = None,
    ):
        self.on(
            "row-edit",
            handler,
            extends=extends,
        )
        return self

    def on_row_validate(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[list] = None,
    ):
        self.on(
            "row-validate",
            handler,
            extends=extends,
        )
        return self

    def on_select_change(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[list] = None,
    ):
        self.on(
            "select-change",
            handler,
            extends=extends,
        )
        return self

    def on_sort_change(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[list] = None,
    ):
        self.on(
            "sort-change",
            handler,
            extends=extends,
        )
        return self

    def on_validate(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[list] = None,
    ):
        self.on(
            "validate",
            handler,
            extends=extends,
        )
        return self


class EnhancedTable(BaseElement):
    def __init__(
        self,
        data: typing.Optional[list] = None,
        columns: typing.Optional[list[TPrimaryTableCol]] = None,
        row_key: typing.Optional[str] = None,
        *,
        tree_expand_and_fold_icon: typing.Union[str, None] = None,
        **kwargs: Unpack[TEnhancedTableProps],
    ):
        super().__init__("t-enhanced-table")
        self.props({"data": data, "columns": columns, "row-key": row_key})
        make_icon_for_str(
            self, tree_expand_and_fold_icon, slot_name="treeExpandAndFoldIcon"
        )
        self.props(handle_props(kwargs))  # type: ignore
        handle_event_from_props(self, kwargs)  # type: ignore


class TBaseTableProps(TypedDict, total=False):
    active_row_keys: list
    default_active_row_keys: list
    active_row_type: str
    allow_resize_column_width: bool
    attach: str
    bordered: bool
    bottom_content: typing.Literal["TNode"]
    cell_empty_content: typing.Literal["TNode"]
    disable_data_page: bool
    disable_space_inactive_row: bool
    empty: typing.Literal["TNode"]
    first_full_row: typing.Literal["TNode"]
    fixed_rows: list
    foot_data: list
    footer_affix_props: dict
    footer_affixed_bottom: TMaybeRef[typing.Union[bool, dict]]
    footer_summary: typing.Literal["TNode"]
    header_affix_props: dict
    header_affixed_top: typing.Union[bool, dict]
    height: typing.Union[float, str]
    horizontal_scroll_affixed_bottom: TMaybeRef[typing.Union[bool, dict]]
    hover: bool
    keyboard_row_hover: bool
    last_full_row: typing.Literal["TNode"]
    lazy_load: bool
    loading: typing.Union[bool, str]
    loading_props: dict
    locale: dict
    max_height: typing.Union[float, str]
    pagination: typing.Union[dict, bool, int]
    pagination_affixed_bottom: typing.Union[bool, dict]
    resizable: bool
    row_attributes: typing.Union[str, dict, list]
    row_class_name: typing.Union[str, dict, list]
    rowspan_and_colspan: str
    rowspan_and_colspan_in_footer: str
    scroll: dict
    show_header: bool
    size: typing.Literal["small", "medium", "large"]
    stripe: bool
    table_content_width: str
    table_layout: typing.Literal["auto", "fixed"]
    top_content: typing.Literal["TNode"]
    vertical_align: typing.Literal["top", "middle", "bottom"]
    on_active_change: EventMixin
    on_active_row_action: EventMixin
    on_cell_click: EventMixin
    on_column_resize_change: EventMixin
    on_page_change: EventMixin
    on_row_click: EventMixin
    on_row_dblclick: EventMixin
    on_row_mousedown: EventMixin
    on_row_mouseenter: EventMixin
    on_row_mouseleave: EventMixin
    on_row_mouseover: EventMixin
    on_row_mouseup: EventMixin
    on_scroll: EventMixin
    on_scroll_x: EventMixin
    on_scroll_y: EventMixin


class TBaseTableCol(TypedDict, total=False):
    align: typing.Literal["left", "right", "center"]
    attrs: typing.Union[str, dict]
    cell: str
    children: list
    class_name: typing.Union[str, list, dict]
    col_key: str
    colspan: float
    ellipsis: typing.Union[bool, str, dict]
    ellipsis_title: typing.Union[bool, str, dict]
    fixed: typing.Literal["left", "right"]
    foot: str
    min_width: typing.Union[float, str]
    render: str
    resizable: bool
    resize: dict
    stop_propagation: bool
    th_class_name: typing.Union[str, list, dict]
    title: str
    width: typing.Union[float, str]


class TPrimaryTableProps(TBaseTableProps, total=False):
    expand_icon: typing.Union[str, bool]
    filter_icon: str
    sort_icon: str
    async_loading: str
    column_controller: dict
    column_controller_visible: bool
    display_columns: list
    default_display_columns: list
    drag_sort: TMaybeRef[
        typing.Literal["row", "row-handler", "col", "row-handler-col", "drag-col"]
    ]
    drag_sort_options: dict
    editable_cell_state: str
    editable_row_keys: list
    expand_on_row_click: bool
    expanded_row: TBaseTableCol
    expanded_row_keys: list
    default_expanded_row_keys: list
    filter_row: typing.Literal["TNode"]
    filter_value: dict
    default_filter_value: dict
    hide_sort_tips: bool
    indeterminate_selected_row_keys: list
    multiple_sort: bool
    reserve_selected_row_on_paginate: bool
    row_selection_allow_uncheck: bool
    row_selection_type: typing.Literal["single", "multiple"]
    select_on_row_click: bool
    selected_row_keys: list
    default_selected_row_keys: list
    show_sort_column_bg_color: bool
    sort: typing.Union[dict, list]
    default_sort: TMaybeRef[typing.Union[dict, list]]
    sort_on_row_draggable: bool
    on_async_loading_click: EventMixin
    on_cell_click: EventMixin
    on_change: EventMixin
    on_column_change: EventMixin
    on_column_controller_visible_change: EventMixin
    on_data_change: EventMixin
    on_display_columns_change: EventMixin
    on_drag_sort: EventMixin
    on_expand_change: EventMixin
    on_filter_change: EventMixin
    on_row_edit: EventMixin
    on_row_validate: EventMixin
    on_select_change: EventMixin
    on_sort_change: EventMixin
    on_validate: EventMixin


class TPrimaryTableCol(TBaseTableCol):
    cell: str
    check_props: typing.Union[str, dict]
    children: list
    colKey: str
    disabled: str
    edit: dict
    filter: dict
    # render: str
    sortType: typing.Literal["desc", "asc", "all"]
    sorter: typing.Union[bool, str]
    title: str
    type: typing.Literal["single", "multiple"]


class TEnhancedTableProps(TPrimaryTableCol):
    before_drag_sort: str
    expanded_tree_nodes: list
    default_expanded_tree_nodes: list
    tree: dict
    on_abnormal_drag_sort: EventMixin
    on_expanded_tree_nodes_change: EventMixin
    on_tree_expand_change: EventMixin


class TableCellSlot:
    def __init__(self, slot: Slot) -> None:
        self.__slot = slot

    def __enter__(self):
        self.__slot.__enter__()
        return self

    def __exit__(self, *exc_info):
        self.__slot.__exit__(*exc_info)

    def param(self, name: typing.Literal["col", "colIndex", "row", "rowIndex"]):
        """
        Get slot parameter by name.

        Args:
            name (typing.Literal[&quot;col&quot;, &quot;colIndex&quot;, &quot;row&quot;, &quot;rowIndex&quot;]): Slot parameter name.
        """
        return typing.cast(typing.Any, self.__slot.slot_props(name))

    @property
    def current(self) -> typing.Any:
        """
        Get current cell value.
        """
        return self.__slot.slot_props("currentValue")


class TableHeaderSlot:
    def __init__(self, slot: Slot) -> None:
        self.__slot = slot

    def __enter__(self):
        self.__slot.__enter__()
        return self

    def __exit__(self, *exc_info):
        self.__slot.__exit__(*exc_info)

    def param(self, name: typing.Literal["col", "colIndex"]):
        """
        Get slot parameter by name.

        Args:
            name (typing.Literal[&quot;col&quot;, &quot;colIndex&quot;]): Slot parameter name.
        """
        return typing.cast(typing.Any, self.__slot.slot_props(name))


def _common_table_props_update(props: dict):
    pass
    # if props.get("pagination") is True:
    #     props.update({"pagination": {"defaultCurrent": 1, "defaultPageSize": 10}})


def _pandas_to_data(dataframe: PandasDataFrameProtocol) -> list:
    return dataframe.to_dict(orient="records")


def _polars_to_data(dataframe: PolarsDataFrameProtocol) -> list:
    return dataframe.to_dicts()
