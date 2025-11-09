from fasthtml.common import *

def ArtefactGroup(*artefacts):
    """
    Create a group of images in a flex container that adapts to the number of images.
    :param images: List of PIL Image objects.
    :return: Div containing the images.
    """
    return Div(
        *artefacts,
        cls="artefact-group-container",
    )