import re
from argparse import (
    Action,
    ArgumentError,
    ArgumentParser,
    Namespace,
    _SubParsersAction,
)
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Sequence

from booking_client.booking import (
    BookingSlot,
    book_with_wait,
    cancel_booking,
    finish_booking,
    wait_booking_with_interactive_cli,
)
from booking_client.custom_argparse import FixedArgumentParser
from booking_client.resource import resource_add, resource_delete


class ValidateTime(Action):
    def __call__(
        self,
        parser: ArgumentParser,
        namespace: Namespace,
        values: Sequence[str],
        option_string: str | None = None,
    ) -> None:
        del option_string

        minutes: int = 0
        hours: int = 0
        date: str | None = None
        time: str | None = None
        invalid_arguments: list[str] = []
        for value in values:
            if match := re.search(r"^(?P<minutes>\d+)m$", value):
                if minutes:
                    raise ArgumentError(
                        self,
                        (
                            f"too many minute values ({minutes} and"
                            f" {match.group('minutes')})"
                        ),
                    )
                minutes = int(match.group("minutes"))
                if not 0 <= minutes <= 60:
                    raise ArgumentError(
                        self, f"minutes must be >= 0 and <= 60 got {value}"
                    )
            elif match := re.search(r"^(?P<hours>\d+)h$", value):
                if hours:
                    raise ArgumentError(
                        self,
                        (
                            f"too many hour values ({hours} and"
                            f" {match.group('hours')})"
                        ),
                    )
                hours = int(match.group("hours"))
                if not 0 <= hours <= 23:
                    raise ArgumentError(
                        self, f"hours must be >= 0 and <= 23, got {value}"
                    )
            elif match := re.search(r"^(?P<date>\d{4}-\d{2}-\d{2})$", value):
                if date:
                    raise ArgumentError(
                        self,
                        (
                            f"too many date values ({date} and"
                            f" {match.group('date')})"
                        ),
                    )
                date = match.group("date")
            elif match := re.search(r"^(?P<time>\d{1,2}:\d{2})$", value):
                if time:
                    raise ArgumentError(
                        self,
                        (
                            f"too many time values ({time} and"
                            f" {match.group('time')})"
                        ),
                    )
                time = match.group("time")
            else:
                invalid_arguments.append(value)
                break

        if invalid_arguments:
            raise ArgumentError(
                self,
                f"invalid values: {', '.join(invalid_arguments)}",
            )

        if hours or minutes:
            duration = timedelta(
                hours=hours,
                minutes=minutes,
            )
        else:
            duration = timedelta(minutes=30)

        try:
            if date and time:
                start_time = datetime.strptime(
                    f"{date} {time}", "%Y-%m-%d %H:%M"
                )
            elif date:
                start_time = datetime.strptime(f"{date}", "%Y-%m-%d")
            elif time:
                current = datetime.now()
                desired_time = datetime.strptime(f"{time}", "%H:%M")
                start_time = current.replace(
                    hour=desired_time.hour, minute=desired_time.minute
                )
                while start_time < current:
                    start_time += timedelta(days=1)
            else:
                start_time = datetime.now()
        except ValueError as e:
            raise ArgumentError(self, ", ".join(e.args))

        setattr(
            namespace,
            self.dest,
            BookingSlot(start_time, start_time + duration),
        )


def add_book_command_with_waiting_option(
    interactive_cli_parser: FixedArgumentParser, subparsers: _SubParsersAction
):
    def callback_function(
        resource_type: str,
        resource_identifier: None | str,
        booking_time: BookingSlot,
        wait: bool,
        workflow_id: int,
        interactive_cli_parser: FixedArgumentParser,
    ):
        book_with_wait(
            resource_type,
            resource_identifier,
            booking_time,
            wait,
            workflow_id,
            interactive_cli_parser,
        )

    subcommand: FixedArgumentParser = subparsers.add_parser("book")
    subcommand.set_defaults(func=callback_function)
    subcommand.set_defaults(interactive_cli_parser=interactive_cli_parser)
    subcommand.add_argument("resource_type")
    subcommand.add_argument(
        "booking_time",
        nargs="+",
        action=ValidateTime,
        help=(
            "desired starting date (YYYY-MM-DD) time (hh:mm) and/or duration"
            " in hours (99h) and/or minutes (99m) - date and time in local"
            " timezone"
        ),
    )
    subcommand.add_argument("--resource_identifier")
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


# TODO: When running book with --wait, prevent accidental SIGINT
# https://stackoverflow.com/a/68732870/12820664
# TODO: To create notification to user when waiting booking to start or timed booking to finish
# https://pypi.org/project/notify2/
# TODO: Argument completion https://stackoverflow.com/a/15289025/12820664
# TODO: Enable user to give booking start time and length see NaiveDatetime
# https://docs.pydantic.dev/latest/usage/types/datetime/
# https://github.com/pydantic/pydantic/pull/4812/files
