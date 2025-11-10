from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .scaffold import (
    DEFAULT_ASSISTANTS,
    InitResult,
    init_palprompt_structure,
    refresh_prompts,
    update_root_agents_file,
)


def parse_assistants(raw: str | None) -> tuple[str, ...]:
    if not raw:
        return DEFAULT_ASSISTANTS
    values = [chunk.strip().lower() for chunk in raw.split(",") if chunk.strip()]
    if not values or values == ["all"]:
        return DEFAULT_ASSISTANTS
    invalid = [name for name in values if name not in DEFAULT_ASSISTANTS]
    if invalid:
        valid = ", ".join(DEFAULT_ASSISTANTS)
        raise ValueError(f"Unknown assistant(s): {', '.join(invalid)}. Valid options: {valid}")
    return tuple(dict.fromkeys(values))


def prompt_for_assistants() -> tuple[str, ...]:
    options = ", ".join(DEFAULT_ASSISTANTS)
    prompt = (
        "Select assistants to install prompts for "
        f"(comma-separated, available: {options}, 'all' for every tool).\n"
        "Press Enter to install for all: "
    )
    try:
        response = input(prompt)
    except EOFError:
        response = ""
    response = response.strip()
    if not response:
        return DEFAULT_ASSISTANTS
    return parse_assistants(response)


def determine_assistants(raw: str | None) -> tuple[str, ...]:
    if raw is not None:
        return parse_assistants(raw)
    if sys.stdin is not None and sys.stdin.isatty():
        return prompt_for_assistants()
    return DEFAULT_ASSISTANTS


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="specline",
        description="SpecLine CLI (alias: palprompt) for managing specline/ workflows",
    )
    subparsers = parser.add_subparsers(dest="command")

    init_parser = subparsers.add_parser(
        "init", help="Initialise specline/ directory structure and prompt templates"
    )
    init_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing specline/ directory if present",
    )
    init_parser.add_argument(
        "--path",
        type=Path,
        default=Path.cwd(),
        help="Target project directory (default: current working directory)",
    )
    init_parser.add_argument(
        "--assistants",
        type=str,
        help=(
            "Comma-separated assistants to install prompts for "
            "(default: claude,cursor,github,specline,codex; use 'all' or leave empty for interactive prompt)."
        ),
    )
    init_parser.add_argument(
        "--update-root-agents",
        action="store_true",
        help="Overwrite the repository root AGENTS.md with a bootstrap that points to specline/AGENTS.md.",
    )

    update_parser = subparsers.add_parser(
        "update", help="Refresh prompt templates and sync assistant directories"
    )
    update_parser.add_argument(
        "--path",
        type=Path,
        default=Path.cwd(),
        help="Target project directory (default: current working directory)",
    )
    update_parser.add_argument(
        "--assistants",
        type=str,
        help="Comma-separated assistants to refresh (same options as init).",
    )
    return parser


def cmd_init(args: argparse.Namespace) -> int:
    try:
        assistants = determine_assistants(args.assistants)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    result: InitResult = init_palprompt_structure(root=args.path, force=args.force, assistants=assistants)

    if result.existing and not args.force:
        print(
            f"specline/ already exists at {result.root.resolve()}. "
            "Use --force to regenerate.",
            file=sys.stderr,
        )
        return 1

    print(
        f"SpecLine init complete at {result.root.resolve()} "
        f"(created: {', '.join(sorted(result.created)) or 'none'}, "
        f"migrated: {', '.join(sorted(result.migrated)) or 'none'})"
    )

    if args.update_root_agents:
        update_root_agents_file(args.path)

    return 0


def cmd_update(args: argparse.Namespace) -> int:
    try:
        assistants = determine_assistants(args.assistants)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    try:
        updated = refresh_prompts(root=args.path, assistants=assistants)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(
        f"SpecLine update complete at {(args.path / 'pal').resolve()} "
        f"(updated: {', '.join(sorted(updated)) or 'none'})"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "init":
        return cmd_init(args)
    if args.command == "update":
        return cmd_update(args)

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
