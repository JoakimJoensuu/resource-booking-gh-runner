import sys
from argparse import _SubParsersAction

from booking_client.booking import (
    GREEN,
    RESET_COLOR,
    book,
    cancel_booking,
    finish_booking,
)
from booking_client.custom_argparse import FixedArgumentParser
from booking_client.resource import resource_add, resource_delete


def add_resource_add_command(subparsers: _SubParsersAction):
    def callback_function(resource_type: str, resource_identifier: str):
        resource_add(resource_type, resource_identifier)

    subcommand: FixedArgumentParser = subparsers.add_parser(
        "add", exit_on_error=False
    )
    subcommand.set_defaults(func=callback_function)
    subcommand.add_argument("resource_type")
    subcommand.add_argument("resource_identifier")


def add_resource_delete_command(subparsers: _SubParsersAction):
    def callback_function(resource_identifier: str):
        resource_delete(resource_identifier)

    subcommand: FixedArgumentParser = subparsers.add_parser(
        "delete", exit_on_error=False
    )
    subcommand.set_defaults(func=callback_function)
    subcommand.add_argument("resource_identifier")


def add_resource_commands(subparsers: _SubParsersAction):
    subcommand: FixedArgumentParser = subparsers.add_parser(
        "resource", exit_on_error=False
    )
    subsubparsers = subcommand.add_subparsers(required=True)
    add_resource_add_command(subsubparsers)
    add_resource_delete_command(subsubparsers)


def add_help_command(
    parser: FixedArgumentParser, subparsers: _SubParsersAction
):
    subcommand: FixedArgumentParser = subparsers.add_parser(
        "help", exit_on_error=False
    )
    subcommand.set_defaults(func=parser.print_help)


def add_finish_command(subparsers: _SubParsersAction):
    subcommand: FixedArgumentParser = subparsers.add_parser(
        "finish", exit_on_error=False
    )

    def callback_function(booking_id: int):
        finish_booking(booking_id)

    subcommand.set_defaults(func=callback_function)
    subcommand.add_argument("booking_id", type=int)


def add_exit_command(subparsers: _SubParsersAction):
    def callback_function(code: int):
        sys.exit(code)

    subcommand: FixedArgumentParser = subparsers.add_parser(
        "exit", exit_on_error=False
    )
    subcommand.set_defaults(func=callback_function)
    subcommand.set_defaults(code=0)


def add_cancel_command(subparsers: _SubParsersAction):
    def callback_function(booking_id: int):
        cancel_booking(booking_id)

    subcommand: FixedArgumentParser = subparsers.add_parser(
        "cancel", exit_on_error=False
    )
    subcommand.set_defaults(func=callback_function)
    subcommand.add_argument("booking_id", type=int)


def add_book_command(subparsers: _SubParsersAction):
    def callback_function(
        resource_type: str, resource_identifier: None | str, workflow_id: int
    ):
        book(resource_type, resource_identifier, workflow_id)

    subcommand: FixedArgumentParser = subparsers.add_parser(
        "book", exit_on_error=False
    )
    subcommand.set_defaults(func=callback_function)
    subcommand.add_argument("resource_type")
    subcommand.add_argument("resource_identifier", nargs="?")
    subcommand.add_argument("--workflow_id", type=int)


def interactive_cli_arg_parser():
    parser = FixedArgumentParser(
        exit_on_error=False, prog=f"{GREEN}>{RESET_COLOR}"
    )
    subparsers = parser.add_subparsers(required=True)

    add_book_command(subparsers)
    add_resource_commands(subparsers)
    add_cancel_command(subparsers)
    add_finish_command(subparsers)
    add_exit_command(subparsers)
    add_help_command(parser, subparsers)

    return parser
