import asyncio
from argparse import ArgumentParser
from asyncio import Task
from typing import Callable, NoReturn

import aiohttp
import requests
from aioconsole import ainput, aprint


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
    main_parser: ArgumentParser,
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


def cancel_booking(**kwargs):
    print(kwargs)


def wait_booking(main_parser: ArgumentParser, booking_id: int):
    async def notifyer(tasks: list[Task]):
        url = f"ws://localhost:8000/booking/{booking_id}/wait"
        async with aiohttp.TCPConnector(limit=1) as connector:
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.ws_connect(url) as websocket:
                    message = await websocket.receive_json()
                    await aprint(f"\n{message}")
                    for task in tasks:
                        if task != asyncio.current_task() and not task.done():
                            task.cancel()

    async def interactive_cli(tasks: list[Task]):
        while True:
            command: str = await ainput("> ")
            if command == "exit":
                for task in tasks:
                    if task != asyncio.current_task() and not task.done():
                        task.cancel()
                return
            try:
                args = vars(main_parser.parse_args(command.split(" ")))
                subcommand: Callable[..., NoReturn] = args.pop("func")
                subcommand(**args)
            except SystemExit:
                pass

    async def wait_and_open_cli():
        async with asyncio.TaskGroup() as group:
            tasks: list[Task] = []
            tasks.append(group.create_task(interactive_cli(tasks)))
            tasks.append(group.create_task(notifyer(tasks)))

    asyncio.run(wait_and_open_cli())


def finish_booking(**kwargs):
    print(kwargs)
