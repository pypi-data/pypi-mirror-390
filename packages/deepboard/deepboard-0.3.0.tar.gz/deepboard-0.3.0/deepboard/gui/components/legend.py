from fasthtml.common import *

def LegendLine(session, runIDs: str, label: str, curveID: str, color: str, hidden: bool, path):
    from __main__ import CONFIG
    if hidden:
        return Li(
            Span(cls="legend-icon", style=f"background-color: {CONFIG.HIDDEN_COLOR};"),
            A(label, cls="legend-label", style=f"color: {CONFIG.HIDDEN_COLOR};"),
            hx_get=f"{path}/show_line?runIDs={runIDs}&curveID={curveID}",
            cls="legend-line"
        )
    else:
        return Li(
            Span(cls="legend-icon", style=f"background-color: {color};"),
            A(label, cls="legend-label"),
            hx_get=f"{path}/hide_line?runIDs={runIDs}&curveID={curveID}",
            cls="legend-line"
        )

def Legend(session, labels: list[tuple], path: str, selected_rows_key: str):
    if selected_rows_key in session and "selected-rows" in session[selected_rows_key] and len(session[selected_rows_key]["selected-rows"]) > 0:
        runIDs = session[selected_rows_key]["selected-rows"]
        runIDs = ','.join([str(i) for i in runIDs])
    else:
        print("Warning: no selected lines")
        runIDs = ""

    labels = [(label[0], label[0], label[1], label[2]) if len(label) == 3 else (label[0], label[1], label[2], label[3]) for label in labels]

    return Div(
        H2("Legend", cls="chart-legend-title"),
        Ul(
            *[LegendLine(session, runIDs, label, curve_id, color, hidden, path=path) for label, curve_id, color, hidden in labels],
            cls="chart-legend",
            id=f"chart-legend-{runIDs}"
        ),
        cls="chart-toolbox",
    )