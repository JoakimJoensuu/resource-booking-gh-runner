import asyncio

from booking_server.api import routes
from booking_server.server import (
    ServerData,
    periodic_cleanup,
    start_cleaner,
    start_server,
)

loop = asyncio.get_event_loop()

initial_server_data: ServerData = {
    "booking_id_counter": 0,
    "bookings": [],
    "resources": [],
    "id_to_booking": {},
}

start_cleaner(loop, periodic_cleanup(initial_server_data))

start_server(routes, initial_server_data, loop)
