from fasthtml.common import *
from .modal import WindowedModal
import hashlib

def hash_id(text):
    return hashlib.md5(text.encode()).hexdigest()[:10]

def get_unique_from_col(col_id: str):
    from __main__ import rTable
    # Load results from the database
    col_names, col_ids, _, _, data = rTable.get_results()

    # Find the index of the column
    idx = col_ids.index(col_id)
    col_name = col_names[idx]

    unique_values = set()
    for row in data:
        unique_values.add(row[idx])

    values = sorted(list(unique_values))
    return col_name, values

def ColValue(col_id, value, selected: bool = True):
    return Div(
        value,
        cls="quick-filter-value selected" if selected else "quick-filter-value",
        id=f"quick-filter-value-{hash_id(str(value))}",
        hx_get=f'/filter_value?colid={col_id}&value={value}',
        hx_swap="outerHTML",
        hx_target=f"#quick-filter-value-{hash_id(str(value))}"
    )

def QuickFilter(session, col_id: str):
    from __main__ import rTable
    filters = session.get("datagrid") and session["datagrid"].get("filters", {}) or {}
    if col_id in filters:
        unselected = filters[col_id]
    else:
        unselected = []

    col_name, values = get_unique_from_col(col_id)

    # Get column values for the given column ID
    return WindowedModal(
        Span(col_name, cls="quick-filter-column-name"),
        Div(
            *[ColValue(col_id, value, selected=str(value) not in unselected) for value in values],
            cls="quick-filter-values-list"
        ),
        Div(
            A('Deselect All', href="#", hx_get=f"/filter_deselect_all?colid={col_id}", hx_target="#windowed-modal", hx_swap="outerHTML"),
            A('Select All', href="#", hx_get=f"/filter_select_all?colid={col_id}", hx_target="#windowed-modal", hx_swap="outerHTML"),
            cls="quick-filter-action"
        ),
        Button("Filter", cls="quick-filter-button", hx_get="/reload_datagrid", hx_target="#experiment-table", hx_swap="innerHTML"),
        title="Quick Filter",
        closable=True,
        active=True,
    )
