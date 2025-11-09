from typing import *
from fasthtml.common import *

def Header(name: str, col_id: str, sort_dir: str = None, has_filter: bool = False):
    if sort_dir == "asc":
        return Th(
            Div(name, I(cls='fa fa-filter', style="margin-left: 0.5em;") if has_filter else None, Span("↑", cls='sort-icon'), hx_get=f'/sort?by={col_id}&order=desc', target_id='experiment-table',
                hx_swap='innerHTML',
                cls='sortable',
                id=f"grid-header-{col_id}"
                ),
            data_col=col_id
        ),
    elif sort_dir == "desc":
        return Th(
            Div(name, I(cls='fa fa-filter', style="margin-left: 0.5em;") if has_filter else None, Span("↓", cls='sort-icon'), hx_get=f'/sort?by={col_id}&order=', target_id='experiment-table',
                hx_swap='innerHTML',
                cls='sortable',
                id=f"grid-header-{col_id}"),
            data_col=col_id
        ),
    else:
        return Th(
            Div(name, I(cls='fa fa-filter', style="margin-left: 0.5em;") if has_filter else None, Span('⇅', cls='sort-icon'), hx_get=f'/sort?by={col_id}&order=asc', target_id='experiment-table',
                hx_swap='innerHTML',
                cls='sortable',
                id=f"grid-header-{col_id}"),
            data_col=col_id
        ),

def HeaderRename(name: str, col_id: str):
    return Th(
        Input(
            type="text",
            value=name,
            name="new_name",
            hx_post=f'/rename_col?col_id={col_id}',
            hx_target='#experiment-table',
            hx_swap='innerHTML',
            id=f"grid-header-{col_id}",
            cls="rename-input"
        )
    ),
