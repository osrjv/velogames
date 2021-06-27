import argparse
import csv
import logging
from velogames.commands import COMMANDS, Rows

DESCRIPTION = """\
Velogames data scraper

parses data from velogames.com and outputs it into a CSV file
for further processing

possible output commands:

  teams:  parse all teams in a league
  riders: parse all selected riders in the league
  scores: parse scores for all different events in the league
"""


def to_csv(rows: Rows, path: str) -> None:
    fields = list(rows[0].keys())

    with open(path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    logging.info("Wrote %d rows to file: %s", len(rows), path)


def main() -> None:
    # fmt: off
    parser = argparse.ArgumentParser(
        description=DESCRIPTION,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "command",
        choices=COMMANDS,
        help="command",
    )
    parser.add_argument(
        "league_id",
        help="league ID from URL",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default="output.csv",
        help="output path (default: %(default)s)",
    )
    parser.add_argument(
        "-u",
        "--url",
        default="https://www.velogames.com/velogame/2021/",
        help="base URL for parsed game (default: %(default)s)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="be more talkative",
    )
    args = parser.parse_args()
    # fmt: on

    log_datefmt = "%H:%M:%S"
    log_format = "%(asctime)s.%(msecs)03d › %(levelname)s › %(message)s"
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format=log_format, datefmt=log_datefmt)

    func = COMMANDS[args.command]
    data = func(args.url, args.league_id)

    # TODO: Add other output formats
    to_csv(data, args.path)


if __name__ == "__main__":
    main()
