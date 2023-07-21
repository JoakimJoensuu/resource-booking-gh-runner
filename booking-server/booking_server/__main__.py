import asyncio

from aiohttp import web
from booking_server.api import routes
from booking_server.server import ServerData, periodic_cleanup

if __name__ == "__main__":
    initial_server_data: ServerData = {
        "booking_id_counter": 0,
        "bookings": [],
        "resources": [],
        "id_to_booking": {},
    }

    app = web.Application()
    app.add_routes(routes)
    app["server_data"] = initial_server_data

    loop = asyncio.get_event_loop()
    loop.create_task(periodic_cleanup(initial_server_data))

    web.run_app(app, loop=loop)
