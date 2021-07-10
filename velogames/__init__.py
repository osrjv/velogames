from rich import pretty, traceback
from rich.console import Console
from velogames.session import Session

state = {
    "url": "https://www.velogames.com/spain/2021/",
    "verbose": False,
}

traceback.install()
pretty.install()

console = Console()
session = Session(state)
