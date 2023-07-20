import asyncio

from aiohttp import web
from booking_server.api import (
    booking_update,
    get_booking,
    get_bookings,
    get_resources,
    new_booking,
    new_resource,
    unimplemented,
)
from booking_server.server import periodic_cleanup
from booking_server.types import ServerData

if __name__ == "__main__":
    app = web.Application()
    app.add_routes(
        [
            web.get("/booking/all", get_bookings),
            web.get("/bookings", get_bookings),
            web.post("/booking", new_booking),
            web.post("/booking/{booking_id}/{action}", booking_update),
            web.get("/booking/before/{booking_id}", unimplemented),
            web.get("/booking/{booking_id}", get_booking),
            web.post("/resource", new_resource),
            web.delete("/resource", unimplemented),
            web.get("/resource/all", get_resources),
            web.get("/resources", get_resources),
        ]
    )

    initial_server_data: ServerData = {
        "booking_id_counter": 0,
        "bookings": [],
        "resources": [],
        "id_to_booking": {},
    }
    app["server_data"] = initial_server_data

    loop = asyncio.get_event_loop()
    loop.create_task(periodic_cleanup(initial_server_data))

    web.run_app(app, loop=loop)
