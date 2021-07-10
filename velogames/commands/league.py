"""Parse teams and standings from a league.

The league ID used by commands is visible the URL for each league.
"""
from collections import defaultdict
from typing import Optional
from rich.progress import Progress

from velogames import console
from velogames.models import RiderBase
from velogames.typer import Typer, typer
from velogames.parsers import league, team
from velogames.utils import print_table


app = Typer(name="league", help=__doc__)


class LeagueRider(RiderBase):
    picked: int

    def __lt__(self, other: "LeagueRider") -> bool:
        return (-self.picked, -self.points) > (-other.picked, -other.points)


@app.command()
def stages(league_id: str):
    """List all available stages."""
    print_table("Stages", league.stages(league_id))


@app.command()
def teams(league_id: str):
    """List all participating teams."""
    title = league.title(league_id)
    console.print(f"Parsing teams for [cyan]{title}[/cyan]")

    result = []
    with Progress(console=console) as progress:
        rows = league.standings(league_id)
        task = progress.add_task("Parsing...", total=len(rows))

        for row in rows:
            overview = team.overview(row.team_id)
            result.append(overview)
            progress.update(task, advance=1)

    print_table("Teams", result, hide={"team_id"}, sort="score")


@app.command()
def riders(league_id: str):
    title = league.title(league_id)
    console.print(f"Parsing picked riders for [cyan]{title}[/cyan]")

    picks = defaultdict(int)
    with Progress(console=console) as progress:
        rows = league.standings(league_id)
        task = progress.add_task("Parsing...", total=len(rows))

        for row in rows:
            for rider in team.riders(row.team_id):
                picks[rider] += 1
            progress.update(task, advance=1)

    result = []
    for rider, picked in picks.items():
        result.append(LeagueRider(**rider.dict(), picked=picked))

    print_table("Riders", result, sort="value", hide={"rider_id"}, reverse=False)


@app.command()
def standings(
    league_id: str,
    stage_id: Optional[int] = typer.Option(None, help="Individual stage to show."),
):
    """Show current standings in the league."""
    title = league.title(league_id)
    console.print(f"Parsing standings for [cyan]{title}[/cyan]")

    for stage in league.stages(league_id):
        if stage.stage_id == stage_id:
            match = stage
            break
    else:
        raise ValueError(f"No stage with id: {stage_id}")

    result = league.standings(league_id, match)
    print_table(
        f"Standings ({match.name})",
        result,
        hide={"team_id"},
        reverse=True,
        positions=True,
    )


@app.command()
def dump(league_id: str):
    title = league.title(league_id)
    console.print(f"Parsing all standings for [cyan]{title}[/cyan]")
    all_stages = league.stages(league_id)

    result = []
    with Progress(console=console) as progress:
        task = progress.add_task("Parsing...", total=len(all_stages))

        for stage in all_stages:
            for standing in league.standings(league_id, stage):
                fields = {
                    "stage_id": stage.stage_id,
                    "stage_name": stage.name,
                    **standing.dict(),
                }
                result.append(fields)

            progress.update(task, advance=1)

    console.print(result)
    # TODO: write it out
