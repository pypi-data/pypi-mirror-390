from fasthtml.common import *
from starlette.responses import Response
from typing import *
from deepboard.gui.components import SplitSelector, StatLine, ArtefactGroup, StatCell, ArtefactHeader

def _is_allowed(fragment: dict, filters: Optional[dict[str, List[str]]]) -> bool:
    if filters is None:
        return True

    for key, unallowed_values in filters.items():
        if key not in fragment:
            raise ValueError(f"Invalid filter key: {key}! Available keys are 'tag', 'epoch', 'run_rep'.")

        if str(fragment[key]) in unallowed_values:
            return False
    return True

class FragmentsStats(NamedTuple):
    steps: List[int]
    epochs: List[int]
    tags: List[str]
    reps: List[int]

def _get_fragments(socket, type: Literal["RAW", "HTML"]):
    if type == "RAW":
        fragments = socket.get_text()
    else:
        fragments = socket.get_fragment()

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

    return fragments, FragmentsStats(steps, epochs, tags, reps)

def TextComponent(text: str):
    return Div(
        P(text, cls="fragment-text"),
        cls="fragment-text-container"
    )

def HTMLComponent(html_str: str):
    # Return whatever is in html_str as a HTML component
    return NotStr(html_str)

def FragmentCard(tag: str, step: int, epoch: Optional[int], run_rep: int, fragments, frag_type: Literal["RAW", "HTML"]):
    from __main__ import rTable


    return Div(
        ArtefactGroup(*[
            TextComponent(frag_content) if frag_type == "RAW" else HTMLComponent(frag_content)
            for frag_content in fragments
        ]),
        Div(
            StatCell("Tag", tag) if tag is not None else None,
            StatCell("Step", str(step)) if step is not None else None,
            StatCell("Epoch", str(epoch)) if epoch is not None  else None,
            StatCell("Run Rep", str(run_rep)) if run_rep is not None else None,
            cls="artefact-card-footer",
        ),
        id=f"artefact-card-{step}-{epoch}-{run_rep}",
        cls="artefact-card",
    )

def FragmentTab(session, runID, type: Literal["RAW", "HTML"], swap: bool = False):
    from __main__ import rTable
    filters = session.get("artefact-filters", {}).get(type, {})
    socket = rTable.load_run(runID)

    fragments, stats = _get_fragments(socket, type=type)
    index = []

    for fragment in fragments:
        idx = (fragment["tag"], fragment["step"], fragment["epoch"], fragment["run_rep"])
        if idx not in index:
            index.append(idx)

    grouped = {}
    for fragment in fragments:
        if not _is_allowed(fragment, filters):
            continue
        idx = (fragment["tag"], fragment["step"], fragment["epoch"], fragment["run_rep"])
        if idx not in grouped:
            grouped[idx] = []
        grouped[idx].append(fragment["fragment"])


    return Div(
        ArtefactHeader(session, type=type),
        *[
            FragmentCard(
                tag,
                step,
                epoch if len(stats.epochs) > 1 else None,
                run_rep if len(stats.reps) > 1 else None,
                fragment_group,
                frag_type=type)
            for (tag, step, epoch, run_rep), fragment_group in grouped.items()
        ],
        style="display; flex; flex-direction: column; align-items: center; justify-content: center;",
        id="fragment-tab",
        hx_swap_oob="true" if swap else None,
    )


def fragment_enable(runID, type: Literal["RAW", "HTML"]):
    """
    Check if some fragments/text are logged and available for the runID. If not, we consider disable it.
    :param runID: The runID to check.
    :return: True if scalars are available, False otherwise.
    """
    from __main__ import rTable
    socket = rTable.load_run(runID)
    if type == "RAW":
        return len(socket.get_text()) > 0
    else:
        return len(socket.get_fragment()) > 0
