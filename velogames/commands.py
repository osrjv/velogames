import logging
from typing import List, Dict, Any
from velogames.parser import LeagueParser, TeamParser

Rows = List[Dict[str, Any]]


def _teams(url: str, league_id: str) -> Rows:
    league = LeagueParser(url, league_id)

    title = league.title()
    logging.info("Parsing teams from league: %s", title)

    standings = league.standings()
    logging.info("Found %s teams", len(standings))

    teams = []
    for standing in standings:
        team = TeamParser(url, standing.team_id)
        overview = team.overview()
        teams.append(overview)

        logging.info("Parsed team: %s", overview.name)

    return [team.dict() for team in teams]


def _riders(url: str, league_id: str) -> Rows:
    league = LeagueParser(url, league_id)

    title = league.title()
    logging.info("Parsing picked riders from league: %s", title)

    standings = league.standings()
    logging.info("Found %s teams", len(standings))

    data = []
    for standing in standings:
        team = TeamParser(url, standing.team_id)
        overview = team.overview()
        riders = team.riders()

        for rider in riders:
            data.append({"team_id": overview.team_id, **rider.dict()})

        logging.info("Parsed team: %s", overview.name)

    return data


def _scores(url: str, league_id: str) -> Rows:
    league = LeagueParser(url, league_id)

    title = league.title()
    logging.info("Parsing score breakdowns from league: %s", title)

    stages = league.stages()
    logging.info("Found %s stage options", len(stages))

    data = []
    for stage in stages:
        stage_data = {"stage_id": stage.stage_id, "stage_name": stage.name}
        standings = league.standings(stage)

        for standing in standings:
            data.append({**stage_data, **standing.dict()})

        logging.info("Parsed stage: %s", stage.name)

    return data


COMMANDS = {
    "teams": _teams,
    "riders": _riders,
    "scores": _scores,
}
