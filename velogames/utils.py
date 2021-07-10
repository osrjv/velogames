import csv
from typing import Any, List, Dict, Optional
from urllib.parse import urlparse, parse_qs
from rich.table import Table, box

from velogames import console
from velogames.models import Model

Record = Dict[str, Any]


def get_param(uri: str, key: str, default: Any = None) -> Any:
    params = parse_qs(urlparse(uri).query)
    try:
        return params[key][0]
    except KeyError:
        return default


def write_csv(rows: List[Record], path: str) -> None:
    fields = list(rows[0].keys())

    with open(path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def print_table(
    title: str,
    rows: List[Model],
    sort: Optional[str] = None,
    reverse: bool = False,
    hide: List[str] = None,
    positions: bool = False,
    count: int = None,
):
    # pylint: disable=too-many-arguments
    if sort is not None:
        rows.sort(reverse=reverse, key=lambda r: getattr(r, str(sort)))
        title += f" (sorted by {sort.title()})"
    else:
        rows.sort(reverse=reverse)

    exclude = set(hide) if hide is not None else set()
    rows = [row.dict(exclude=exclude) for row in rows]

    table = Table(
        box=box.HORIZONTALS,
        show_header=True,
        header_style="cyan",
        title=title,
    )

    if positions:
        table.add_column("Position")

    for key in rows[0].keys():
        name = key.title()
        if sort is not None and sort == key:
            name = f"[bold]{name}"
        table.add_column(name)

    for index, row in enumerate(rows):
        if count is not None and index >= count:
            break

        values = [str(value) for value in row.values()]
        if positions:
            position = str(index + 1)
            if index < 3:
                position += [" 🥇", " 🥈", " 🥉"][index]
            values.insert(0, position)

        table.add_row(*values)

    console.print()
    console.print(table)
