from fasthtml.common import *

def LogSelector(session, path: str, selected_rows_key: str, session_path: str):
    if selected_rows_key in session and "selected-rows" in session[selected_rows_key] and len(session[selected_rows_key]["selected-rows"]) > 0:
        runIDs = session[selected_rows_key]["selected-rows"]
        runIDs = ','.join([str(i) for i in runIDs])
    else:
        print("Warning: no selected lines")
        runIDs = ""

    if "chart_scale" not in session[session_path]:
        session[session_path]["chart_scale"] = "default"
    type = session[session_path]["chart_scale"]
    return Div(
        H2("Log Scale", cls="setup-title"),
        Input(type="checkbox", name="log scale", id=f"chart-scale-{runIDs}", value="scale", cls="chart-type-checkbox",
              checked=type == "log", hx_get=f"{path}/change_scale?runIDs={runIDs}&log={type == 'log'}",
              hx_swap="outerHTML", hx_target="#chart-scale-selector"),
        style="display: flex; flex-direction: row; align-items: center; justify-content: space-between; width: 100%;",
        id="chart-scale-selector"
    )