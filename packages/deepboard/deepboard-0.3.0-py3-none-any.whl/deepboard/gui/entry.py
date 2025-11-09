import runpy
import os
import sys


def main():
    try:
        import fasthtml  # or whatever dependency is required
    except ImportError:
        raise ImportError(
            "The GUI feature requires additional dependencies. Please install with:\n"
            "  pip install deepboard[full]"
        )
    if os.path.dirname(__file__) not in sys.path:
        sys.path.insert(0, os.path.dirname(__file__))
    script_path = os.path.join(os.path.dirname(__file__), "main.py")
    runpy.run_path(script_path, run_name="__main__")


if __name__ == "__main__":
    main()