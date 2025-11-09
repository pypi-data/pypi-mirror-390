from typing import *
from fasthtml.common import *

def right_click_handler(session, elementIds: List[str], top: int, left: int):
    from __main__ import rTable
    elementId = [elem for elem in elementIds if elem.startswith("grid-header-")][0]
    clicked_col = elementId.replace("grid-header-", "")
    hidden_columns = [(key, alias) for key, (order, alias, _) in rTable.result_columns.items() if order is None]
    filters = session.get("datagrid", {}).get("filters", {})
    return Div(
        Ul(
            Li('Hide', hx_get=f"/hide?col={clicked_col}", hx_target='#experiment-table', hx_swap="innerHTML", cls="menu-item"),
            Li('Rename', hx_get=f'/rename_col_datagrid?col={clicked_col}', hx_target='#experiment-table', hx_swap="innerHTML", cls="menu-item"),
            Li(I(cls="fa fa-filter", style="margin-right: 5px"), 'Quick Filter', hx_get=f'/filter_col_datagrid?colid={clicked_col}', hx_target='#windowed-modal',
               hx_swap="outerHTML", cls="menu-item"),
            Li(I(cls="fa-solid fa-filter-circle-xmark", style="margin-right: 5px"), 'Clear Filter',
               hx_get=f'/filter_clear?colid={clicked_col}', hx_target='#experiment-table',
               hx_swap="innerHTML", cls="menu-item") if clicked_col in filters and len(filters[clicked_col]) > 0 else None,
            Li(
                Div(A('Add', href="#", cls="has-submenu"), Span("►"),
                    style="display: flex; flex-direction: row; justify-content: space-between;"),
                Ul(
                    *[Li(alias, hx_get=f"/show?col={col_name}&after={clicked_col}", hx_target='#experiment-table', hx_swap="innerHTML", cls="menu-item")
                      for col_name, alias in hidden_columns],
                    cls="submenu"
                ),
                cls="menu-item has-submenu-wrapper"
            ),
            cls='dropdown-menu'
        ),
        id='custom-menu',
        style=f'visibility: visible; top: {top}px; left: {left}px;',
    )
def right_click_handler_row(session, elementIds: List[str], top: int, left: int):
    from __main__ import rTable
    elementId = [elem for elem in elementIds if elem.startswith("grid-row-")][0]
    clicked_row = int(elementId.replace("grid-row-", ""))
    hidden_runs = rTable.get_hidden_runs()
    if clicked_row in hidden_runs:
        hideshow_button = Li('Show', hx_get=f"/show_run?run_id={clicked_row}", hx_target='#experiment-table',
                             hx_swap="innerHTML", cls="menu-item")
    else:
        hideshow_button = Li('Hide', hx_get=f"/hide_run?run_id={clicked_row}", hx_target='#experiment-table',
                             hx_swap="innerHTML",cls="menu-item")
    if session.get("show_hidden", False):
        toggle_visibility_button = Li('Hide Hidden', hx_get=f"/hide_hidden", hx_target='#experiment-table',
                                      hx_swap="innerHTML", cls="menu-item")
    else:
        toggle_visibility_button = Li('Show Hidden', hx_get=f"/show_hidden", hx_target='#experiment-table',
                                      hx_swap="innerHTML", cls="menu-item")
    return Div(
        Ul(
            hideshow_button,
            toggle_visibility_button,
            cls='dropdown-menu'
        ),
        id='custom-menu',
        style=f'visibility: visible; top: {top}px; left: {left}px;',
    )