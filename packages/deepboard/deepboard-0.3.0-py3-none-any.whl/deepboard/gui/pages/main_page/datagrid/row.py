from typing import *
from fasthtml.common import *
from .utils import format_value
def Row(data, hparam_mask, run_id, selected: bool, hidden: bool, color: str, max_decimals: int, fullscreen: bool):
    cls = "table-row"
    if selected:
        cls += " table-row-selected"

    if hidden:
        cls += " table-row-hidden"

    return Tr(
        *[Td(
            format_value(value, max_decimals, is_hparam),
            style=f"background-color:transparent !important" if i == 0 and color else None,
        ) for i, (value, is_hparam) in enumerate(zip(data, hparam_mask))],
        hx_get=f"/click_row?run_id={run_id}&fullscreen={fullscreen}",  # HTMX will GET this URL
        hx_trigger="click[!event.ctrlKey && !event.metaKey]",
        hx_target="#experiment-table",  # Target DOM element to update
        hx_swap="innerHTML",  # Optional: how to replace content
        id=f"grid-row-{run_id}",
        cls=cls,
        style=f"background-color:#{color}70 !important" if color else None,
    )