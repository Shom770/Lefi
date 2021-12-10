from __future__ import annotations

from typing import Dict, Generic, Tuple, Type, TypeVar, Union
import inspect
import sys


__all__ = (
    "Converter",
    "StringConverter",
    "IntegerConverter",
    "BooleanConverter",
    "UserConverter",
    "MemberConverter",
    "ChannelConverter",
    "RoleConverter",
)

T_co = TypeVar("T_co", covariant=True)


class ConverterMeta(type):
    __convert_type__: Type

    def __new__(cls: Type[ConverterMeta], name: str, bases: Tuple[Type, ...], attrs: dict) -> ConverterMeta:
        attrs["__convert_type__"] = attrs["__orig_bases__"][0].__args__[0]
        return super().__new__(cls, name, bases, attrs)


class Converter(Generic[T_co], metaclass=ConverterMeta):
    """
    A base converter class.

    All converters should inherit this class.
    """

    @staticmethod
    def convert(data: Dict, interaction: "Interaction") -> T_co:  # type: ignore
        raise NotImplementedError


class StringConverter(Converter["str"]):
    @staticmethod
    def convert(data: Dict, interaction: "Interaction") -> str:  # type: ignore
        """
        Returns the string passed in.

        Parameters
        ----------
        data: :class:`dict`
            The data of the argument containing information about the value passed in

        interaction: :class:`Interaction`
            The Interaction instance from the interaction with the slash command.

        Returns
        -------
        :class:`str`
            The string passed in
        """
        return data["value"]


class IntegerConverter(Converter["int"]):
    @staticmethod
    def convert(data: Dict, interaction: "Interaction") -> int:  # type: ignore
        """
        Converts a string to an integer.

        Parameters
        ----------
        data: :class:`dict`
            The data of the argument containing information about the value passed in

        interaction: :class:`Interaction`
            The Interaction instance from the interaction with the slash command.

        Returns
        -------
        :class:`int`
            The string passed in, converted into an integer
        """
        return int(data["value"])


class BooleanConverter(Converter["bool"]):
    @staticmethod
    def convert(data: Dict, interaction: "Interaction") -> bool:  # type: ignore
        """
        Converts a string to a boolean.

        Parameters
        ----------
        data: :class:`dict`
            The data of the argument containing information about the value passed in

        interaction: :class:`Interaction`
            The Interaction instance from the interaction with the slash command.

        Returns
        -------
        :class:`bool`
            The string passed in, converted into a boolean.
        """
        return bool(data["value"])


class UserConverter(Converter["User"]):  # type: ignore
    @staticmethod
    async def convert(data: Dict, interaction: "Interaction") -> "User":  # type: ignore
        """
        Converts the ID passed in into a User.

        Parameters
        ----------
        data: :class:`dict`
            The data of the argument containing information about the value passed in

        interaction: :class:`Interaction`
            The Interaction instance from the interaction with the slash command.

        Returns
        -------
        :class:`User`
            The User instance from the ID given.
        """
        user_id: int = int(data["value"])

        if user := interaction.client.get_user(user_id):
            return user

        data = await interaction.client.fetch_user(user_id)
        return interaction.client._state.add_user(data)


class MemberConverter(Converter["Member"]):  # type: ignore
    @staticmethod
    async def convert(data: Dict, interaction: "Interaction") -> "Member":  # type: ignore
        """
        Converts the ID passed in into a Member.

        Parameters
        ----------
        data: :class:`dict`
            The data of the argument containing information about the value passed in

        interaction: :class:`Interaction`
            The Interaction instance from the interaction with the slash command.

        Returns
        -------
        :class:`Member`
            The Member instance from the ID given.
        """
        member_id: int = int(data["value"])
        guild = interaction.guild

        return guild.get_member(member_id) or await guild.fetch_member(member_id)


class ChannelConverter(Converter["Channel"]):  # type: ignore
    @staticmethod
    def convert(data: Dict, interaction: "Interaction") -> "Channel":  # type: ignore
        """
        Converts the channel ID passed in into a Channel.

        Parameters
        ----------
        data: :class:`dict`
            The data of the argument containing information about the value passed in

        interaction: :class:`Interaction`
            The Interaction instance from the interaction with the slash command.

        Returns
        -------
        :class:`Channel`
            The Channel instance from the ID given.
        """
        channel_id: int = int(data["value"])
        guild = interaction.guild

        return guild.get_channel(channel_id)


class RoleConverter(Converter["Role"]):  # type: ignore
    @staticmethod
    def convert(data: Dict, interaction: "Interaction") -> "Role":  # type: ignore
        """
        Converts the role ID passed in into a Role.

        Parameters
        ----------
        data: :class:`dict`
            The data of the argument containing information about the value passed in

        interaction: :class:`Interaction`
            The Interaction instance from the interaction with the slash command.

        Returns
        -------
        :class:`Role`
            The Role instance from the ID given.
        """
        role_id: int = int(data["value"])
        guild = interaction.guild

        return guild.get_role(role_id)


_CONVERTERS: Dict[str, Union[Type[Converter], Converter]] = {}
for name, object in inspect.getmembers(sys.modules[__name__], inspect.isclass):
    if not issubclass(object, Converter) or name == "Converter":
        continue

    _CONVERTERS[object.__convert_type__.__forward_arg__] = object
