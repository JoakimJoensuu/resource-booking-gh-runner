from typing import TypeVar

T = TypeVar("T")


class alist(list[T]):  # pylint: disable=invalid-name
    async def __aiter__(self):
        for _ in self:
            yield _
