from typing import *
from fasthtml.common import *
from deepboard.gui.components import Legend, ChartType, Smoother, LogSelector
from .components import SplitCard, ChartCardList, CompareSetup, Chart
from .compare_page import ComparePage

def build_compare_routes(rt):
    rt("/compare")(ComparePage)
    rt("/compare/toggle_accordion")(toggle_accordion)
    rt("/compare/change_chart")(change_chart_type)
    rt("/compare/change_scale")(change_chart_scale)
    rt("/compare/hide_line")(hide_line)
    rt("/compare/show_line")(show_line)
    rt("/compare/change_smoother")(change_smoother)
    rt("/compare/chart")(load_chart)

# Routes
def toggle_accordion(session, split: str, metrics: str, open: bool):
    if "cards-state" not in session["compare"]:
        session["compare"]["cards-state"] = {}
    session["compare"]["cards-state"][split] = open
    return SplitCard(session, split, metrics=metrics.split(","))

def change_chart_type(session, runIDs: str, step: bool):
    new_type = "time" if step else "step"
    session["compare"]["chart_type"] = new_type
    return (ChartType(session, path="/compare", session_path="compare", selected_rows_key="compare"), # We want to toggle it
            ChartCardList(session, swap=True)
    )

def change_chart_scale(session, runIDs: str, log: bool):
    new_scale = "default" if log else "log"
    session["compare"]["chart_scale"] = new_scale
    return (LogSelector(session, path="/compare", session_path="compare", selected_rows_key="compare"), # We want to toggle it
            ChartCardList(session, swap=True)
    )

def hide_line(session, runIDs: str, curveID: str):
    if 'hidden_lines' not in session["compare"]:
        session["compare"]['hidden_lines'] = []
    session["compare"]['hidden_lines'].append(curveID)
    return CompareSetup(session, swap=True), ChartCardList(session, swap=True)


def show_line(session, runIDs: str, curveID: str):
    if 'hidden_lines' not in session["compare"]:
        session["compare"]['hidden_lines'] = []
    if curveID in session["compare"]['hidden_lines']:
        session["compare"]['hidden_lines'].remove(curveID)

    return CompareSetup(session, swap=True), ChartCardList(session, swap=True)

def change_smoother(session, runIDs: str, smoother: int):
    session["compare"]["smoother_value"] = smoother
    return CompareSetup(session, swap=True), ChartCardList(session, swap=True)

def load_chart(session, split: str, metric: str, type: str, running: bool, logscale: bool = False):
    return Chart(session, split, metric, type, running, logscale=logscale)