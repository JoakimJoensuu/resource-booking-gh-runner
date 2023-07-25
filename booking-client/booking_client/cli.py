from argparse import ArgumentParser
from typing import Callable, NoReturn

from booking_client.commands import (
    add_book_command,
    add_cancel_command,
    add_finish_command,
    add_resource_commands,
    add_wait_command,
)


def handle_command():
    main_parser = ArgumentParser(prog="booking")
    main_subparsers = main_parser.add_subparsers(required=True)

    add_book_command(main_subparsers)

    add_resource_commands(main_subparsers)

    add_cancel_command(main_subparsers)

    add_wait_command(main_subparsers)

    add_finish_command(main_subparsers)

    args = vars(main_parser.parse_args())
    subcommand: Callable[..., NoReturn] = args.pop("func")
    subcommand(**args)


# TODO: go into interactive mode when `book --wait` or `wait` command is ran
# TODO: Use tkinter or similiar library to create notification windows when waiting
# booking to start or timed booking to finish
# TODO: When running book with --wait, prevent accidental SIGINT
# TODO: To receive notifications https://stackoverflow.com/a/51610341/12820664
# TODO: Argcomplete https://stackoverflow.com/a/15289025/12820664
