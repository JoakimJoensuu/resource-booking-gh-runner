from argparse import ArgumentParser, _SubParsersAction

from booking_client.booking import (
    book,
    book_with_wait,
    cancel_booking,
    finish_booking,
    wait_booking,
)
from booking_client.resource import resource_add, resource_delete


def add_book_command(main_subparsers: _SubParsersAction):
    book_parser: ArgumentParser = main_subparsers.add_parser("book")
    book_parser.set_defaults(func=book)
    book_parser.add_argument("resource_type")
    book_parser.add_argument("resource_identifier", nargs="?")
    book_parser.add_argument("--workflow_id", type=int)


def add_book_command_with_waiting_option(
    interactive_parser: ArgumentParser, main_subparsers: _SubParsersAction
):
    book_parser: ArgumentParser = main_subparsers.add_parser("book")
    book_parser.set_defaults(func=book_with_wait)
    book_parser.set_defaults(main_parser=interactive_parser)
    book_parser.add_argument("resource_type")
    book_parser.add_argument("resource_identifier", nargs="?")
    book_parser.add_argument("--wait", "-w", action="store_true")
    book_parser.add_argument("--workflow_id", type=int)


def add_resource_add_command(resource_subparsers: _SubParsersAction):
    add_parser: ArgumentParser = resource_subparsers.add_parser("add")
    add_parser.set_defaults(func=resource_add)
    add_parser.add_argument("resource_type")
    add_parser.add_argument("resource_identifier")


def add_resource_delete_command(resource_subparsers: _SubParsersAction):
    delete_parser: ArgumentParser = resource_subparsers.add_parser("delete")
    delete_parser.set_defaults(func=resource_delete)
    delete_parser.add_argument("resource_identifier")


def add_resource_commands(main_subparsers: _SubParsersAction):
    resource_parser: ArgumentParser = main_subparsers.add_parser("resource")
    resource_subparsers = resource_parser.add_subparsers(required=True)
    add_resource_add_command(resource_subparsers)
    add_resource_delete_command(resource_subparsers)


def add_cancel_command(main_subparsers: _SubParsersAction):
    cancel_parser: ArgumentParser = main_subparsers.add_parser("cancel")
    cancel_parser.set_defaults(func=cancel_booking)
    cancel_parser.add_argument("booking_id", type=int)


def add_wait_command(
    interactive_parser: ArgumentParser, main_subparsers: _SubParsersAction
):
    wait_parser: ArgumentParser = main_subparsers.add_parser("wait")
    wait_parser.set_defaults(func=wait_booking)
    wait_parser.set_defaults(main_parser=interactive_parser)
    wait_parser.add_argument("booking_id", type=int)


def add_finish_command(main_subparsers: _SubParsersAction):
    wait_parser: ArgumentParser = main_subparsers.add_parser("finish")
    wait_parser.set_defaults(func=finish_booking)
    wait_parser.add_argument("booking_id", type=int)
