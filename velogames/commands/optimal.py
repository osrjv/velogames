from colorama import Style
from rich.console import RenderGroup
from rich.live import Live
from rich.table import Table, box

from velogames import console
from velogames.typer import typer
from velogames.parsers import riders as parser
from velogames.solver import Solver


def _create_table(team):
    table = Table(
        box=box.HORIZONTALS,
        show_header=True,
        header_style="bold #5f5fff",
        title="Optimal team",
    )

    schema = parser.Rider.schema()
    for prop in schema["properties"].values():
        table.add_column(prop["title"])

    for rider in team:
        values = (str(v) for v in rider.dict().values())
        table.add_row(*values)

    return table


def solve(
    generations: int = typer.Option(
        10000,
        "--generations",
        "-g",
        help="Number of generations to run solver.",
    ),
):
    riders = parser.list_all()
    state = None

    try:
        solver = Solver(riders, generations)
        with Live(console=console, screen=True, refresh_per_second=4) as live:
            for gen, team in solver.iter():
                state = RenderGroup(
                    "",
                    _create_table(team),
                    "",
                    f"Generation: {gen}/{generations or 'Unknown'}",
                    f"Points: {sum(r.points for r in team)}",
                    f"Cost: {sum(r.cost for r in team)}/100",
                )
                live.update(RenderGroup(state, "", "Press Ctrl-C to stop search"))
    except KeyboardInterrupt:
        pass

    if state:
        console.print(state)


solve.__doc__ = f"""\
Attempt to create the optimal team.

Uses the scores up to this point in the race to create an ideal
composition of rider picks.

{Style.BRIGHT}Note{Style.RESET_ALL}: The feature is experimental and might not
always resolve the best possible picks.
"""
