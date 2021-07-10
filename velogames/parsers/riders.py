# pylint: disable=invalid-name
from typing import Optional
from velogames import session
from velogames.utils import get_param
from velogames.models import RiderBase, Percentage


class Rider(RiderBase):
    role: str
    selected: Optional[Percentage] = None


def list_all():
    parser = session.fetch("riders.php")

    table = parser.find("div", class_="single_post").find("table")
    headers = [th.text.lower() for th in table.find("thead").find_all("th")]

    riders = []
    for tr in table.find("tbody").find_all("tr"):
        values = [td.text for td in tr.find_all("td")]
        fields = dict(zip(headers, values))

        link = tr.a.get("href")
        rider_id = get_param(link, "rider")

        fields["rider_id"] = rider_id
        fields["name"] = fields.pop("rider")
        fields["role"] = fields.pop("class")

        rider = Rider(**fields)
        riders.append(rider)

    return riders
