from fasthtml.common import *
from .modal import WindowedModal
import hashlib
from typing import Literal, NamedTuple

class FragmentsStats(NamedTuple):
    steps: List[int]
    epochs: List[int]
    tags: List[str]
    reps: List[int]

def hash_id(text):
    return hashlib.md5(text.encode()).hexdigest()[:10]

def get_values(socket, type: Literal["RAW", "HTML", "IMAGE", "PLOT"]):
    match type:
        case "RAW":
            fragments = socket.get_text()
        case "HTML":
            fragments = socket.get_fragment()
        case "IMAGE":
            fragments = socket.get_images()
        case "PLOT":
            fragments = socket.get_figures()
        case _:
            raise ValueError(f"Unsupported fragment type: {type}")

    steps = list({fragment["step"] for fragment in fragments})
    epochs = list({fragment["epoch"] for fragment in fragments})
    tags = list({fragment["tag"] for fragment in fragments})
    reps = list({fragment["run_rep"] for fragment in fragments})
    steps = [s for s in steps if s is not None]
    steps.sort()
    epochs = [e for e in epochs if e is not None]
    epochs.sort()
    tags = [t for t in tags if t is not None]
    tags.sort()
    reps = [r for r in reps if r is not None]
    reps.sort()

    return FragmentsStats(steps, epochs, tags, reps)

def ArtefactValue(type, element, value, selected: bool = True):
    return Div(
        value,
        cls="quick-filter-value selected" if selected else "quick-filter-value",
        id=f"quick-filter-value-{hash_id(str(value))}",
        hx_get=f'/filter_artefact?type={type}&element={element}&value={value}',
        hx_swap="outerHTML",
        hx_target=f"#quick-filter-value-{hash_id(str(value))}"
    )

def ArtefactFilter(session, type: str, elem2filter: str, swap: bool = False):
    from __main__ import rTable

    filers = session.get("artefact-filters", {}).get(type, {})
    runID = session.get("datagrid", {}).get('selected-rows', [])[-1]

    unselected = filers.get(elem2filter, [])
    socket = rTable.load_run(runID)

    stats = get_values(socket, type=type)
    match type:
        case "RAW":
            name = "text"
        case "HTML":
            name = "fragments"
        case "IMAGE":
            name = "images"
        case "PLOT":
            name = "figures"
        case _:
            raise ValueError(f"Unsupported artefact type: {type}")

    match elem2filter:
        case "step":
            values = stats.steps
        case "epoch":
            values = stats.epochs
        case "tag":
            values = stats.tags
        case "reps":
            values = stats.reps
        case _:
            raise ValueError(f"Invalid filter element: {elem2filter}! Available elements are 'step', 'epoch', 'tag', 'run_rep'.")

    # Get column values for the given column ID
    return WindowedModal(
        Span(elem2filter, cls="quick-filter-column-name"),
        Div(
            *[ArtefactValue(type, elem2filter, value, selected=str(value) not in unselected) for value in values],
            cls="quick-filter-values-list"
        ),
        Div(
            A('Deselect All', href="#", hx_get=f"/artefact_filter_deselect_all?elem={elem2filter}&type={type}", hx_target="#windowed-modal", hx_swap="outerHTML"),
            A('Select All', href="#", hx_get=f"/artefact_filter_select_all?elem={elem2filter}&type={type}", hx_target="#windowed-modal", hx_swap="outerHTML"),
            cls="quick-filter-action"
        ),
        Button("Filter", cls="quick-filter-button", hx_get=f'/filter_artefacts?type={type}', hx_target="#sp-tab-content", hx_swap="innerHTML"),
        title=f"Filter {name}",
        closable=True,
        active=True,
        swap_oob=swap
    )