from .template import RightPanel, fill_panel, reset_scalar_session
from .scalars import build_scalar_routes
from .run_info import build_info_routes
from .images import build_images_routes
from .routes import build_routes as build_rp_routes

def build_right_panel_routes(rt):
    rt("/fillpanel")(fill_panel)
    build_images_routes(rt)
    build_scalar_routes(rt)
    build_info_routes(rt)
    build_rp_routes(rt)
