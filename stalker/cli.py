"""Command line entry point: subcommands for scripting, interactive menu otherwise."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

from stalker import __version__, config, i18n, ui, views
from stalker.core import ip_lookup, my_ip, phone, username
from stalker.i18n import t
from stalker.net import DEFAULT_TIMEOUT, StalkerError


# ---------------------------------------------------------------- helpers

def _save_json(data, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def _run(task, *args, **kwargs):
    """Run a lookup, turning StalkerError into a translated message. Returns None on failure."""
    try:
        return task(*args, **kwargs)
    except StalkerError as exc:
        ui.error(t(exc.key, **exc.params))
        return None


# ---------------------------------------------------------------- interactive menu

def _ask(prompt: str) -> str:
    return input(ui.cyan("  » ") + prompt).strip()


def _offer_save(kind: str, data) -> None:
    answer = _ask(t("common.save_prompt")).lower()
    if answer[:1] == t("common.save_yes"):
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        path = _save_json(data, Path("results") / f"{kind}-{stamp}.json")
        ui.success(t("common.saved", path=path))


def _menu_ip() -> None:
    target = _ask(t("ip.prompt"))
    ui.info(t("common.working"))
    data = _run(ip_lookup.lookup, target or None)
    if data:
        views.show_ip(data)
        _offer_save("ip", data)


def _menu_my_ip() -> None:
    ui.info(t("common.working"))
    data = _run(my_ip.my_ip)
    if data:
        views.show_my_ip(data)


def _menu_phone() -> None:
    number = _ask(t("phone.prompt"))
    if not number:
        return
    data = _run(phone.analyze, number, config.get("region"), i18n.get_language())
    if data:
        views.show_phone(data)
        _offer_save("phone", data)


def _menu_username() -> None:
    name = _ask(t("user.prompt"))
    if not name:
        return
    name = _run(username.normalize, name)
    if name is None:
        return
    ui.info(t("user.checking", count=len(username.SITES)))
    results = _run(username.search, name)
    if results:
        views.show_username(name, results)
        _offer_save("username", {"username": name, "results": results})


def _menu_language() -> None:
    new = "en" if i18n.get_language() == "tr" else "tr"
    i18n.set_language(new)
    config.set("lang", new)
    ui.success(t("menu.lang_changed"))


MENU = (
    ("1", "menu.ip", _menu_ip),
    ("2", "menu.myip", _menu_my_ip),
    ("3", "menu.phone", _menu_phone),
    ("4", "menu.username", _menu_username),
    ("5", "menu.language", _menu_language),
    ("0", "menu.exit", None),
)


def interactive() -> int:
    actions = {key: action for key, _, action in MENU}
    while True:
        ui.clear_screen()
        ui.print_banner()
        print(ui.bold(f"  {t('menu.title')}"))
        for key, label, _ in MENU:
            print(f"  {ui.magenta(f'[{key}]')} {t(label)}")
        print()

        choice = _ask(t("menu.prompt"))
        if choice not in actions:
            ui.warn(t("menu.invalid"))
            input(ui.dim(f"  {t('common.press_enter')}"))
            continue
        action = actions[choice]
        if action is None:
            ui.success(t("common.bye"))
            return 0
        try:
            action()
        except KeyboardInterrupt:
            print()
            ui.warn(t("common.interrupted"))
        print()
        input(ui.dim(f"  {t('common.press_enter')}"))


# ---------------------------------------------------------------- argparse

def build_parser() -> argparse.ArgumentParser:
    # argparse fetches its own texts ("usage:", "options", errors...) via gettext.
    argparse._ = i18n.argparse_gettext
    parser = argparse.ArgumentParser(prog="stalker", description=t("cli.description"))
    parser.add_argument("-V", "--version", action="version", version=f"stalker {__version__}")
    parser.add_argument("--lang", choices=i18n.SUPPORTED, help=t("cli.lang"))
    parser.add_argument("--no-color", action="store_true", help=t("cli.no_color"))

    # Repeated on every subcommand (with SUPPRESS so they don't clobber the
    # top-level values) so `stalker ip 1.1.1.1 --lang tr` works too.
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--lang", choices=i18n.SUPPORTED, default=argparse.SUPPRESS,
                        help=t("cli.lang"))
    common.add_argument("--no-color", action="store_true", default=argparse.SUPPRESS,
                        help=t("cli.no_color"))
    common.add_argument("--json", action="store_true", help=t("cli.json"))
    common.add_argument("-o", "--output", metavar="FILE", help=t("cli.output"))
    common.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT, help=t("cli.arg.timeout"))

    sub = parser.add_subparsers(dest="command", metavar="{ip,myip,phone,user}")

    p = sub.add_parser("ip", parents=[common], help=t("cli.cmd.ip"))
    p.add_argument("address", nargs="?", help=t("cli.arg.ip"))

    sub.add_parser("myip", parents=[common], help=t("cli.cmd.myip"))

    p = sub.add_parser("phone", parents=[common], help=t("cli.cmd.phone"))
    p.add_argument("number", help=t("cli.arg.number"))
    p.add_argument("-r", "--region", help=t("cli.arg.region"))

    p = sub.add_parser("user", parents=[common], help=t("cli.cmd.user"))
    p.add_argument("username", help=t("cli.arg.username"))
    p.add_argument("--found-only", action="store_true", help=t("cli.arg.found_only"))

    return parser


def _pre_scan_lang(argv: list[str]) -> str | None:
    """Read --lang before argparse runs so that --help is already translated."""
    for i, arg in enumerate(argv):
        if arg == "--lang" and i + 1 < len(argv):
            return argv[i + 1]
        if arg.startswith("--lang="):
            return arg.split("=", 1)[1]
    return None


def run_command(args) -> int:
    timeout = args.timeout
    if args.command == "ip":
        data = _run(ip_lookup.lookup, args.address, timeout)
        show = views.show_ip
    elif args.command == "myip":
        data = _run(my_ip.my_ip, timeout)
        show = views.show_my_ip
    elif args.command == "phone":
        data = _run(phone.analyze, args.number, args.region or config.get("region"),
                    i18n.get_language())
        show = views.show_phone
    else:
        name = _run(username.normalize, args.username)
        if name is None:
            return 1
        if not args.json:
            ui.info(t("user.checking", count=len(username.SITES)))
        results = _run(username.search, name, timeout)
        data = {"username": name, "results": results} if results else None
        show = lambda d: views.show_username(d["username"], d["results"], args.found_only)  # noqa: E731

    if data is None:
        return 1
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        show(data)
    if args.output:
        path = _save_json(data, args.output)
        if not args.json:
            ui.success(t("common.saved", path=path))
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    # Priority: --lang flag > STALKER_LANG > saved choice > system language.
    env_lang = os.environ.get("STALKER_LANG", "").lower()
    i18n.set_language(
        _pre_scan_lang(argv)
        or (env_lang if env_lang in i18n.SUPPORTED else None)
        or config.get("lang")
        or i18n.detect_language()
    )

    ui.setup_console(color="--no-color" not in argv)
    args = build_parser().parse_args(argv)

    try:
        if args.command is None:
            return interactive()
        return run_command(args)
    except (KeyboardInterrupt, EOFError):
        print()
        ui.warn(t("common.interrupted"))
        return 130
