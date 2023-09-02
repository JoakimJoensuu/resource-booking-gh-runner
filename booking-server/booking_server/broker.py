import asyncio

from booking_common.models import JobInfo
from booking_server.booking import Booking, BookingStatus, find_waiting_booking
from booking_server.resource import Resource, find_free_resource
from fastcore.basics import AttrDict
from ghapi.all import GhApi


async def re_run_github_job(github: JobInfo, github_token: str):
    api = GhApi(github.repo_owner, github.repo_name, github_token)

    while True:
        run_info: AttrDict = api.actions.get_workflow_run(run_id=github.run_id)
        print(run_info["status"])
        if run_info["status"] == "completed":
            break
        await asyncio.sleep(0.5)

    api.actions.re_run_job_for_workflow_run(job_id=github.job_id)


def assign_to_each_others(resource: Resource, booking: Booking):
    booking.info.status = BookingStatus.ON
    booking.used_resource = resource
    resource.used_by = booking
    booking.event.set()
    booking.event.clear()


async def try_assigning_new_resource(
    booking: Booking, resources: list[Resource], github_token: str
):
    # TODO: What if booking was deleted from server data before this is
    # ran and this still holds the reference to the object

    if booking.info.status != BookingStatus.WAITING:
        return

    requested = booking.info.resource

    resource = find_free_resource(requested, resources)

    if resource is None:
        return

    assign_to_each_others(resource, booking)

    if booking.info.github is not None:
        await re_run_github_job(booking.info.github, github_token)


async def try_assigning_to_booking(
    resource: Resource, bookings: list[Booking], github_token: str
):
    # TODO: What if resource is deleted before this runs and this still
    # holds the reference to the object

    if resource.used_by is not None:
        return

    booking = find_waiting_booking(resource, bookings)

    if booking is None:
        return

    assign_to_each_others(resource, booking)

    if booking.info.github is not None:
        await re_run_github_job(booking.info.github, github_token)
