from fasthtml.common import *
from typing import Optional, List

def ArtefactFilterOptions(shown: bool, type: str, swap: bool = False):
    if shown:
        hx_options = dict(
            hx_trigger="outsideClick",
            hx_swap="outerHTML",
            hx_get=f"/show_filter_artefacts_options?show=False&type={type}",
        )
    else:
        hx_options = {}

    return Ul(
            Li("Tag", cls="menu-item", hx_get=f"/add_filter_artefacts?filter_by=tag&type={type}", hx_target="#windowed-modal", hx_swap="outerHTML"),
            Li("Epoch", cls="menu-item", hx_get=f"/add_filter_artefacts?filter_by=epoch&type={type}", hx_target="#windowed-modal", hx_swap="outerHTML"),
            Li("Run Repetition", cls="menu-item", hx_get=f"/add_filter_artefacts?filter_by=reps&type={type}", hx_target="#windowed-modal", hx_swap="outerHTML"),
            cls="artefact-filter-options" + (" hidden" if not shown else ""),
            id=f"artefact-filter-options-{type}",
            hx_swap_oob="true" if swap else None,
        **hx_options
        )

def ArtefactHeader(session, type: str, show_options: bool = False):
    filters = session.get("artefact-filters", {}).get(type, {})

    return Div(
        Div(
            Button(
                I(cls="fa-solid fa-filter", style="margin-right: 5px"),
                "Filter",
                hx_get=f"/show_filter_artefacts_options?show={not show_options}&type={type}",
                hx_swap="outerHTML",
                hx_target=f"#artefact-filter-options-{type}",
                cls="artefact-header-button",
            ),
            ArtefactFilterOptions(show_options, type=type),
            style="position: relative",
        ),
        *[
            Button(
                f"{key.capitalize()}",
                I(cls="fa-solid fa-x", style="margin-left: 1em"),
                hx_get=f"/artefact_clear_filter?type={type}&element={key}",
                hx_target="#sp-tab-content",
                cls="artefact-header-button filter"
            )
            for key in filters.keys() if len(filters[key]) > 0
        ],
        cls="artefact-header"
    )