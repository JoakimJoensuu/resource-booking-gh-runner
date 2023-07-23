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

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
loop = asyncio.get_event_loop()

initial_server_state = ServerState(
    booking_id_counter=0, bookings=[], resources=[], ids_to_bookings={}
)
initial_background_tasks: alist[Task[Any]] = alist([])

loop.create_task(
    periodic_cleanup(initial_server_state, initial_background_tasks)
)

app = BookingApp(
    server_state=initial_server_state,
    background_tasks=initial_background_tasks,
)
app.include_router(router)

asgi_app = ASGIWrapper(cast(ASGIFramework, app))
config = Config()
config.accesslog = "-"


loop.run_until_complete(worker_serve(asgi_app, config))
