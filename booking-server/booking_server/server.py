import asyncio
import json

from aiohttp.web import Application
from booking_server.types import ServerData, dumpable_server_data


async def get_server_data(application: Application):
    server_data: ServerData = application["server_data"]
    return server_data


async def periodic_cleanup(server_data: ServerData):
    # TODO: Implement
    # TODO: Could be also ran from endpoint handlers when lists get too big
    while True:
        print("I could clean something, but here is current server data")

        dumpable = dumpable_server_data(server_data)
        print(json.dumps(dumpable, indent=2))

        await asyncio.sleep(5)
