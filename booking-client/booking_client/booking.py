import requests


def book(
    resource_type: str,
    resource_identifier: None | str,
    wait: bool,
    workflow_id: int,
):
    print(f"Booking resource {resource_type}")
    response = requests.post(
        "http://localhost:8000/booking",
        json={
            "name": "Some client",
            "resource": {
                "type": resource_type,
                "identifier": resource_identifier,
            },
        },
        timeout=0.1,
    )

    print(response.json())


def cancel_booking(**kwargs):
    print(kwargs)


def wait_booking(**kwargs):
    print(kwargs)


def finish_booking(**kwargs):
    print(kwargs)
