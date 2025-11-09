from fasthtml.common import *
from starlette.responses import Response
from typing import *
from deepboard.gui.components import Modal, SplitSelector, StatLine, ArtefactGroup, StatCell, ArtefactHeader

def _is_allowed(fragment: dict, filters: Optional[dict[str, List[str]]]) -> bool:
    if filters is None:
        return True

    for key, unallowed_values in filters.items():
        if key not in fragment:
            raise ValueError(f"Invalid filter key: {key}! Available keys are 'tag', 'epoch', 'run_rep'.")

        if str(fragment[key]) in unallowed_values:
            return False
    return True

class ImagesStats(NamedTuple):
    steps: List[int]
    epochs: List[int]
    tags: List[str]
    reps: List[int]

def _get_images(socket, type: Literal["IMAGE", "PLOT"]):
    if type == "IMAGE":
        images = socket.get_images()
    else:
        images = socket.get_figures()

    steps = list({img["step"] for img in images})
    epochs = list({img["epoch"] for img in images})
    tags = list({img["tag"] for img in images})
    reps = list({img["run_rep"] for img in images})
    steps = [s for s in steps if s is not None]
    steps.sort()
    epochs = [e for e in epochs if e is not None]
    epochs.sort()
    tags = [t for t in tags if t is not None]
    tags.sort()
    reps = [r for r in reps if r is not None]
    reps.sort()
    return images, ImagesStats(steps, epochs, tags, reps)


def ImageComponent(image_id: int):
    """
    Create a single image component with a specific style.
    :return: Div containing the image.
    """
    return Div(
        A(
            Img(src=f"/images/id={image_id}", alt="Image"),
            hx_get=f"/images/open_modal?id={image_id}",
            hx_target="#modal",
            hx_swap="outerHTML",
            style='cursor: pointer;',
        ),
        cls="image",
    )

def InteractiveImage(image_id: int):
    return Div(
        Div(
            Div(
                Img(src=f"/images/id={image_id}", alt="Image"),
                cls="interactive-image",
                id="zoomableDiv",
                # style="transition: transform 0.1s ease-out;"
            ),
            cls="interactive-image-container",
            style="overflow: hidden; position: relative; user-select: none; touch-action: none;"
        ),
        Script("""
    var elem = document.getElementById('zoomableDiv');

    if (elem) {
        const panzoom = Panzoom(elem, {
            maxScale: 5,
            minScale: 0.25,
            step: 0.125,
            animate: false,
            cursor: 'move',
            pinchAndPan: true
        });

        // Enable mouse wheel zoom
        elem.parentElement.addEventListener('wheel', panzoom.zoomWithWheel);
    }
            """),
    )



def ImageCard(tag: str, step: int, epoch: Optional[int], run_rep: int, images):
    return Div(
        ArtefactGroup(*[ImageComponent(img_id) for img_id in images]),
        Div(
            StatCell("Tag", tag) if tag is not None else None,
            StatCell("Step", str(step)) if step is not None else None,
            StatCell("Epoch", str(epoch)) if epoch is not None else None,
            StatCell("Run Rep", str(run_rep)) if run_rep is not None else None,
            cls="artefact-card-footer",
        ),
        id=f"artefact-card-{step}-{epoch}-{run_rep}",
        cls="artefact-card",
    )

def ImageTab(session, runID, type: Literal["IMAGE", "PLOT"], swap: bool = False):
    from __main__ import rTable
    filters = session.get("artefact-filters", {}).get(type, {})
    socket = rTable.load_run(runID)

    images, stats = _get_images(socket, type=type)
    index = []

    for image in images:
        idx = (image["tag"], image["step"], image["epoch"], image["run_rep"])
        if idx not in index:
            index.append(idx)

    grouped = {}
    for image in images:
        if not _is_allowed(image, filters):
            continue
        idx = (image["tag"], image["step"], image["epoch"], image["run_rep"])
        if idx not in grouped:
            grouped[idx] = []
        grouped[idx].append(image["id"])

    return Div(
        ArtefactHeader(session, type=type),
        *[
            ImageCard(
                tag,
                step,
                epoch if len(stats.epochs) > 1 else None,
                run_rep if len(stats.reps) > 1 else None,
                image_group
            )
            for (tag, step, epoch, run_rep), image_group in grouped.items()
        ],
        style="display; flex; flex-direction: column; align-items: center; justify-content: center;",
        id="images-tab",
        hx_swap_oob="true" if swap else None,
    )


def images_enable(runID, type: Literal["IMAGES", "PLOT"]):
    """
    Check if some scalars are logged and available for the runID. If not, we consider disable it.
    :param runID: The runID to check.
    :return: True if scalars are available, False otherwise.
    """
    from __main__ import rTable
    socket = rTable.load_run(runID)
    if type == "IMAGES":
        return len(socket.get_images()) > 0
    else:
        return len(socket.get_figures()) > 0

# routes
def build_images_routes(rt):
    rt("/images/id={image_id}")(load_image)
    rt("/images/open_modal")(open_image_modal)


def load_image(image_id: int):
    from __main__ import rTable
    img = rTable.get_image_by_id(image_id)
    if img is None:
        return Response(f"Image not found with id: {image_id}:(", status_code=404)
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)

    return Response(
        content=img_buffer.getvalue(),
        media_type="image/png"
    )

def open_image_modal(session, id: int):
    return Modal(
        InteractiveImage(
            id
        ),
        active=True,
    )