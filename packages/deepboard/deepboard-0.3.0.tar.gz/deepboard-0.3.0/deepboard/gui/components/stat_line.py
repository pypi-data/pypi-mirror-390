from fasthtml.common import *

def StatLine(label: str, value: str):
    return Span(
        H3(f"{label}: ", style="font-size: 1em; margin: 0.1em; margin-right: 0.5em; font-weight: bold;"),
        H3(value, style="font-size: 1em; margin: 0.1em; font-weight: normal;"),
        cls="expand"
    )