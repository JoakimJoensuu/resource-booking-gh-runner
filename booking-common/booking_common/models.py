from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class JobInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")
    run_id: int = Field(examples=[5672835261])
    job_id: int = Field(examples=[15367862127])
    repo_owner: str = Field(examples=["JoakimJoensuu"])
    repo_name: str = Field(examples=["resource-booking-gh-runner"])


class RequestedResource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: str = Field(examples=["big_machine"])
    identifier: None | str = Field(examples=["floor_3"], default=None)

    model_config = ConfigDict(extra="forbid")


class BookingRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(examples=["Some One"])
    resource: RequestedResource
    start_time: datetime
    end_time: datetime
    github: JobInfo | None = None


class BookingStatus(str, Enum):
    CANCELLED = "CANCELLED"
    FINISHED = "FINISHED"
    WAITING = "WAITING"
    ON = "ON"


class BookingInfo(BookingRequest):
    model_config = ConfigDict(extra="forbid")
    id: int
    booking_time: datetime
    status: BookingStatus


class ResourceInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: str
    identifier: str
    # TODO: Allow adding arbitrary commands to be ran when resource is reserved or freed


class BookingResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    info: BookingInfo
    used_resource: ResourceInfo | None
