import typer
import click
from colorama import Fore, Style


def _color(text, color):
    return color + text + Fore.RESET + Style.RESET_ALL


class HelpFormatter(click.HelpFormatter):
    def write_usage(self, prog, args="", prefix="Usage: "):
        super().write_usage(
            prog=_color(prog, Fore.WHITE + Style.BRIGHT),
            args=_color(args, Fore.YELLOW),
            prefix=_color(prefix, Fore.BLUE + Style.BRIGHT),
        )

    def write_heading(self, heading):
        super().write_heading(_color(heading, Fore.BLUE + Style.BRIGHT))

    def write_dl(self, rows, col_max=30, col_spacing=2):
        rows = [(_color(term, Fore.YELLOW), value) for term, value in rows]
        super().write_dl(rows, col_max, col_spacing)


class HelpFormatterMixin:
    # pylint: disable=too-few-public-methods
    def get_help(self, ctx):
        formatter = HelpFormatter(
            width=ctx.terminal_width, max_width=ctx.max_content_width
        )
        self.format_help(ctx, formatter)
        return formatter.getvalue().rstrip("\n")


class Group(HelpFormatterMixin, click.Group):
    pass


class Command(HelpFormatterMixin, click.Command):
    pass


class Typer(typer.Typer):
    def __init__(
        self,
        *args,
        cls=Group,
        context_settings=None,
        add_completion=False,
        **kwargs,
    ) -> None:
        super().__init__(
            *args,
            cls=cls,
            context_settings=context_settings
            or {"help_option_names": ["-h", "--help"]},
            add_completion=add_completion,
            **kwargs,
        )

    def command(self, *args, cls=Command, **kwargs) -> typer.Typer.command:
        return super().command(*args, cls=cls, **kwargs)
