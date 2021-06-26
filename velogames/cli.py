import click
from velogames.parser import LeagueParser, TeamParser

LEAGUE_ID = "805863053"


@click.command()
def run():
    league = LeagueParser(LEAGUE_ID)

    title = league.title()
    print(title)

    stages = league.stages()
    print(stages)

    standings = league.standings()
    print(standings)

    for standing in standings:
        team = TeamParser(standing.tid)

        overview = team.overview()
        print(overview)

        riders = team.riders()
        print(riders)


if __name__ == "__main__":
    run()
