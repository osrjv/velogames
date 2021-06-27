# pylint: disable=invalid-name
from functools import lru_cache
from typing import Any, Optional, List
from urllib.parse import urlparse, parse_qs, urljoin

import requests
from bs4 import BeautifulSoup  # type: ignore
from velogames.containers import Stage, Standing, Team, Rider


@lru_cache(maxsize=None)
def to_parser(url: str) -> BeautifulSoup:
    response = requests.get(url)
    response.raise_for_status()
    return BeautifulSoup(response.text, features="html.parser")


def get_param(uri: str, key: str, default: Any = None) -> Any:
    params = parse_qs(urlparse(uri).query)
    try:
        return params[key][0]
    except KeyError:
        return default


def maybe_int(val: Any) -> Any:
    if val == "-":
        return 0
    try:
        return int(val)
    except ValueError:
        return val


class LeagueParser:
    def __init__(self, url: str, lid: str):
        self.url = url
        self.lid = lid

    def parser(self, stage: Optional[Stage] = None) -> BeautifulSoup:
        query = f"leaguescores.php?league={self.lid}"

        if stage is not None and stage.stage_id is not None:
            query += f"&ga={stage.game_id}&st={stage.stage_id}"

        url = urljoin(self.url, query)
        parser = to_parser(url)

        return parser

    def title(self) -> str:
        parser = self.parser()
        return parser.find("h4", class_="teamtitle").text or ""

    def stages(self) -> List[Stage]:
        parser = self.parser()

        links = parser.find(class_="wrap-content").find_all("a")

        stages = []
        for a in links:
            name = a.text

            link = a.get("href")
            game_id = get_param(link, "ga")
            stage_id = get_param(link, "st")

            stage = Stage(name=name, game_id=game_id, stage_id=stage_id)
            stages.append(stage)

        return stages

    def standings(self, stage: Optional[Stage] = None) -> List[Standing]:
        parser = self.parser(stage)

        rows = parser.find(id="users").ul.find_all("li", recursive=False)

        standings = []
        for li in rows:
            name = li.find(class_="name").text
            user = li.find(class_="born", recursive=False).text
            score = int(li.find(style="float:right").text)

            link = li.find(class_="name").a.get("href")
            team_id = get_param(link, "tid")

            standing = Standing(team_id=team_id, name=name, user=user, score=score)
            standings.append(standing)

        return standings


class TeamParser:
    def __init__(self, url: str, team_id: str):
        self.url = url
        self.team_id = team_id

    def parser(self, stage: Optional[Stage] = None) -> BeautifulSoup:
        query = f"teamroster.php?tid={self.team_id}"

        if stage is not None and stage.stage_id is not None:
            query += f"&ga={stage.game_id}&st={stage.stage_id}"

        url = urljoin(self.url, query)
        parser = to_parser(url)

        return parser

    def overview(self, stage: Optional[Stage] = None) -> Team:
        parser = self.parser(stage)

        li = parser.find(class_="popular-posts").find_all("li")

        name = li[0].span.b.text
        user = li[0].span.find(text=True, recursive=False)
        country = li[0].time.text
        cost = li[1].b.text
        score = li[2].b.text
        rank = li[2].time.text.split()[-3]

        team = Team(
            team_id=self.team_id,
            name=name,
            user=user,
            country=country,
            cost=cost,
            score=score,
            rank=rank,
        )

        return team

    def riders(self, stage: Optional[Stage] = None) -> List[Rider]:
        parser = self.parser(stage)

        tr = parser.find("table", class_="responsive").find_all("tr")

        header = [th.find(text=True, recursive=False) for th in tr[0].find_all("th")]
        header = [th for th in header if th.strip()]
        header.insert(0, "Rider")

        riders = []
        for element in tr[1:]:
            td = element.find_all("td")

            link = td[0].a.get("href")
            values = [maybe_int(elem.text) for elem in td]
            row = {column: values[idx] for idx, column in enumerate(header)}

            rider = Rider(
                rider_id=get_param(link, "rider"),
                name=row["Rider"],
                team=row["Team"],
                cost=row["Cost"],
                points=row["Tot"],
                stage=row["Stg"],
                general=row["GC"],
                daily=row["PC"],
                kom=row["KOM"],
                sprint=row["Spr"],
                summit=row["Sum"],
                breakaway=row["Bky"],
                assist=row["Ass"],
            )
            riders.append(rider)

        return riders
