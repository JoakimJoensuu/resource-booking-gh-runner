from aiohttp import web
from aiohttp.web_request import Request
from typing import TypedDict, Dict, List


class Resource(TypedDict):
    type: str
    identifier: str


resources: List[Resource] = []


async def validate_resource(resource) -> Resource:
    # TODO: Proper error reporting mechanism
    return {"identifier": resource["identifier"], "type": resource["type"]}


number_counter = 0


class Reservation(TypedDict):
    id: str


reservations: List[Reservation] = []


async def handle(request):
    global number_counter
    reservation_id = number_counter
    number_counter += 1
    return web.Response(text=str(reservation_id))


async def new_resource(request: Request):
    json_body: Dict = await request.json()

    resource = await validate_resource(json_body)

    # TODO: Check for existing resources with same identifier
    resources.append(resource)

    return web.Response(text="TODO")


async def get_resources(_: Request):
    return web.json_response(resources)


app = web.Application()
app.add_routes(
    [
        web.get("/all", handle),
        web.post("/book", handle),
        web.delete("/{reservation_id}", handle),
        web.get("/reservations/before/{reservation_id}", handle),
        web.get("/reservation/{reservation_id}", handle),
        web.post("/resource", new_resource),
        web.get("/resource/all", get_resources),
    ]
)


def main():
    web.run_app(app)


if __name__ == "__main__":
    main()
