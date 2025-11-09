from typing import *
from fasthtml.common import *
from .row import Row
from .header import Header, HeaderRename

def apply_filters(data: List[List[Any]], colors: List[str], col_ids: list[str], filters: dict) -> Tuple[List[List[Any]], List[str]]:
    for col_id, excluded_values in filters.items():
        if not excluded_values: # Empty filter
            continue
        if col_id not in col_ids: # Error, should not happen
            print("Here, problem!!!!")
            continue

        col_idx = col_ids.index(col_id)
        colors = [color for row, color in zip(data, colors) if str(row[col_idx]) not in excluded_values]
        data = [row for row in data if str(row[col_idx]) not in excluded_values]

    return data, colors

def DataGrid(session, rename_col: str = None, wrapincontainer: bool = False, fullscreen: bool = False, swap: bool = False):
    """
    Note that fullscreen only work if the container is requested because it applies on the container
    """
    from __main__ import rTable, CONFIG

    if "datagrid" not in session:
        session["datagrid"] = dict()
    show_hidden = session.get("show_hidden", False)
    rows_selected = session["datagrid"].get("selected-rows") or []
    sort_by: Optional[str] = session["datagrid"].get("sort_by", None)
    sort_order: Optional[str] = session["datagrid"].get("sort_order", None)
    columns, col_ids, is_hparam, row_colors, data = rTable.get_results(show_hidden=show_hidden)
    # If the columns to sort by is hidden, we reset it
    if sort_by is not None and sort_by not in col_ids:
        session["datagrid"]["sort_by"] = sort_by = None
        session["datagrid"]["sort_order"] = sort_order = None

    filters = session["datagrid"].get("filters", {})
    # Apply filters
    data, row_colors = apply_filters(data, row_colors, col_ids, filters)
    if sort_by is not None and sort_order is not None:
        sort_idx = col_ids.index(sort_by)
        indices = sorted(
            range(len(data)),
            key=lambda i: (data[i][sort_idx] is None, data[i][sort_idx]),
            reverse=(sort_order == "desc")
        )

        # Reorder both lists using the sorted indices
        data = [data[i] for i in indices]
        row_colors = [row_colors[i] for i in indices]

    run_ids = [row[col_ids.index("run_id")] for row in data]
    rows_hidden = rTable.get_hidden_runs() if show_hidden else []
    table = Table(
                # We put the headers in a form so that we can sort them using htmx
                Thead(
                    Tr(
                        *[
                            HeaderRename(col_name, col_id) if col_id == rename_col else Header(
                                col_name,
                                col_id,
                                sort_order if col_id == sort_by else None,
                                has_filter=col_id in filters and len(filters[col_id]) > 0
                            )
                            for col_name, col_id in zip(columns, col_ids)],
                        id="column-header-row"
                    )
                    ),
                Tbody(
                    *[Row(row,
                          is_hparam,
                          run_id,
                          max_decimals=CONFIG.MAX_DEC,
                          selected=run_id in rows_selected,
                          hidden=run_id in rows_hidden,
                          color=color,
                          fullscreen=fullscreen) for row, run_id, color in zip(data, run_ids, row_colors)],
                ),
                cls="data-grid"
            ),

    if wrapincontainer:
        return Div(
                table,
                cls="scroll-container" if not fullscreen else "scroll-container fullscreen",
                id="experiment-table",
                hx_swap_oob="true" if swap else "false",
            ),
    else:
        return table