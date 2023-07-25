import asyncio
from asyncio import Task

import aiohttp
import requests
from aioconsole import ainput, aprint


def book(
    resource_type: str,
    resource_identifier: None | str,
    wait: bool,
    workflow_id: int,
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


def wait_booking(booking_id):
    async def notifyer(tasks: list[Task]):
        url = f"ws://localhost:8000/booking/{booking_id}/wait"
        async with aiohttp.TCPConnector(limit=1) as connector:
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.ws_connect(url) as websocket:
                    message = await websocket.receive_json()
                    print(message)
                    for task in tasks:
                        if task != asyncio.current_task() and not task.done():
                            task.cancel()

    async def interactive_cli(tasks: list[Task]):
        while True:
            command = await ainput("> ")
            # TODO: Parse command and act based on it
            if command == "exit":
                for task in tasks:
                    if task != asyncio.current_task() and not task.done():
                        task.cancel()
                return
            await aprint(
                f"Unimplemented command in interactive mode ({command})"
            )

    async def main():
        async with asyncio.TaskGroup() as group:
            tasks: list[Task] = []
            for coro in (interactive_cli(tasks), notifyer(tasks)):
                tasks.append(group.create_task(coro))

    asyncio.run(main())


def finish_booking(**kwargs):
    print(kwargs)
