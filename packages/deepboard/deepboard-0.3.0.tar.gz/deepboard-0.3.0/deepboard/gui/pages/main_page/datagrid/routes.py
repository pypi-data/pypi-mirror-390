from typing import *
from fasthtml.common import *
from .datagrid import DataGrid
from .compare_button import CompareButton
from ..main_page import MainPage
from ....components.quick_filter import QuickFilter, ColValue, get_unique_from_col
from ....components.modal import WindowedModal

def build_datagrid_endpoints(rt):
    rt("/hide")(hide_column)
    rt("/show")(show_column)
    rt("/rename_col_datagrid")(get_rename_column)
    rt("/rename_col", methods=["POST"])(post_rename_column)
    rt("/sort")(sort)
    rt("/reorder_columns", methods=["POST"])(reorder_columns)
    rt("/shift_click_row")(shift_click_row) # Endpoint is called in the javascript file
    rt("/hide_run")(hide_run)
    rt("/show_run")(show_run)
    rt("/show_hidden")(show_hidden)
    rt("/hide_hidden")(hide_hidden)
    rt("/compare_action")(compare_action)
    rt("/filter_col_datagrid")(load_datagrid)
    rt("/filter_value")(filter_value)
    rt("/filter_deselect_all")(deselect_all)
    rt("/filter_select_all")(select_all)
    rt("/reload_datagrid")(reload_datagrid)
    rt("/filter_clear")(filter_clear)


async def hide_column(session, col: str):
    from __main__ import rTable
    rTable.hide_column(col)

    # Return the datagrid
    return DataGrid(session)

async def show_column(session, col: str, after: str):
    from __main__ import rTable
    cols = rTable.result_columns
    if after not in cols:
        print(f"[WARNING]: Did not find column: {after}")
        return DataGrid(session)
    pos = cols[after][0] + 1
    print(f"Show column: {col} after {after} position {pos}")
    rTable.show_column(col, pos)

    # Return the datagrid
    return DataGrid(session)

async def get_rename_column(session, col: str):
    from __main__ import rTable
    if col not in rTable.result_columns:
        print(f"[WARNING]: Did not find column: {col}")
        return DataGrid(session)
    return DataGrid(session, rename_col=col)

async def post_rename_column(session, col_id: str, new_name: str):
    from __main__ import rTable
    if col_id not in rTable.result_columns:
        print(f"[WARNING]: Did not find column: {col_id}")
        return DataGrid(session)
    rTable.set_column_alias({col_id: new_name})

    # Return the datagrid
    return DataGrid(session)

async def sort(session, by: str, order: str):
    if "datagrid" not in session:
        session["datagrid"] = dict(
            sort_by=None,
            sort_order=None
        )
    session["datagrid"]["sort_by"] = by
    session["datagrid"]["sort_order"] = order
    return DataGrid(session)

async def reorder_columns(session, order: str):
    from __main__ import rTable
    order = order.split(",")
    prep_order = {col_id: i + 1 for i, col_id in enumerate(order)}
    rTable.set_column_order(prep_order)
    return DataGrid(session)

async def shift_click_row(session, run_id: int):
    if "datagrid" not in session:
        session["datagrid"] = dict()

    session["datagrid"]["multiselection"] = True
    if "selected-rows" not in session["datagrid"]:
        session["datagrid"]["selected-rows"] = []

    if run_id in session["datagrid"]["selected-rows"]:
        session["datagrid"]["selected-rows"].remove(run_id)
    else:
        session["datagrid"]["selected-rows"].append(run_id)

    return DataGrid(session), CompareButton(session, swap=True)

async def hide_run(session, run_id: int):
    from __main__ import rTable
    rTable.hide_run(run_id)
    return DataGrid(session)

async def show_run(session, run_id: int):
    from __main__ import rTable
    rTable.show_run(run_id)
    return DataGrid(session)

async def show_hidden(session):
    session["show_hidden"] = True
    return DataGrid(session)

async def hide_hidden(session):
    session["show_hidden"] = False
    return DataGrid(session)

def compare_action(session, run_ids: str):
    if "show_hidden" not in session:
        session["show_hidden"] = False
    session["datagrid"] = dict()
    return MainPage(session, swap=True), HttpHeader("HX-Blank-Redirect", f"/compare?run_ids={run_ids}")

async def load_datagrid(session, colid: str):
    return QuickFilter(session, colid)

async def filter_value(session, colid: str, value: str):
    if "datagrid" not in session:
        session["datagrid"] = dict(
            filters={}
        )
    if "filters" not in session["datagrid"]:
        session["datagrid"]["filters"] = {}

    filters = session["datagrid"].get("filters", {})
    if colid not in filters:
        filters[colid] = []

    if value in filters[colid]:
        filters[colid].remove(value)
        selected = True
    else:
        filters[colid].append(value)
        selected = False

    session["datagrid"]["filters"] = filters
    return ColValue(colid, value, selected=selected)

async def select_all(session, colid: str):
    if "datagrid" not in session:
        session["datagrid"] = dict(
            filters={}
        )
    if "filters" not in session["datagrid"]:
        session["datagrid"]["filters"] = {}

    session["datagrid"]["filters"][colid] = []
    return QuickFilter(session, colid)


async def deselect_all(session, colid: str):
    _, values = get_unique_from_col(colid)
    if "datagrid" not in session:
        session["datagrid"] = dict(
            filters={}
        )
    if "filters" not in session["datagrid"]:
        session["datagrid"]["filters"] = {}

    session["datagrid"]["filters"][colid] = [str(val) for val in values]
    return QuickFilter(session, colid)

async def reload_datagrid(session):
    return DataGrid(session), WindowedModal(title="", active=False, swap_oob=True)

async def filter_clear(session, colid: str):
    if "datagrid" not in session:
        return DataGrid(session)
    if "filters" not in session["datagrid"]:
        return DataGrid(session)
    filters = session["datagrid"]["filters"]
    if colid in filters:
        del filters[colid]
    session["datagrid"]["filters"] = filters
    return DataGrid(session)
