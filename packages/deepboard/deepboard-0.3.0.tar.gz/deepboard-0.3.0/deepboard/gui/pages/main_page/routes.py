from .handlers import click_row_handler
from .datagrid import build_datagrid_endpoints
from .right_panel import build_right_panel_routes
from .main_page import MainPage
from deepboard.gui.components import Modal, WindowedModal

def build_main_page_endpoints(rt):
    rt("/click_row")(click_row_handler)
    rt("/reset")(reset)
    rt("/fullscreen")(fullscreen)
    rt("/close_modal")(close_modal)
    rt("/close_windowed_modal")(close_windowed_modal)
    build_datagrid_endpoints(rt)
    build_right_panel_routes(rt)

def reset(session):
    if "show_hidden" not in session:
        session["show_hidden"] = False
    session["datagrid"] = dict()
    return MainPage(session, swap=True)

def close_modal(session):
    return Modal(active=False)

def close_windowed_modal(session):
    return WindowedModal(title="", active=False)

def fullscreen(session, full: bool):
    return MainPage(session, swap=True, fullscreen=full)