"""Launch the existing game from its asset directory."""
import os
from pathlib import Path
import runpy


def launch():
    root = Path(__file__).resolve().parent
    os.chdir(root)
    runpy.run_path(str(root / "home.py"), run_name="__main__")


if __name__ == "__main__":
    launch()
