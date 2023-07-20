# gh-runner-hw-booking


## Prerequisities

[GitHub CLI](https://cli.github.com/)
[pip >= v21.3](https://pip.pypa.io/en/stable/installation/)
[Python >= Python 3.8.10](https://www.python.org/downloads/)

## Python dev setup

**TODO: Use pinned git hash version in pyproject.toml for booking-common package**

**### TODO: Create dev_setup.sh script that creates venv, installs all packages as editable**

```console
python -m venv --clear .venv
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
