from typing import *
from fasthtml.common import *
from ....components import plotly2fasthtml_download
from .utils import make_lines
from deepboard.gui.utils import make_fig

def Chart(session, split: str, metric: str, type: Literal["step", "duration"], running: bool, logscale: bool):
    from __main__ import rTable
    runIDs = [int(txt) for txt in session["compare"]["selected-rows"]]
    runIDs.sort()
    sockets = [rTable.load_run(runID) for runID in runIDs]
    hidden_lines = session["compare"]["hidden_lines"] if "hidden_lines" in session["compare"] else []
    smoothness = session["compare"]["smoother_value"] - 1 if "smoother_value" in session["compare"] else 0
    lines = make_lines(sockets, split, metric, runIDs, type)

    # # Sort lines by label
    lines.sort(key=lambda x: x[0])
    # Hide lines if needed
    lines = [line for line in lines if line[0] not in hidden_lines]
    fig = make_fig(lines, type=type, smoothness=smoothness, log_scale=logscale)

    if running:
        update_params = dict(
            hx_get=f"/compare/chart?split={split}&metric={metric}&type={type}&running={running}&logscale={logscale}",
            hx_target=f"#chart-container-{split}-{metric}",
            hx_trigger="every 10s",
            hx_swap="outerHTML",
        )
    else:
        update_params = {}
    return  Div(
            plotly2fasthtml_download(fig, js_options=dict(responsive=True)),
            cls="chart-container",
            id=f"chart-container-{split}-{metric}",
            **update_params
        ),

def LoadingChart(session, split: str, metric: str, type: Literal["step", "duration"], running: bool = False, logscale: bool = False):
    return Div(
            Div(
                H1(metric, cls="chart-title"),
                cls="chart-header",
                id=f"chart-header-{split}-{metric}"
            ),
        Div(
            cls="chart-container",
            id=f"chart-container-{split}-{metric}",
            hx_get=f"/compare/chart?split={split}&metric={metric}&type={type}&running={running}&logscale={logscale}",
            hx_target=f"#chart-container-{split}-{metric}",
            hx_trigger="load",
        ),
        cls = "chart",
        id = f"chart-{split}-{metric}",
    )