from __future__ import annotations

import inspect

from typing import TYPE_CHECKING, List, Dict, Any, Tuple, Union

from .converters import _CONVERTERS

from ..enums import CommandOptionType

if TYPE_CHECKING:
    from lefi import Interaction
    from .command import AppCommand
    from ..member import Member
    from ..user import User
    from ..channel import Channel
    from ..role import Role


class ArgumentParser:
    """A class representing an ArgumentParser.

    Parameters
    ----------
    command: :class:`AppCommand`
        The slash command.

    Attributes
    ----------
    command: :class:`AppCommand`
        The AppCommand object.
    """

    def __init__(self, command: AppCommand) -> None:
        self.command = command

    async def create_arguments(
        self, interaction: Interaction, data: List[Dict]
    ) -> list[Union[str, int, bool, Member, User, Channel, Role]]:
        """Converts each argument passed in into its respective type.

        Parameters
        ----------
        interaction: :class:`Interaction`
            The Interaction instance from the interaction with the slash command.

        data: :class:`list`
            A list containing information about each argument the user entered, with each argument being a dictionary.

        Returns
        -------
        List
            The list containing the converted arguments.
        """
        arguments: List = []
        signature = inspect.signature(self.command.callback)

        for index, argument in enumerate(start=1, iterable=data):
            parameter_name = list(signature.parameters.keys())[index]

            converter = _CONVERTERS.get(signature.parameters[parameter_name].annotation.removeprefix("lefi."))

            # Add a `client` attribute for some of the converters to use
            interaction.client = self.command.client  # type: ignore

            if inspect.iscoroutinefunction(converter.convert):  # type: ignore
                arguments.append(await converter.convert(argument, interaction))  # type: ignore

            elif callable(converter):
                arguments.append(converter.convert(argument, interaction))

        return arguments

    async def parse_arguments(self) -> List:
        """Parses each argument into their value and their type (represented by CommandOptionType)

        Returns
        -------
        List[Tuple[:class:`str`, :class:`CommandOptionType`]]
            A list containing a tuple of the value of the argument along with its type.
        """
        arguments: List = []

        signature = inspect.signature(self.command.callback)

        for index, (argument, parameter) in enumerate(signature.parameters.items()):
            if index == 0:
                continue

            if parameter.kind is parameter.POSITIONAL_OR_KEYWORD:
                arguments.append(await self.convert(parameter, argument))

        return arguments

    async def convert(self, parameter: inspect.Parameter, data: str) -> Tuple[str, Any]:
        """Converts the argument into its type (represented by CommandOptionType)

        Parameters
        ----------
        parameter: :class:`inspect.Parameter`
            A Parameter instance representing a parameter from the callback of the command.

        data: :class:`str`
            A string containing the value passed in for the argument.

        Returns
        -------
        Tuple[:class:`str`, :class:`CommandOptionType`]
            A tuple containing the value passed into the argument and its type.
        """

        argument_types: Dict[Any, int] = {
            "str": CommandOptionType.STRING,
            "int": CommandOptionType.INTEGER,
            "bool": CommandOptionType.BOOLEAN,
            "User": CommandOptionType.USER,
            "Member": CommandOptionType.MEMBER,
            "Channel": CommandOptionType.CHANNEL,
            "Role": CommandOptionType.ROLE,
        }

        if parameter.annotation is not parameter.empty:
            cleaned = parameter.annotation.removeprefix("lefi.")
            return data, argument_types[cleaned]

        return data, CommandOptionType.STRING
