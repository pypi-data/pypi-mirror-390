from fasthtml.common import *
from typing import *
from ....components import ArtefactHeader, ArtefactFilterOptions, ArtefactFilter, ArtefactValue, WindowedModal
from ....components.artefactFilter import get_values
from .images import ImageTab
from .fragments import FragmentTab

def build_routes(rt):
    rt("/show_filter_artefacts_options")(show_filter_artefacts_options)
    rt("/add_filter_artefacts")(add_filter_artefacts)
    rt("/filter_artefact")(filter_artefact)
    rt("/artefact_filter_deselect_all")(deselect_all)
    rt("/artefact_filter_select_all")(select_all)
    rt("/filter_artefacts")(filter_artefacts)
    rt("/artefact_clear_filter")(clear_filters)

def show_filter_artefacts_options(session, show: bool, type: str):
    return ArtefactFilterOptions(show, type)


def add_filter_artefacts(session, filter_by: str, type: str):
    return ArtefactFilter(session, type, filter_by), ArtefactFilterOptions(False, type, swap=True)

def filter_artefact(session, type: str, element: str, value: str):
    filers = session.get("artefact-filters", {}).get(type, {})
    unselected = filers.get(element, [])
    if value in unselected:
        unselected.remove(value)
    else:
        unselected.append(value)

    # Store back to session
    if "artefact-filters" not in session:
        session["artefact-filters"] = {}
    if type not in session["artefact-filters"]:
        session["artefact-filters"][type] = {}

    session["artefact-filters"][type][element] = unselected
    return ArtefactValue(type, element, value, selected=(value not in unselected))

def deselect_all(session, elem: str, type: str):
    from __main__ import rTable
    if "artefact-filters" not in session:
        session["artefact-filters"] = {}
    if type not in session["artefact-filters"]:
        session["artefact-filters"][type] = {}

    runID = session.get("datagrid", {}).get('selected-rows', [])[-1]
    socket = rTable.load_run(runID)
    stats = get_values(socket, type)
    match elem:
        case "step":
            values = stats.steps
        case "epoch":
            values = stats.epochs
        case "tag":
            values = stats.tags
        case "reps":
            values = stats.reps
        case _:
            raise ValueError(f"Unsupported element to filter: {elem}")
    session["artefact-filters"][type][elem] = [str(val) for val in values]
    return ArtefactFilter(session, type, elem)

def select_all(session, elem: str, type: str):
    if "artefact-filters" not in session:
        session["artefact-filters"] = {}
    if type not in session["artefact-filters"]:
        session["artefact-filters"][type] = {}

    session["artefact-filters"][type][elem] = []
    return ArtefactFilter(session, type, elem)

def filter_artefacts(session, type: str):
    runID = session.get("datagrid", {}).get('selected-rows', [])[-1]
    # Close modal + refresh according tab content
    match type:
        case'IMAGE':
            tab_content = ImageTab(session, runID, type="IMAGE")
        case "PLOT":
            tab_content = ImageTab(session, runID, type="PLOT")
        case 'RAW':
            tab_content = FragmentTab(session, runID, type="RAW")
        case 'HTML':
            tab_content = FragmentTab(session, runID, type="HTML")
        case _:
            raise ValueError(f"Unsupported artefact type: {type}")

    return tab_content, WindowedModal(title="", active=False, swap_oob=True)

def clear_filters(session, type: str, element: str):
    if "artefact-filters" not in session:
        return
    if type not in session["artefact-filters"]:
        return

    session["artefact-filters"][type][element] = []
    runID = session.get("datagrid", {}).get('selected-rows', [])[-1]
    # Refresh according tab content
    match type:
        case'IMAGE':
            tab_content = ImageTab(session, runID, type="IMAGE")
        case "PLOT":
            tab_content = ImageTab(session, runID, type="PLOT")
        case 'RAW':
            tab_content = FragmentTab(session, runID, type="RAW")
        case 'HTML':
            tab_content = FragmentTab(session, runID, type="HTML")
        case _:
            raise ValueError(f"Unsupported artefact type: {type}")

    return tab_content