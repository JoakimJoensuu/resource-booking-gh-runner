import asyncio
from argparse import ArgumentError
from asyncio import Task
from typing import Callable, NoReturn

import aiohttp
import requests
from aioconsole import ainput, aprint
from booking_client.custom_argparse import FixedArgumentParser


def book(
    resource_type: str, resource_identifier: None | str, workflow_id: int
):
    print(f"Booking resource {resource_type}")
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


def book_with_wait(
    resource_type: str,
    resource_identifier: None | str,
    wait: bool,
    workflow_id: int,
    parser: FixedArgumentParser,
):
    print(f"Booking resource {resource_type}")
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
    booking_id = response.json()["info"]["id"]

    if wait:
        wait_booking_with_interactive_cli(parser, booking_id)


def cancel_booking(booking_id: int):
    print(booking_id)


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
                    for task in tasks:
                        if task != asyncio.current_task() and not task.done():
                            task.cancel()

    async def open_interactive_cli(tasks: list[Task]):
        while True:
            command: str = await ainput("> ")
            try:
                args = vars(parser.parse_args(command.split()))
                subcommand: Callable[..., NoReturn] = args.pop("func")
                subcommand(**args)
            except SystemExit:
                for task in tasks:
                    if task != asyncio.current_task() and not task.done():
                        task.cancel()
                return
            except ArgumentError as error:
                await aprint(error.message)

    async def wait_and_open_cli():
        async with asyncio.TaskGroup() as group:
            tasks: list[Task] = []
            tasks.append(group.create_task(open_interactive_cli(tasks)))
            tasks.append(group.create_task(wait_booking(tasks, booking_id)))

    asyncio.run(wait_and_open_cli())


def finish_booking(booking_id: int):
    print(booking_id)
