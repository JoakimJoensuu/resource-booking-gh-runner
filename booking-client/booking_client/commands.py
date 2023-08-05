from argparse import ArgumentParser, _SubParsersAction

from booking_client.booking import (
    book,
    book_with_wait,
    cancel_booking,
    finish_booking,
    wait_booking_with_interactive_cli,
)
from booking_client.resource import resource_add, resource_delete


def add_book_command(subparsers: _SubParsersAction):
    def callback_function(
        resource_type: str, resource_identifier: None | str, workflow_id: int
    ):
        book(resource_type, resource_identifier, workflow_id)

    subcommand: ArgumentParser = subparsers.add_parser("book")
    subcommand.set_defaults(func=callback_function)
    subcommand.add_argument("resource_type")
    subcommand.add_argument("resource_identifier", nargs="?")
    subcommand.add_argument("--workflow_id", type=int)


def add_book_command_with_waiting_option(
    interactive_cli_parser: ArgumentParser, subparsers: _SubParsersAction
):
    def callback_function(
        resource_type: str,
        resource_identifier: None | str,
        wait: bool,
        workflow_id: int,
        interactive_cli_parser: ArgumentParser,
    ):
        book_with_wait(
            resource_type,
            resource_identifier,
            wait,
            workflow_id,
            interactive_cli_parser,
        )

    subcommand: ArgumentParser = subparsers.add_parser("book")
    subcommand.set_defaults(func=callback_function)
    subcommand.set_defaults(interactive_cli_parser=interactive_cli_parser)
    subcommand.add_argument("resource_type")
    subcommand.add_argument("resource_identifier", nargs="?")
    subcommand.add_argument("--wait", "-w", action="store_true")
    subcommand.add_argument("--workflow_id", type=int)


def add_resource_add_command(resource_subparsers: _SubParsersAction):
    def callback_function(resource_type: str, resource_identifier: str):
        resource_add(resource_type, resource_identifier)

    subcommand: ArgumentParser = resource_subparsers.add_parser("add")
    subcommand.set_defaults(func=callback_function)
    subcommand.add_argument("resource_type")
    subcommand.add_argument("resource_identifier")


def add_resource_delete_command(resource_subparsers: _SubParsersAction):
    def callback_function(resource_identifier: str):
        resource_delete(resource_identifier)

    subcommand: ArgumentParser = resource_subparsers.add_parser("delete")
    subcommand.set_defaults(func=callback_function)
    subcommand.add_argument("resource_identifier")


def add_resource_commands(subparsers: _SubParsersAction):
    subcommand: ArgumentParser = subparsers.add_parser("resource")
    subsubcommand = subcommand.add_subparsers(required=True)
    add_resource_add_command(subsubcommand)
    add_resource_delete_command(subsubcommand)


def add_cancel_command(subparsers: _SubParsersAction):
    def callback_function(booking_id: int):
        cancel_booking(booking_id)

    subcommand: ArgumentParser = subparsers.add_parser("cancel")
    subcommand.set_defaults(func=callback_function)
    subcommand.add_argument("booking_id", type=int)


def add_wait_command(
    interactive_cli_parser: ArgumentParser, subparsers: _SubParsersAction
):
    def callback_function(
        interactive_cli_parser: ArgumentParser, booking_id: int
    ):
        wait_booking_with_interactive_cli(interactive_cli_parser, booking_id)

    subcommand: ArgumentParser = subparsers.add_parser("wait")
    subcommand.set_defaults(func=callback_function)
    subcommand.set_defaults(interactive_cli_parser=interactive_cli_parser)
    subcommand.add_argument("booking_id", type=int)


def add_finish_command(subparsers: _SubParsersAction):
    subcommand: ArgumentParser = subparsers.add_parser("finish")

    def callback_function(booking_id: int):
        finish_booking(booking_id)

    subcommand.set_defaults(func=callback_function)
    subcommand.add_argument("booking_id", type=int)


def add_exit_command(subparsers: _SubParsersAction):
    subcommand: ArgumentParser = subparsers.add_parser("exit")
    subcommand.set_defaults(func=exit)
