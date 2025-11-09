from fasthtml.common import *
from .scalars import ScalarTab, scalar_enable
from .images import ImageTab, images_enable
from .fragments import FragmentTab, fragment_enable
from .config import ConfigView
from .hparams import HParamsView
from .run_info import InfoView

def reset_scalar_session(session):
    session["scalars"] = dict(
        hidden_lines=[],
        smoother_value=1,
        chart_type='step'
    )

def Tabs(session, run_id, active_tab: str, inner: bool = False):
    from __main__ import rTable
    scalar_is_available = scalar_enable(run_id)
    images_is_available = images_enable(run_id, type="IMAGES")
    plot_is_available = images_enable(run_id, type="PLOT")
    text_is_available = fragment_enable(run_id, type="RAW")
    fragment_is_available = fragment_enable(run_id, type="HTML")


    # Verify that the active tab requested is availalable
    if active_tab == 'scalars' and not scalar_is_available:
        active_tab = "images"
    if active_tab == "images" and not images_is_available:
        active_tab = "figures"
    if active_tab == "figures" and not plot_is_available:
        active_tab = "text"
    if active_tab == "text" and not text_is_available:
        active_tab = "fragments"
    if active_tab == "fragments" and not fragment_is_available:
        active_tab = "config"
    tabs = []

    # If the runID does not have any scalars logged, we do not show the scalars tab
    if scalar_is_available:
        tabs.append(
            Div('Scalars', cls='tab active' if active_tab == 'scalars' else 'tab',
                hx_get=f'/fillpanel?run_id={run_id}&tab=scalars', hx_target='#sp-tab-menu')
        )

    if images_is_available:
        tabs.append(
            Div('Images', cls='tab active' if active_tab == 'images' else 'tab',
                hx_get=f'/fillpanel?run_id={run_id}&tab=images', hx_target='#sp-tab-menu')
        )

    if plot_is_available:
        tabs.append(
            Div('Figures', cls='tab active' if active_tab == 'figures' else 'tab',
                hx_get=f'/fillpanel?run_id={run_id}&tab=figures', hx_target='#sp-tab-menu')
        )

    if text_is_available:
        tabs.append(
            Div('Text', cls='tab active' if active_tab == 'text' else 'tab',
                hx_get=f'/fillpanel?run_id={run_id}&tab=text', hx_target='#sp-tab-menu')
        )

    if fragment_is_available:
        tabs.append(
            Div('Fragments', cls='tab active' if active_tab == 'fragments' else 'tab',
                hx_get=f'/fillpanel?run_id={run_id}&tab=fragments', hx_target='#sp-tab-menu')
        )

    tabs += [
        Div('Config', cls='tab active' if active_tab == 'config' else 'tab',
            hx_get=f'/fillpanel?run_id={run_id}&tab=config', hx_target='#sp-tab-menu'),
        Div('HParams', cls='tab active' if active_tab == 'hparams' else 'tab',
            hx_get=f'/fillpanel?run_id={run_id}&tab=hparams', hx_target='#sp-tab-menu'),
        Div('Info', cls='tab active' if active_tab == 'run_info' else 'tab',
            hx_get=f'/fillpanel?run_id={run_id}&tab=run_info', hx_target='#sp-tab-menu'),
    ]
    if inner:
        return Div(
            *tabs,
            style="display: flex;"
        )
    else:
        return Div(
                Div(
                    *tabs,
                    style="display: flex;"
                ),
                cls='tab-menu',
                id="sp-tab-menu",
            )

def TabContent(session, run_id: int, active_tab: str, swap: bool = False):
    if active_tab == 'scalars':
        tab_content = ScalarTab(session, run_id)
    elif active_tab == 'images':
        tab_content = ImageTab(session, run_id, type="IMAGE")
    elif active_tab == 'figures':
        tab_content = ImageTab(session, run_id, type="PLOT")
    elif active_tab == 'text':
        tab_content = FragmentTab(session, run_id, type="RAW")
    elif active_tab == 'fragments':
        tab_content = FragmentTab(session, run_id, type="HTML")
    elif active_tab == 'config':
        tab_content = ConfigView(run_id)
    elif active_tab == 'hparams':
        tab_content = HParamsView(run_id)
    elif active_tab == 'run_info':
        tab_content = InfoView(run_id)
    else:
        tab_content = Div(
            P("Invalid tab selected.", cls="error-message")
        )

    return Div(
        tab_content,
        id='sp-tab-content', cls='tab-content',
        hx_swap_oob="true" if swap else None,
    )
def RightPanelContent(session, run_id: int, active_tab: str):
    run_name = "DEBUG" if run_id == -1 else run_id
    return Div(
        H1(f"Run: {run_name}"),
        Tabs(session, run_id, active_tab),
        TabContent(session, run_id, active_tab),
        cls="right-panel-content",
        id="right-panel-content"
    ),

def OpenPanel(session, run_id: int, active_tab: str = 'scalars'):
    return Div(
        RightPanelContent(session, run_id, active_tab),
        cls="open-right-panel"
    )

def RightPanel(session, closed: bool = False):
    placeholder_text = [
        P("⌘ / ctrl + click to compare runs", cls="right-panel-placeholder"),
        P("'F' for fullscreen", cls="right-panel-placeholder")
    ]
    if "datagrid" in session and session["datagrid"].get("selected-rows") and len(session["datagrid"]["selected-rows"]) == 1:
        run_id = session["datagrid"]["selected-rows"][0]
    else:
        run_id = None
    return Div(
        Button(
            I(cls="fas fa-times"),
            hx_get="/reset",
            hx_target="#container",
            hx_swap="outerHTML",
            cls="close-button",
        ) if run_id is not None else None,
        Div(*placeholder_text) if run_id is None else OpenPanel(session, run_id),
        id='right-panel',
        cls="right-panel" if not closed else "right-panel-closed",
        hx_swap_oob='true'
    ),


def fill_panel(session, run_id: int, tab: str):
    return Tabs(session, run_id, tab, inner=True), TabContent(session, run_id, tab, swap=True)
