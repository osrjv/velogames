import time

try:
    from importlib import metadata
except ImportError:
    import importlib_metadata as metadata

from colorama import Style, Fore
from velogames import console, state
from velogames.typer import typer, Typer
from velogames.commands import league, riders, optimal

DOC = f"""\
Velogames CLI 🚴

A command-line tool for parsing data from
{Fore.BLUE + Style.BRIGHT}https://velogames.com{Fore.RESET + Style.RESET_ALL},
and outputting it into various formats for further processing.
"""

app = Typer()

# Subcommands
app.add_typer(league.app)

# Commands
app.command("riders")(riders.list_all)
app.command("optimal")(optimal.solve)


def handle_result(*args, **kwargs):
    # pylint: disable=unused-argument
    duration = time.monotonic() - state["start_time"]
    console.print(f"\nFinished in {int(duration * 1000)} ms")


def handle_version(value: bool):
    if value:
        console.print(metadata.version("velogames"), highlight=False)
        raise typer.Exit()


@app.callback(result_callback=handle_result)
def main(
    # fmt: off
    url: str = typer.Option(
        state["url"],
        "--url",
        "-u",
        help="Base URL for current game.",
    ),
    verbose: bool = typer.Option(
        state["verbose"],
        "--verbose",
        "-v",
        help="Be more talkative.",
    ),
    version: bool = typer.Option(
        False,
        "--version",
        callback=handle_version,
        is_eager=True,
        show_default=False,
        help="Print version and exit.",
    ),
    # fmt: on
):
    # pylint: disable=unused-argument
    state["url"] = url
    state["verbose"] = verbose
    state["start_time"] = time.monotonic()


main.__doc__ = DOC

if __name__ == "__main__":
    main()
