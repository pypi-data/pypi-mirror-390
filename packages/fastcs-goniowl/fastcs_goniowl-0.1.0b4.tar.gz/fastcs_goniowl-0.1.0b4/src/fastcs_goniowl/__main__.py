"""Interface for ``python -m fastcs_goniowl``."""

from argparse import ArgumentParser
from collections.abc import Sequence
from pathlib import Path

from fastcs.launch import FastCS
from fastcs.transport.epics.ca.options import EpicsCAOptions
from fastcs.transport.epics.options import (
    EpicsGUIOptions,
    EpicsIOCOptions,
)

from fastcs_goniowl.goniowl_controller import GoniOwlController

from . import __version__

__all__ = ["main"]

OPI_PATH = Path("/epics/opi")


def main(args: Sequence[str] | None = None) -> None:
    """Argument parser for the CLI."""
    parser = ArgumentParser()

    # Positional argument
    parser.add_argument("pv_prefix", type=str, help="Prefix for process variable names")
    parser.add_argument(
        "keras_file_path", type=str, help="Path of keras model file to load"
    )

    # Optional --version flag
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"{__version__}",
        help="Show program version and exit",
    )

    parsed_args = parser.parse_args()
    pv_prefix = parsed_args.pv_prefix
    keras_file_path = parsed_args.keras_file_path

    ui_path = OPI_PATH if OPI_PATH.is_dir() else Path.cwd()

    # Create a controller instance...
    controller = GoniOwlController(keras_file_path=keras_file_path)

    # ...some IOC options...
    options = EpicsCAOptions(
        ca_ioc=EpicsIOCOptions(pv_prefix=pv_prefix),
        gui=EpicsGUIOptions(
            output_path=ui_path / "goniowl.bob", title=f"GoniOwl - {pv_prefix}"
        ),
    )

    # ...and pass them both to FastCS
    launcher = FastCS(controller, [options])
    launcher.create_docs()
    launcher.create_gui()
    launcher.run()


if __name__ == "__main__":
    main()
