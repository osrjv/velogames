# pylint: disable=invalid-name
from functools import lru_cache
from urllib.parse import urlparse, parse_qs, urljoin
import requests
from bs4 import BeautifulSoup
from velogames.containers import Stage, Standing, Team, Rider


DEFAULT_URL = "https://www.velogames.com/velogame/2021/"


@lru_cache(maxsize=None)
def to_parser(url):
    response = requests.get(url)
    response.raise_for_status()
    return BeautifulSoup(response.text, features="html.parser")


def get_param(uri, key, default=None):
    params = parse_qs(urlparse(uri).query)
    try:
        return params[key][0]
    except KeyError:
        return default


def maybe_int(val):
    if val == "-":
        return 0
    try:
        return int(val)
    except ValueError:
        return val


class LeagueParser:
    def __init__(self, lid: str, url: str = DEFAULT_URL):
        self.lid = lid
        self._url = url

    def url(self, stage=None):
        uri = f"leaguescores.php?league={self.lid}"

        if stage is not None and stage.stage_id is not None:
            uri += f"&ga={stage.game_id}&st={stage.stage_id}"

        return urljoin(self._url, uri)

    def parser(self, stage=None):
        url = self.url(stage)
        return to_parser(url)

    def title(self):
        parser = self.parser()
        return parser.find("h4", class_="teamtitle").text

    def stages(self):
        stages = []
        parser = self.parser()

        links = parser.find(class_="wrap-content").find_all("a")
        for a in links:
            name = a.text

            link = a.get("href")
            game_id = get_param(link, "ga")
            stage_id = get_param(link, "st")

            stage = Stage(name=name, game_id=game_id, stage_id=stage_id)
            stages.append(stage)

        return stages

    def standings(self, stage=None):
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
    def __init__(self, team_id: str, url: str = DEFAULT_URL):
        self.team_id = team_id
        self._url = url

    def url(self, stage=None):
        uri = f"teamroster.php?tid={self.team_id}"

        if stage is not None and stage.stage_id is not None:
            uri += f"&ga={stage.game_id}&st={stage.stage_id}"

        return urljoin(self._url, uri)

    def parser(self, stage=None):
        url = self.url(stage)
        return to_parser(url)

    def overview(self, stage=None):
        parser = self.parser(stage)
        li = parser.find(class_="popular-posts").find_all("li")

        name = li[0].span.b.text
        user = li[0].span.find(text=True, recursive=False)
        country = li[0].time.text
        cost = li[1].b.text
        score = li[2].b.text
        rank = li[2].time.text.split()[-1]

        return Team(
            team_id=self.team_id,
            name=name,
            user=user,
            country=country,
            cost=cost,
            score=score,
            rank=rank,
        )

    def riders(self, stage=None):
        parser = self.parser(stage)
        tr = parser.find("table", class_="responsive").find_all("tr")

        header = [th.find(text=True, recursive=False) for th in tr[0].find_all("th")]
        header = [th for th in header if th.strip()]
        header.insert(0, "Rider")

        table = []
        for element in tr[1:]:
            td = element.find_all("td")
            link = td[0].a.get("href")
            values = [maybe_int(elem.text) for elem in td]

            rider = {column: values[idx] for idx, column in enumerate(header)}
            rider["ID"] = get_param(link, "rider")
            table.append(rider)

        riders = []
        for row in table:
            rider = Rider(
                rider_id=row["ID"],
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
