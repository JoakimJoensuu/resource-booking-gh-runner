from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, TypedDict

if TYPE_CHECKING:
    from booking_server.booking import Booking, BookingInfo


class RequestedResource(TypedDict):
    type: str
    identifier: None | str


class ResourceInfo(TypedDict):
    type: str
    identifier: str
    # TODO: Allow adding arbitrary commands to be ran when resource is reserved or freed


class Resource(TypedDict):
    info: ResourceInfo
    used_by: None | Booking


class DumpableResource(TypedDict):
    info: ResourceInfo
    used_by: BookingInfo | None


async def validate_resource(resource: Dict) -> Resource:
    # TODO: Proper error reporting mechanism
    # TODO: Generic TypedDict validation function
    return {
        "info": {
            "identifier": resource["identifier"],
            "type": resource["type"],
        },
        "used_by": None,
    }


async def dumpable_resource(resource: Resource) -> DumpableResource:
    return {
        "info": resource["info"],
        "used_by": (
            resource["used_by"]["info"] if resource["used_by"] else None
        ),
    }


async def dumpable_resources(
    resources: List[Resource],
) -> List[DumpableResource]:
    return [await dumpable_resource(resource) for resource in resources]
