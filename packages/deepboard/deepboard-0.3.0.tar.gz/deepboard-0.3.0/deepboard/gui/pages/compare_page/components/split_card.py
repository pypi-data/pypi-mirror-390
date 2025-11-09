from typing import *
from fasthtml.common import *
from .chart import LoadingChart

def SplitCard(session, split: str, metrics: List[str]):
    from __main__ import rTable
    runIDs = sorted([int(rid) for rid in session["compare"]["selected-rows"]])
    sockets = [rTable.load_run(runID) for runID in runIDs]
    running = any([socket.status == "running" for socket in sockets])
    metrics = sorted(metrics)
    chart_type = session["compare"]["chart_type"] if "chart_type" in session["compare"] else "step"
    logscale = session["compare"]["chart_scale"] == "log" if "chart_scale" in session["compare"] else False

    opened = session["compare"]["cards-state"][split] if "cards-state" in session["compare"] and split in session["compare"]["cards-state"] else True
    if opened:
        return Li(
            Div(
                H1(split, cls="split-card-title"),
                Button(
                    I(cls="fas fa-chevron-down"),
                    hx_get=f"/compare/toggle_accordion?split={split}&metrics={','.join(metrics)}&open=false",
                    hx_target=f"#split-card-{split}",
                    hx_swap="outerHTML",
                    cls="accordion-toggle"
                ),
                cls="split-card-header"
            ),
            Div(
                *[LoadingChart(session, split, metric, type=chart_type, running=running, logscale=logscale) for metric in metrics],
                cls="multi-charts-container"
            ),
            cls="split-card",
            id=f"split-card-{split}",
        )
    else:
        return Li(
            Div(
                H1(split, cls=".split-card-title"),
                Button(
                    I(cls="fas fa-chevron-down"),
                    hx_get=f"/compare/toggle_accordion?split={split}&metrics={','.join(metrics)}&open=true",
                    hx_target=f"#split-card-{split}",
                    hx_swap="outerHTML",
                    cls="accordion-toggle rotated"
                ),

                cls="split-card-header"
            ),
            cls="split-card closed",
            id=f"split-card-{split}",
        )