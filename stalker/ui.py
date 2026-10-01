"""Terminal output helpers: colors, banner and key/value tables."""

from __future__ import annotations

import os
import sys

from stalker import __version__
from stalker.i18n import t

_color_enabled = True


def setup_console(color: bool = True) -> None:
    """Make the console UTF-8 and ANSI capable (Windows needs a nudge for both)."""
    global _color_enabled
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    if os.name == "nt":
        # An empty `os.system` call switches the Windows console into VT (ANSI) mode.
        os.system("")

    _color_enabled = (
        color
        and "NO_COLOR" not in os.environ
        and hasattr(sys.stdout, "isatty")
        and sys.stdout.isatty()
    )


def _paint(code: str):
    def apply(text) -> str:
        text = str(text)
        return f"\033[{code}m{text}\033[0m" if _color_enabled else text

    return apply


red = _paint("91")
green = _paint("92")
yellow = _paint("93")
blue = _paint("94")
magenta = _paint("95")
cyan = _paint("96")
bold = _paint("1")
dim = _paint("2")


BANNER = r"""
 ███████╗████████╗ █████╗ ██╗     ██╗  ██╗███████╗██████╗
 ██╔════╝╚══██╔══╝██╔══██╗██║     ██║ ██╔╝██╔════╝██╔══██╗
 ███████╗   ██║   ███████║██║     █████╔╝ █████╗  ██████╔╝
 ╚════██║   ██║   ██╔══██║██║     ██╔═██╗ ██╔══╝  ██╔══██╗
 ███████║   ██║   ██║  ██║███████╗██║  ██╗███████╗██║  ██║
 ╚══════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝"""


def clear_screen() -> None:
    if sys.stdout.isatty():
        os.system("cls" if os.name == "nt" else "clear")


def print_banner() -> None:
    print(magenta(BANNER))
    print(f"  {cyan(t('app.tagline'))}  {dim(t('app.version', version=__version__))}\n")


def section(title: str) -> None:
    line = "─" * (len(title) + 4)
    print()
    print(cyan(f"┌{line}┐"))
    print(cyan("│  ") + bold(title) + cyan("  │"))
    print(cyan(f"└{line}┘"))


def kv_table(rows: list[tuple[str, object]]) -> None:
    """Print aligned `label : value` rows; empty values become a dash."""
    if not rows:
        return
    width = max(len(label) for label, _ in rows)
    for label, value in rows:
        if value is None or value == "" or value == []:
            value = t("common.none")
        print(f"  {label.ljust(width)} : {green(value)}")


def info(msg: str) -> None:
    print(f"{blue('[*]')} {msg}")


def success(msg: str) -> None:
    print(f"{green('[+]')} {msg}")


def warn(msg: str) -> None:
    print(f"{yellow('[!]')} {msg}")


def error(msg: str) -> None:
    print(f"{red('[x]')} {msg}", file=sys.stderr)


def note(msg: str) -> None:
    print(dim(f"  {msg}"))
