# -*- coding: utf-8 -*-
import os
import argparse


def __run_shell(_) -> None:
    try:
        from eastwind.core.shell import run_shell
        run_shell()
    except KeyboardInterrupt:
        return


def __run_background(_) -> None:
    # Config the environment first.
    from eastwind.lib.path import DIR_ROOT, DIR_EASTWIND
    import sys
    def __insert_path(target_path: str) -> None:
        if target_path not in sys.path:
            sys.path.insert(0, target_path)
    __insert_path(DIR_EASTWIND)
    __insert_path(DIR_ROOT)
    # Launch the background main.
    from eastwind.core.background import main
    main()


COMMANDS = {
    "shell": {
        "func": __run_shell,
        "description": "Launch backend manage shell",
    },
    "background": {
        "func": __run_background,
        "description": "Launch background task executor"
    },
}


def main() -> None:
    # Run the command line interface main.
    parser = argparse.ArgumentParser(
        prog="eastwind",
        description="Eastwind - a general-purpose rapid development framework for automated research data processing platform"
    )
    subparsers = parser.add_subparsers(
        dest="command",
        help="Available commands"
    )
    for cmd_name, cmd_info in COMMANDS.items():
        cmd_parser = subparsers.add_parser(cmd_name, help=cmd_info["description"])
        cmd_parser.set_defaults(func=cmd_info["func"])

    args = parser.parse_args()
    # Run the function we expected.
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
