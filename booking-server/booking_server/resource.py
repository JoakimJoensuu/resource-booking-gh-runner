from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from booking_server.booking import Booking, BookingInfo
    from booking_server.server import ServerState


class ResourceInfo(BaseModel):
    type: str
    identifier: str
    # TODO: Allow adding arbitrary commands to be ran when resource is reserved or freed


class Resource(BaseModel):
    info: ResourceInfo
    used_by: None | Booking = None


class NewResource(BaseModel):
    type: str = Field(examples=["big_machine"])
    identifier: str = Field(examples=["floor_3"])


class DumpableResource(BaseModel):
    info: ResourceInfo
    used_by: BookingInfo | None


async def dumpable_resource(resource: Resource):
    used_by = resource.used_by.info if resource.used_by else None
    return DumpableResource(info=resource.info, used_by=used_by)


async def dumpable_resources(
    resources: list[Resource],
):
    return [await dumpable_resource(resource) for resource in resources]


async def add_new_resource(
    new_resource: NewResource,
    server_state: ServerState,
):
    # TODO: Check for existing resources with same identifier use HTTP 409 Conflict
    # even when they have different types
    resource = Resource(info=ResourceInfo(**new_resource.model_dump()))
    server_state.resources.append(resource)
    return resource
