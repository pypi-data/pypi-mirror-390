"""Define /user endpoints."""
from typing import Awaitable, Callable

from .const import GET_HOMES_URL, GET_USER_URL


class User:  # pylint: disable=too-few-public-methods
    """Define an object to handle the endpoints."""

    def __init__(self, request: Callable[..., Awaitable]) -> None:
        """Initialize."""
        self._request: Callable[..., Awaitable] = request

    async def get_info(
        self
    ) -> dict:
        """Return user account data.

        :rtype: ``dict``
        """
        

        user_info: dict = await self._request(
            "get",
            GET_USER_URL
        )

        for items in user_info['data']:
            return items

    async def get_homes(
        self
    ) -> dict:
        """Return user homes data

        :rtype: ``dict``
        """

        homes_info: dict = await self._request(
            "get",
            GET_HOMES_URL
        )

        return homes_info['data']