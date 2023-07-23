# resource-booking

Hobby project to get familiar with Python asyncio.

Targeted key features:
 - server to keep track of resources and reservations and automatically allocate free resources
 - CLI tool for booking, adding and removing resources from the reservation system
 - popup notifications for starting and soon-to-end bookings when the CLI is in interactive mode
 - stop GitHub Actions workflow and resume when the requested resource becomes available
## Development prerequisities

 - [GitHub CLI](https://cli.github.com/)
 - [pip >= v21.3](https://pip.pypa.io/en/stable/installation/)
 - [Python >= 3.8](https://www.python.org/downloads/)

## Python dev setup

```console
python3.11 -m venv --clear .venv
. .venv/bin/activate
pip install --upgrade "pip>=21.3"
pip install --editable booking-server[dev] --editable booking-client[dev]
pip install --editable booking-common[dev]
./server_reload.sh
```

```console
. .venv/bin/activate
booking
```
