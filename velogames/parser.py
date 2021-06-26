from functools import lru_cache
from urllib.parse import urlparse, parse_qs, urljoin

import requests
from bs4 import BeautifulSoup

from velogames.containers import Stage, Standing, Team


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

        if stage is not None and stage.sid is not None:
            uri += f"&ga={stage.gid}&st={stage.sid}"

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
            gid = get_param(link, "ga")
            sid = get_param(link, "st")

            stage = Stage(name, gid, sid)
            stages.append(stage)

        return stages

    def standings(self, stage=None):
        standings = []
        parser = self.parser(stage)

        rows = parser.find(id="users").ul.find_all("li", recursive=False)
        for li in rows:
            name = li.find(class_="name").text
            user = li.find(class_="born", recursive=False).text
            score = int(li.find(style="float:right").text)

            link = li.find(class_="name").a.get("href")
            tid = get_param(link, "tid")

            standing = Standing(name, user, score, tid)
            standings.append(standing)

        return standings


class TeamParser:
    def __init__(self, tid: str, url: str = DEFAULT_URL):
        self.tid = tid
        self._url = url

    def url(self, stage=None):
        uri = f"teamroster.php?tid={self.tid}"

        if stage is not None and stage.sid is not None:
            uri += f"&ga={stage.gid}&st={stage.sid}"

        return urljoin(self._url, uri)

    def parser(self, stage=None):
        url = self.url(stage)
        return to_parser(url)

    def overview(self, stage=None):
        parser = self.parser(stage)

        li = parser.find(class_="popular-posts").find_all("li")

        name = li[0].span.find(text=True, recursive=False)
        user = li[0].span.b.text
        country = li[0].time.text

        cost = li[1].b.text

        score = li[2].b.text
        rank = li[2].time.text.split()[-1]

        return Team(name, user, country, cost, score, rank, self.tid)

    def riders(self, stage=None):
        parser = self.parser(stage)

        tr = parser.find("table", class_="responsive").find_all("tr")

        header = [th.find(text=True, recursive=False) for th in tr[0].find_all("th")]
        header = [th for th in header if th.strip()]
        header.insert(0, "Rider")

        rows = [[td.text for td in row.find_all("td")] for row in tr[1:]]

        riders = []
        for row in rows:
            rider = {}
            for idx, column in enumerate(header):
                value = row[idx]
                rider[column] = maybe_int(value)
            riders.append(rider)

        return riders
