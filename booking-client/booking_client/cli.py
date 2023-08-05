from argparse import ArgumentParser
from typing import Callable, NoReturn

from booking_client.commands import (
    add_book_command,
    add_book_command_with_waiting_option,
    add_cancel_command,
    add_exit_command,
    add_finish_command,
    add_resource_commands,
    add_wait_command,
)


def interactive_cli_arg_parser():
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(required=True)

    add_book_command(subparsers)
    add_resource_commands(subparsers)
    add_cancel_command(subparsers)
    add_finish_command(subparsers)
    add_exit_command(subparsers)

    return parser


def main_arg_parser(interactive_cli_parser):
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(required=True)

    add_book_command_with_waiting_option(interactive_cli_parser, subparsers)
    add_resource_commands(subparsers)
    add_cancel_command(subparsers)
    add_wait_command(interactive_cli_parser, subparsers)
    add_finish_command(subparsers)

    return parser


def entrypoint():
    interactive_cli_parser = interactive_cli_arg_parser()
    main_parser = main_arg_parser(interactive_cli_parser)

    args = vars(main_parser.parse_args())
    subcommand: Callable[..., NoReturn] = args.pop("func")
    subcommand(**args)


# TODO: go into interactive mode when `book --wait` command is ran
# TODO: Use tkinter or similiar library to create notification windows when waiting
# booking to start or timed booking to finish
# TODO: When running book with --wait, prevent accidental SIGINT
# TODO: To receive notifications https://stackoverflow.com/a/51610341/12820664
# TODO: Argcomplete https://stackoverflow.com/a/15289025/12820664
