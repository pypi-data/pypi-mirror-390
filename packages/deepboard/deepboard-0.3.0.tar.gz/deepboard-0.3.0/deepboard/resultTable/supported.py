from typing import Tuple, Optional
from ..__version__ import __version__
from packaging.version import Version

def is_table_supported(version: Optional[str]) -> tuple[bool, str]:
    """
    Check if the given database version is supported by the current Deepboard version.
    :param version: The found database version.
    :return: True if supported, False otherwise along with an error message.
    """
    # Older versions did not have a version stored
    if version is None:
        return False, "No database version found. Please downgrade your Deepboard installation to 0.2.3 or earlier"

    version = Version(version)
    current = Version(__version__)
    # Version is stored from 0.3.0 onwards
    if version.major == 0 and version.minor == 3:
        return True, ""
    else:
        return False, (f"The ResultTable database with version {version} is not supported by Deepboard version "
                       f"{current}. Please upgrade your Deepboard installation.")

