# pylint: disable=invalid-name
import re
from typing import Optional, List

from velogames import session
from velogames.utils import get_param
from velogames.models import Stage, Standing


def _to_parser(league_id: str, stage: Optional[Stage] = None):
    stage_params = {"st": stage.stage_id, "ga": stage.game_id} if stage else {}
    parser = session.fetch(
        "leaguescores.php", params={"league": league_id, **stage_params}
    )

    content = parser.find(class_="single_post").text.strip()
    if re.search(".*League not found.*", content):
        raise ValueError(f"League not found: {league_id}")
    if re.search(".*Unknown column.*", content):
        raise ValueError(f"Invalid request: {content}")

    return parser


def title(league_id: str) -> str:
    parser = _to_parser(league_id)
    return parser.find("h4", class_="teamtitle").text or ""


def stages(league_id: str) -> List[Stage]:
    parser = _to_parser(league_id)

    output = []
    for a in parser.find(class_="wrap-content").find_all("a"):
        name = a.text

        link = a.get("href")
        game_id = get_param(link, "ga")
        stage_id = get_param(link, "st")

        stage = Stage(name=name, game_id=game_id, stage_id=stage_id)
        output.append(stage)

    return output


def standings(league_id: str, stage: Optional[Stage] = None) -> List[Standing]:
    parser = _to_parser(league_id, stage)

    output = []
    for li in parser.find(id="users").ul.find_all("li", recursive=False):
        name = li.find(class_="name").text
        user = li.find(class_="born", recursive=False).text
        score = int(li.find(style="float:right").text)

        link = li.find(class_="name").a.get("href")
        team_id = get_param(link, "tid")

        standing = Standing(team_id=team_id, name=name, user=user, score=score)
        output.append(standing)

    return output
