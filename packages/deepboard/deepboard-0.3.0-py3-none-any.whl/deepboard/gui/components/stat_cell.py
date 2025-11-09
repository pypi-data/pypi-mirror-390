from fasthtml.common import *

def StatCell(label: str, value: str):
    return Span(
        f"{label}: {value}",
        cls="stat-cell"
    )