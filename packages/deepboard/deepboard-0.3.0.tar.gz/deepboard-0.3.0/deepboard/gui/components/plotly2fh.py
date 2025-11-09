from fasthtml.common import *
import json
from uuid import uuid4
from plotly.io import to_json

def plotly2fasthtml_download(chart, callbacks=None, js_options=None):
    """
    Fork of the original plotly2fasthtml to add a download CSV button.
    """
    chart_id = f"uniq-{uuid4()}"
    chart_json = to_json(chart)
    if callbacks:
        for callback in callbacks:
            callback.register_plot(chart_id)

    if js_options is None:
        js_options = {}

    js_options["modeBarButtonsToAdd"] = [{
            'name': 'Download CSV',
            'icon': {
                'width': 857.1,
                'height': 1000,
                'path': 'm214-7h429v214h-429v-214z m500 0h72v500q0 8-6 21t-11 20l-157 156q-5 6-19 12t-22 5v-232q0-22-15-38t-38-16h-322q-22 0-37 16t-16 38v232h-72v-714h72v232q0 22 16 38t37 16h465q22 0 38-16t15-38v-232z m-214 518v178q0 8-5 13t-13 5h-107q-7 0-13-5t-5-13v-178q0-8 5-13t13-5h107q7 0 13 5t5 13z m357-18v-518q0-22-15-38t-38-16h-750q-23 0-38 16t-16 38v750q0 22 16 38t38 16h517q23 0 50-12t42-26l156-157q16-15 27-42t11-49z',
                'transform': 'matrix(1 0 0 -1 0 850)'
            },
            'click': 'clickDownloadCSV'
        }]

    js_options_json = json.dumps(js_options or {})
    # Replace "clickDownloadCSV" with the actual function name
    js_options_json = js_options_json.replace('"clickDownloadCSV"', 'clickDownloadCSV')
    return Div(
        Script(
            f"""
        var plotly_data = {chart_json};
        Plotly.newPlot('{chart_id}', plotly_data.data, plotly_data.layout, {js_options_json});
    """
        ),
        *(callbacks or []),
        id=chart_id,
    )