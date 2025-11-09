from typing import *
from fasthtml.common import *
from .components import CompareSetup, ChartCardList


def ComparePage(session, run_ids: str):
    run_ids = run_ids.split(",")
    session["compare"] = {"selected-rows": run_ids}
    return (Title("Compare"),
            Div(id="custom-menu"),
            Div(
                Div(
                    CompareSetup(session),
                    cls="compare-setup-container"
                ),
                Div(
                    ChartCardList(session),
                    cls="cards-list-container"
                ),
                cls="compare-container"
            )
            )