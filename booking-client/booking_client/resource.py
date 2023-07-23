import requests


def resource_add(resource_type: str, resource_identifier: str):
    requests.post(
        "http://localhost:8000/resource",
        json={"type": resource_type, "identifier": resource_identifier},
        timeout=0.1,
    )


def resource_delete(resource_identifier: str):
    print(resource_identifier)
