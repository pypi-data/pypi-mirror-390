from typing import *
from fasthtml.common import *
from .datagrid import DataGrid, CompareButton
from .right_panel import RightPanel

def MainPage(session, swap: bool = False, fullscreen: bool = False):
    return Div(
        Div(
            DataGrid(session, wrapincontainer=True, fullscreen=fullscreen),
            CompareButton(session),
            Div(hx_target="#container",
                hx_swap="outerHTML",
                hx_trigger="keyup[!event.target.matches('input, textarea') && (key=='f' || key=='F')] from:body",
                hx_get=f"/fullscreen?full={'true' if not fullscreen else 'false'}",),
            cls="table-container"
        ),
        RightPanel(session, closed = fullscreen),
        cls='container',
        id="container",
        hx_swap_oob="true" if swap else None
    )