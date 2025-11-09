from typing import *
from datetime import datetime, timedelta
from fasthtml.common import *
from markupsafe import Markup

def CopyToClipboard(text: str, cls, top_right: bool = False):
    return Div(
        Pre(Markup(text), cls='copy-text' + ' ' + cls),
        Span(
            Span(
                I(cls=f'fas fa-copy copy-icon default-icon {cls}'),
                I(cls=f'fas fa-check copy-icon check-icon {cls}'),
                cls='copy-icon-container',
            ),
            style="position: absolute; top: 0em; right: 0em;" if top_right else ""
        ),
        onclick='copyToClipboard(this)',
        style="width: 100%;",
        cls='copy-container'
    )

def ConfigView(runID: int):
    from __main__ import rTable

    # Config
    cfg_text = rTable.get_config(runID)

    # Cli
    row = rTable.get_experiment_raw(runID)
    command_line = row["command"]
    if row['cli'] == "":
        lines = []
    else:
        cli = {keyvalue.split("=")[0]: "=".join(keyvalue.split("=")[1:]) for keyvalue in row['cli'].split(" ")}
        # lines = [P(Markup(f"- {key}: {value}"), cls="config-part") for key, value in cli.items()]
        lines = "\n".join(f"- {key}: {value}" for key, value in cli.items())
    return Div(
        Div(
            H2("Configuration"),
            Div(
                # *cfg,
                CopyToClipboard(cfg_text, cls="raw-file-view", top_right=True), # , cls="raw-file-view"),
                cls="file-view",
            )
        ) if cfg_text is not None else None,
        Div(
            H2("Cli"),
            Div(
                Pre(Markup(lines), cls='raw-file-view'),
                cls="file-view",
            ) if len(lines) > 0 else None,

            Div(
                CopyToClipboard(command_line, cls="raw-file-view"),
                cls="file-view",
                style="margin-top: 2em;"
            )
        )
    )