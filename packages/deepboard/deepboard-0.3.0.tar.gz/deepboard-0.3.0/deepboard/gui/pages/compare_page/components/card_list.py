from typing import *
from fasthtml.common import *
from .split_card import SplitCard

def ChartCardList(session, swap: bool = False):
    runIDs = sorted([int(rid) for rid in session["compare"]["selected-rows"]])
    from __main__ import rTable
    sockets = [rTable.load_run(runID) for runID in runIDs]
    keys = {key for socket in sockets for key in socket.formatted_scalars}
    splits = {split for split, metric in keys}
    splits = sorted(splits)
    metrics = {split: [metric for sp, metric in keys if sp == split] for split in splits}

    return Ul(
                *[SplitCard(session, split, metrics[split]) for split in splits],
                cls="comparison-list",
                id="chart-card-list",
                hx_swap_oob="true" if swap else None
            )