import argparse
import asyncio
from asyncio import Task
from typing import Any, cast

import uvloop
from booking_server.api import router
from booking_server.custom_asyncio import alist
from booking_server.server import BookingApp, ServerState, periodic_cleanup
from hypercorn import Config
from hypercorn.app_wrappers import ASGIWrapper
from hypercorn.asyncio.run import worker_serve
from hypercorn.typing import ASGIFramework

parser = argparse.ArgumentParser()
parser.add_argument(
    "github_token",
    type=str,
    help=(
        "GitHub token for re-running jobs. Must have R/W permissions for"
        ' "Actions" in your repository.'
    ),
)
github_token: str = parser.parse_args().github_token

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
loop = asyncio.get_event_loop()

initial_server_state = ServerState(
    booking_id_counter=0,
    bookings=[],
    resources=[],
    ids_to_bookings={},
    ids_to_resources={},
)
initial_background_tasks: alist[Task[Any]] = alist([])

loop.create_task(
    periodic_cleanup(initial_server_state, initial_background_tasks)
)

app = BookingApp(
    server_state=initial_server_state,
    background_tasks=initial_background_tasks,
    github_token=github_token,
)
app.include_router(router)

asgi_app = ASGIWrapper(cast(ASGIFramework, app))
config = Config()
config.accesslog = "-"

loop.run_until_complete(worker_serve(asgi_app, config))
