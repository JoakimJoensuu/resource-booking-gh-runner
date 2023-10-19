from __future__ import annotations

import asyncio
import json
from asyncio import Task
from typing import Any, Coroutine

from aioconsole import aprint  # type: ignore
from booking_server.booking import (
    Booking,
    BookingResponse,
    dumpable_bookings,
    dumpable_ids_to_bookings,
)
from booking_server.custom_asyncio import alist
from booking_server.resource import (
    DumpableResource,
    Resource,
    dumpable_ids_to_resources,
    dumpable_resources,
)
from fastapi import FastAPI, WebSocket
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, ConfigDict
from starlette.requests import Request


class ServerState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    booking_id_counter: int = 0
    bookings: list[Booking] = []
    resources: list[Resource] = []
    ids_to_bookings: dict[int, Booking] = {}
    ids_to_resources: dict[str, Resource] = {}


class DumpableServerState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    booking_id_counter: int
    bookings: list[BookingResponse]
    resources: list[DumpableResource]
    ids_to_bookings: dict[int, BookingResponse]
    ids_to_resources: dict[str, DumpableResource]


DumpableServerState.model_rebuild()
ServerState.model_rebuild()


def fire_and_forget(
    app: BookingApp, background_routine: Coroutine[Any, Any, None]
):
    background_task = asyncio.create_task(background_routine)
    app.background_tasks.append(background_task)


async def dumpable_server_state(server_state: ServerState):
    return DumpableServerState(
        bookings=await dumpable_bookings(server_state.bookings),
        resources=await dumpable_resources(server_state.resources),
        booking_id_counter=server_state.booking_id_counter,
        ids_to_bookings=await dumpable_ids_to_bookings(
            server_state.ids_to_bookings
        ),
        ids_to_resources=await dumpable_ids_to_resources(
            server_state.ids_to_resources
        ),
    )


async def periodic_cleanup(
    server_state: ServerState, background_tasks: alist[Task[Any]]
):
    # TODO: Implement
    # TODO: Could be also ran from endpoint handlers when lists get too big
    while True:
        await aprint(
            "===============================CLEANUP=============================="
        )
        await aprint(
            "I could clean something, but here is current server data:"
        )
        server_state_snapshot = await dumpable_server_state(server_state)
        await aprint(
            json.dumps(jsonable_encoder(server_state_snapshot), indent=2)
        )
        await aprint(f"Background tasks running {len(background_tasks)}.")
        background_tasks[:] = [
            task async for task in background_tasks if not task.done()
        ]
        await aprint(f"Background tasks left {len(background_tasks)}.")
        await asyncio.sleep(10)


class BookingApp(FastAPI):
    server_state: ServerState
    background_tasks: alist[Task[Any]]
    github_token: str

    def __init__(
        self,
        *,
        github_token: str,
        server_state: ServerState = ServerState(),
        background_tasks: alist[Task] = alist([]),
        **fast_api_kwargs: Any,
    ) -> None:
        super().__init__(
            **fast_api_kwargs,
        )
        self.server_state = server_state
        self.background_tasks = background_tasks
        self.github_token = github_token


class AppRequest(Request):
    app: BookingApp


class AppWebSocket(WebSocket):
    app: BookingApp
