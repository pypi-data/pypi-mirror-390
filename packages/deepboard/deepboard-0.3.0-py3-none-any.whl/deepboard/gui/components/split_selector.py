from fasthtml.common import *
from typing import Literal

def SplitSelector(runID, available_splits: List[str], selected: str, step: int, epoch: int, run_rep: int,
                  type: str, path: str, swap: bool = False):

    swap_oob = dict(swap_oob="true") if swap else {}
    return Select(
        *[
            Option(split.capitalize() if split else "", value=split, selected=selected == split, cls="artefact-split-option")
            for split in available_splits
        ],
        name="split_select",
        hx_get=f"{path}?runID={runID}&step={step}&epoch={epoch}&run_rep={run_rep}&type={type}",
        hx_target=f"#artefact-card-{step}-{epoch}-{run_rep}",
        hx_trigger="change",
        hx_swap="outerHTML",
        hx_params="*",
        **swap_oob,
        cls="artefact-split-select",
    )