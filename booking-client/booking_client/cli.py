from argparse import _SubParsersAction

from booking_client.booking import (
    book_with_wait,
    cancel_booking,
    finish_booking,
    wait_booking_with_interactive_cli,
)
from booking_client.custom_argparse import FixedArgumentParser
from booking_client.resource import resource_add, resource_delete


def add_book_command_with_waiting_option(
    interactive_cli_parser: FixedArgumentParser, subparsers: _SubParsersAction
):
    def callback_function(
        resource_type: str,
        resource_identifier: None | str,
        wait: bool,
        workflow_id: int,
        interactive_cli_parser: FixedArgumentParser,
    ):
        book_with_wait(
            resource_type,
            resource_identifier,
            wait,
            workflow_id,
            interactive_cli_parser,
        )

    subcommand: FixedArgumentParser = subparsers.add_parser("book")
    subcommand.set_defaults(func=callback_function)
    subcommand.set_defaults(interactive_cli_parser=interactive_cli_parser)
    subcommand.add_argument("resource_type")
    subcommand.add_argument("resource_identifier", nargs="?")
    subcommand.add_argument("--wait", "-w", action="store_true")
    subcommand.add_argument("--workflow_id", type=int)


def add_resource_add_command(resource_subparsers: _SubParsersAction):
    def callback_function(resource_type: str, resource_identifier: str):
        resource_add(resource_type, resource_identifier)

    subcommand: FixedArgumentParser = resource_subparsers.add_parser("add")
    subcommand.set_defaults(func=callback_function)
    subcommand.add_argument("resource_type")
    subcommand.add_argument("resource_identifier")


def add_resource_delete_command(resource_subparsers: _SubParsersAction):
    def callback_function(resource_identifier: str):
        resource_delete(resource_identifier)

    subcommand: FixedArgumentParser = resource_subparsers.add_parser("delete")
    subcommand.set_defaults(func=callback_function)
    subcommand.add_argument("resource_identifier")


def add_resource_commands(subparsers: _SubParsersAction):
    subcommand: FixedArgumentParser = subparsers.add_parser("resource")
    subsubcommand = subcommand.add_subparsers(required=True)
    add_resource_add_command(subsubcommand)
    add_resource_delete_command(subsubcommand)


def add_cancel_command(subparsers: _SubParsersAction):
    def callback_function(booking_id: int):
        cancel_booking(booking_id)

    subcommand: FixedArgumentParser = subparsers.add_parser("cancel")
    subcommand.set_defaults(func=callback_function)
    subcommand.add_argument("booking_id", type=int)


def add_wait_command(
    interactive_cli_parser: FixedArgumentParser, subparsers: _SubParsersAction
):
    def callback_function(
        interactive_cli_parser: FixedArgumentParser, booking_id: int
    ):
        wait_booking_with_interactive_cli(interactive_cli_parser, booking_id)

    subcommand: FixedArgumentParser = subparsers.add_parser("wait")
    subcommand.set_defaults(func=callback_function)
    subcommand.set_defaults(interactive_cli_parser=interactive_cli_parser)
    subcommand.add_argument("booking_id", type=int)


def add_finish_command(subparsers: _SubParsersAction):
    subcommand: FixedArgumentParser = subparsers.add_parser("finish")

    def callback_function(booking_id: int):
        finish_booking(booking_id)

    subcommand.set_defaults(func=callback_function)
    subcommand.add_argument("booking_id", type=int)


def main_arg_parser(interactive_cli_parser):
    parser = FixedArgumentParser()
    subparsers = parser.add_subparsers(required=True)

    add_book_command_with_waiting_option(interactive_cli_parser, subparsers)
    add_resource_commands(subparsers)
    add_cancel_command(subparsers)
    add_wait_command(interactive_cli_parser, subparsers)
    add_finish_command(subparsers)

    return parser


# TODO: go into interactive mode when `book --wait` command is ran
# TODO: Use tkinter or similiar library to create notification windows when waiting
# booking to start or timed booking to finish
# TODO: When running book with --wait, prevent accidental SIGINT
# TODO: To receive notifications https://stackoverflow.com/a/51610341/12820664
# TODO: Argcomplete https://stackoverflow.com/a/15289025/12820664
