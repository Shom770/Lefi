from __future__ import annotations

import inspect

from typing import TYPE_CHECKING, List, Dict, Any, Tuple

from .converters import Converter

from ..enums import CommandOptionType

if TYPE_CHECKING:
    from lefi import Interaction
    from .command import AppCommand

__all__ = ("ArgumentParser",)


class ArgumentParser:
    def __init__(self, command: AppCommand) -> None:
        self.converter = Converter(command.client)
        self.command = command

    async def create_arguments(self, interaction: Interaction, data: List[Dict]) -> List:
        arguments: List = []
        signature = inspect.signature(self.command.callback)

        for index, input in enumerate(start=1, iterable=data):
            parameter_name = list(signature.parameters.keys())[index]

            if signature.parameters[parameter_name].annotation == "lefi.Member":
                corresponding_value = 7
            else:
                corresponding_value = input["type"]
            converter = self.converter.CONVERTER_MAPPING[corresponding_value]
            if inspect.iscoroutinefunction(converter):
                # passes input if the converter isn't the Member converter, otherwise pass in both arguments below
                to_pass = (input,) if corresponding_value != 7 else (input, interaction)

                arguments.append(await converter(*to_pass))

            elif callable(converter):
                arguments.append(converter(input))

        return arguments

    async def parse_arguments(self) -> List:
        arguments: List = []

        signature = inspect.signature(self.command.callback)

        for index, (argument, parameter) in enumerate(signature.parameters.items()):
            if index == 0:
                continue

            if parameter.kind is parameter.POSITIONAL_OR_KEYWORD:
                arguments.append(await self.convert(parameter, argument))

        return arguments

    async def convert(self, parameter: inspect.Parameter, data: str) -> Tuple[str, Any]:
        argument_types: Dict[Any, int] = {
            "str": CommandOptionType.STRING,
            "int": CommandOptionType.INTEGER,
            "bool": CommandOptionType.BOOLEAN,
            "User": CommandOptionType.USER,
            "Member": CommandOptionType.MEMBER,
        }

        if parameter.annotation is not parameter.empty:
            cleaned = parameter.annotation.removeprefix("lefi.")
            return data, argument_types[cleaned]

        return data, CommandOptionType.STRING
