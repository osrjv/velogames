from typing import List
from colorama import Fore

from velogames.typer import typer
from velogames.parsers import riders as parser
from velogames.models import field_enum
from velogames.utils import print_table


RiderFields = field_enum(parser.Rider)


def list_all(
    # fmt: off
    count: int = typer.Option(
        20,
        "--count",
        "-c",
        help="Maximum number of riders to show.",
    ),
    sort: RiderFields = typer.Option(
        None,
        "--sort",
        "-s",
        help="Sort column by given field.",
        case_sensitive=False,
    ),
    reverse: bool = typer.Option(
        False,
        "--reverse",
        "-r",
        help=f"Reverse sorted order, if {Fore.YELLOW}sort{Fore.RESET} given.",
    ),
    hide: List[RiderFields] = typer.Option(
        [],
        "--hide",
        "-h",
        help="Hide column from output.",
    ),
    # fmt: on
):
    """List all riders participating in the current game."""
    print_table(
        "Riders",
        parser.list_all(),
        sort=sort.value if sort is not None else None,
        reverse=reverse if sort is not None else True,
        hide=hide,
        count=count,
        positions=sort is None,
    )
