# resource-booking

Hobby project to get familiar with Python asyncio.

Targeted key features:
- CLI tool to book, add and remove resources from/to the booking system
- pop-up notifications for starting or ending booking when CLI is in interactive mode
- stop GitHub Actions workflow and continue when requested resource becomes free

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
