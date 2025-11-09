from deepboard.gui.utils import get_lines
from typing import *

def make_lines(sockets, split: str, metric: str, runIDs: List[int], type: Literal["step", "duration"]):
    from __main__ import CONFIG
    lines = []
    all_reps = [socket.get_repetitions() for socket in sockets]
    multi_rep = any(len(rep) > 1 for rep in all_reps)
    for i, runID in enumerate(runIDs):
        reps = get_lines(sockets[i], split, metric, key=type)

        for rep_idx, rep in enumerate(reps):
            lines.append((
                f'{runID}.{rep_idx}' if multi_rep else f'{runID}',
                rep["index"],
                rep["value"],
                CONFIG.COLORS[i % len(CONFIG.COLORS)],
                rep["epoch"],
            ))
    return lines