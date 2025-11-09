from fasthtml.common import *


def Modal(*content, active: bool = False):
    return Div(
        Button(
            I(cls="fas fa-times"),
            hx_get="/close_modal",
            hx_target="#modal",
            hx_swap="outerHTML",
            cls="close-button",
        ) if active else None,
        Div(
            *content,
            cls="modal",
            onclick="event.stopPropagation();",
        ),
        cls="modal-overlay" if active else "modal-overlay hidden",
        id="modal"
    )

def WindowedModal(*content, title: str, closable: bool = True, active: bool = False, swap_oob: bool = False):
    return Div(
        Div(
            Div(
                Button(
                    I(cls="fas fa-times"),
                    hx_get="/close_windowed_modal",
                    hx_target="#windowed-modal",
                    hx_swap="outerHTML",
                    cls="windowed-modal-header-close-button",
                ) if active and closable else None,
                H2(title),
                cls="windowed-modal-header",
            ),
            *content,
            cls="windowed-modal-content",
            onclick="event.stopPropagation();",
        ),
        cls="windowed-modal" if active else "windowed-modal hidden",
        id="windowed-modal",
        hx_swap_oob="true" if swap_oob else None
    )