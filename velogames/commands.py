from typing import List, Dict, Any
from velogames.parser import LeagueParser, TeamParser

Rows = List[Dict[str, Any]]


def _teams(url: str, league_id: str) -> Rows:
    league = LeagueParser(url, league_id)

    title = league.title()
    print(f"Parsing teams from league: {title}")

    standings = league.standings()
    print(f"Found {len(standings)} teams")

    teams = []
    for standing in standings:
        team = TeamParser(url, standing.team_id)
        overview = team.overview()
        teams.append(overview)
        print(f"Parsed team: {overview.name}")

    return [team.dict() for team in teams]


def _riders(url: str, league_id: str) -> Rows:
    league = LeagueParser(url, league_id)

    title = league.title()
    print(f"Parsing picked riders from league: {title}")

    standings = league.standings()
    print(f"Found {len(standings)} teams")

    data = []
    for standing in standings:
        team = TeamParser(url, standing.team_id)
        overview = team.overview()
        riders = team.riders()
        data.extend([{"team_id": overview.team_id, **rider.dict()} for rider in riders])
        print(f"Parsed team: {overview.name}")

    return data


def _scores(url: str, league_id: str) -> Rows:
    league = LeagueParser(url, league_id)

    title = league.title()
    print(f"Parsing score breakdowns from league: {title}")

    stages = league.stages()
    print(f"Found {len(stages)} stage options")

    data = []
    for stage in stages:
        standings = league.standings(stage)
        extras = {"stage_id": stage.stage_id, "stage_name": stage.name}
        data.extend([{**extras, **standing.dict()} for standing in standings])
        print(f"Parsed stage: {stage.name}")

    return data


COMMANDS = {
    "teams": _teams,
    "riders": _riders,
    "scores": _scores,
}
