import argparse
from functools import partial
from typing import cast

import uvloop
from booking_server.api import router
from booking_server.server import BookingApp, fire_and_forget, periodic_cleanup
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


app = BookingApp(
    github_token=github_token,
)
app.include_router(router)
app.router.on_startup.append(
    partial(
        fire_and_forget,
        app,
        periodic_cleanup(app.server_state, app.background_tasks),
    )
)

asgi_app = ASGIWrapper(cast(ASGIFramework, app))
config = Config()
config.accesslog = "-"
uvloop.run(worker_serve(asgi_app, config))
