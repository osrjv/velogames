# pylint: disable=invalid-name
from typing import Optional, List, Any
from velogames import session
from velogames.utils import get_param
from velogames.models import Team, RiderBase


class Rider(RiderBase):
    stage: int
    general: int
    daily: int
    kom: int
    sprint: int
    summit: int
    breakaway: int
    assist: int


def _maybe_int(val: Any) -> Any:
    if val == "-":
        return 0
    try:
        return int(val)
    except ValueError:
        return val


def overview(team_id: str, stage_id: Optional[str] = None) -> Team:
    parser = session.fetch("teamroster.php", params={"tid": team_id, "st": stage_id})

    li = parser.find(class_="popular-posts").find_all("li")

    name = li[0].span.b.text
    user = li[0].span.find(text=True, recursive=False)
    country = li[0].time.text
    cost = li[1].b.text
    score = li[2].b.text
    rank = li[2].time.text.split()[-3]

    if user is None:
        raise ValueError(f"Invalid team id: {team_id}")

    team = Team(
        team_id=team_id,
        name=name,
        user=user,
        country=country,
        cost=cost,
        score=score,
        rank=rank,
    )

    return team


def riders(team_id: str, stage_id: Optional[str] = None) -> List[Rider]:
    parser = session.fetch("teamroster.php", params={"tid": team_id, "st": stage_id})

    tr = parser.find("table", class_="responsive").find_all("tr")

    header = [th.find(text=True, recursive=False) for th in tr[0].find_all("th")]
    header = [th for th in header if th.strip()]
    header.insert(0, "Rider")

    result = []
    for element in tr[1:]:
        td = element.find_all("td")

        link = td[0].a.get("href")
        values = [_maybe_int(elem.text) for elem in td]
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
        result.append(rider)

    return result
