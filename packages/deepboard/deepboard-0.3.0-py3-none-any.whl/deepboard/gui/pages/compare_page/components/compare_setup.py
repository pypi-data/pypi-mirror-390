from typing import *
from fasthtml.common import *
from deepboard.gui.components import Legend, ChartType, Smoother, LogSelector

def getName(row: dict) -> Optional[str]:
    """
    From an experiment dict, get its display name. If a 'note' is given, use it. Otherwise, use the comment. If no
    comment is given, return None
    :param row: The experiment row as dict
    :return: note or comment or None
    """
    s = row.get('note') or row.get('comment') or None
    if s is None:
        return None

    s = [line.strip() for line in s.splitlines() if line.strip()][0] # First non-empty line
    return s

def CompareSetup(session, swap: bool = False):
    from __main__ import CONFIG
    from __main__ import rTable
    if "hidden_lines" in session["compare"]:
        hidden_lines = session["compare"]["hidden_lines"]
    else:
        hidden_lines = []
    raw_labels = [int(txt) for txt in session["compare"]["selected-rows"]]
    raw_labels = sorted(raw_labels)
    sockets = [rTable.load_run(runID) for runID in raw_labels]
    repetitions = [socket.get_repetitions() for socket in sockets]
    names = [getName(rTable.get_experiment_raw(runID)) for runID in raw_labels]
    if any(len(rep) > 1 for rep in repetitions):
        labels = [(f"{label}.{rep} — {name}" if name is not None else f"{label}.{rep}", f"{label}.{rep}", CONFIG.COLORS[i % len(CONFIG.COLORS)], f"{label}.{rep}" in hidden_lines) for i, (label, name) in enumerate(zip(raw_labels, names)) for rep in sockets[i].get_repetitions()]
    else:
        labels = [(f"{label} — {name}" if name is not None else f"{label}", f"{label}", CONFIG.COLORS[i % len(CONFIG.COLORS)], f"{label}" in hidden_lines) for
                  i, (label, name) in enumerate(zip(raw_labels, names))]
    return Div(
        H1("Setup", cls="chart-scalar-title"),
        Legend(session, labels, path="/compare", selected_rows_key="compare"),
        ChartType(session, path="/compare", selected_rows_key="compare", session_path="compare"),
        LogSelector(session, path="/compare", selected_rows_key="compare", session_path="compare"),
        Smoother(session, path="/compare", selected_rows_key="compare", session_path="compare"),
        cls="setup-card",
        id="setup-card",
        hx_swap_oob="true" if swap else None,
    )
