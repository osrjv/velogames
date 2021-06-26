import argparse
import csv

from velogames import commands

COMMANDS = {
    "teams": commands.teams,
    "riders": commands.riders,
    "scores": commands.scores,
}

DESCRIPTION = """\
Velogames data scraper

Parses data from velogames.com and outputs it into a CSV file
for further processing.

Possible output commands:

    teams:  Parse all teams in a league
    riders: Parse all selected riders in the league
    scores: Parse scores for all different events in the league
"""


def to_csv(rows, path):
    with open(path, "w", newline="", encoding="utf-8") as fd:
        fields = rows[0].keys()
        writer = csv.DictWriter(fd, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to file: {path}")


def main():
    parser = argparse.ArgumentParser(
        description=DESCRIPTION, formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument("command", choices=COMMANDS, help="command")
    parser.add_argument("league_id", help="league ID from URL")
    parser.add_argument(
        "path",
        help="output path (default: output.csv)",
        nargs="?",
        metavar="[path]",
        default="output.csv",
    )

    args = parser.parse_args()

    func = COMMANDS[args.command]
    data = func(args.league_id)
    to_csv(data, args.path)


if __name__ == "__main__":
    main()
