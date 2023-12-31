from __future__ import annotations

import asyncio
import sys
from argparse import ArgumentError
from asyncio import Task
from dataclasses import dataclass
from datetime import datetime
from signal import SIGINT
from time import time
from typing import TYPE_CHECKING, Callable, NoReturn

import aiohttp
import requests
from aioconsole import ainput, aprint  # type: ignore
from booking_common.models import (
    BookingRequest,
    BookingResponse,
    RequestedResource,
)
from requests.exceptions import HTTPError

if TYPE_CHECKING:
    from booking_client.custom_argparse import FixedArgumentParser


GREEN = "\033[92m"
RESET_COLOR = "\033[0m"


class CliExit(Exception):
    pass


@dataclass
class BookingSlot:
    start_time: datetime
    end_time: datetime


def book_with_wait(
    resource_type: str,
    resource_identifier: None | str,
    booking_time: BookingSlot,
    wait: bool,
    workflow_id: int,
    parser: FixedArgumentParser,
):
    if workflow_id:
        pass  # TODO

    body = BookingRequest(
        name="Some Client",
        start_time=booking_time.start_time,
        end_time=booking_time.end_time,
        resource=RequestedResource(
            identifier=resource_identifier, type=resource_type
        ),
    )

    try:
        response = requests.post(
            "http://localhost:8000/booking",
            data=body.model_dump_json(),
            timeout=0.1,
        )
    except ConnectionError:
        print("Could not connect to booking server", file=sys.stderr)
        sys.exit(1)

    try:
        response.raise_for_status()
    except HTTPError:
        print(response.json()["detail"], file=sys.stderr)
        sys.exit(1)

    booking = BookingResponse(**response.json())

    print(f"Booking id is {booking.info.id}")

    if wait:
        wait_booking_with_interactive_cli(parser, booking.info.id)


def book(
    resource_type: str, resource_identifier: None | str, workflow_id: int
):
    print(f"Booking resource {resource_type}")

    if workflow_id:
        pass  # TODO

    response = requests.post(
        "http://localhost:8000/booking",
        json={
            "name": "Some client",
            "resource": {
                "type": resource_type,
                "identifier": resource_identifier,
            },
        },
        timeout=0.1,
    )

    print(response.json())


def cancel_booking(booking_id: int):
    print(booking_id)


@dataclass
class InterruptInfo:
    timeout: float
    required_interrupts: int
    first_interrupt: float = 0
    interrupt_count: int = 0


def cancel_all(tasks: list[Task]):
    for task in tasks:
        if task != asyncio.current_task() and not task.done():
            task.cancel()


def ask_exit(tasks: list[Task], status: InterruptInfo):
    time_now = time()

    if time_now < status.first_interrupt + status.timeout:
        if status.interrupt_count + 1 == status.required_interrupts:
            print("")
            cancel_all(tasks)
            return
    else:
        status.interrupt_count = 0
        status.first_interrupt = time_now

    status.interrupt_count += 1

    print(
        "\n"
        "Are you sure you want to exit? Attempt"
        f" {status.interrupt_count}/{status.required_interrupts} within"
        f" {status.timeout} seconds"
    )
    print(f"{GREEN}> {RESET_COLOR}", end="", flush=True)


def wait_booking_with_interactive_cli(
    parser: FixedArgumentParser, booking_id: int
):
    async def wait_booking(tasks: list[Task], booking_id: int):
        url = f"ws://localhost:8000/booking/{booking_id}/wait"
        async with aiohttp.TCPConnector(limit=1) as connector:
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.ws_connect(url) as websocket:
                    message = await websocket.receive_json()
                    await aprint(f"\n{message}")
                    cancel_all(tasks)

    async def open_interactive_cli(tasks: list[Task]):
        while True:
            command: str = await ainput(f"{GREEN}> {RESET_COLOR}")
            try:
                args = vars(parser.parse_args(command.split()))
                subcommand: Callable[..., NoReturn] = args.pop("func")
                subcommand(**args)
            except CliExit:
                cancel_all(tasks)
                return
            except ArgumentError as error:
                await aprint(error.message)

    async def wait_and_open_cli() -> None:
        async with asyncio.TaskGroup() as group:
            tasks: list[Task] = []
            tasks.append(group.create_task(open_interactive_cli(tasks)))
            tasks.append(group.create_task(wait_booking(tasks, booking_id)))

            asyncio.get_running_loop().add_signal_handler(
                SIGINT, ask_exit, tasks, InterruptInfo(3, 3)
            )
        asyncio.get_running_loop().remove_signal_handler(SIGINT)

    asyncio.run(wait_and_open_cli())


def finish_booking(booking_id: int):
    print(booking_id)
