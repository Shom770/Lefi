from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Callable, ClassVar
import re


if TYPE_CHECKING:
    from lefi import Interaction
    from ...client import Client
    from ..member import Member
    from ..user import User

__all__ = ("Converter",)


class Converter:
    _ID_REGEX = re.compile(r'([0-9]{15,20})$')

    def __init__(self, client: Client) -> None:
        self.client = client

        self.CONVERTER_MAPPING: Dict[int, Callable] = {
            3: self._str,
            4: self._int,
            5: self._bool,
            6: self.user,
            7: self.member,
        }

    def _str(self, data: Dict) -> str:
        return data["value"]

    def _int(self, data: Dict) -> int:
        return int(data["value"])

    def _bool(self, data: Dict) -> bool:
        return bool(data["value"])

    async def user(self, data: Dict) -> User:
        user_id: int = int(data["value"])

        if user := self.client.get_user(user_id):
            return user

        data = await self.client.http.get_user(user_id)
        return self.client._state.add_user(data)

    async def member(self, data: Dict, interaction: Interaction) -> Member:
        data["value"] = int(data["value"])
        guild = interaction.guild

        return guild.get_member(data["value"]) or await guild.fetch_member(data["value"])
