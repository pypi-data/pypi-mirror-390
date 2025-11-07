from typing import Type, get_origin
from json import loads, JSONDecodeError
from inspect import isclass

from simtypes import check
from simtypes.typing import ExpectedType


def from_string(value: str, expected_type: Type[ExpectedType]) -> ExpectedType:
    if not isinstance(value, str):
        raise ValueError(f'You can only pass a string as a string. You passed {type(value).__name__}.')

    origin_type = get_origin(expected_type)

    if any(x in (dict, list, tuple) for x in (expected_type, origin_type)):
        type_name = expected_type.__name__ if origin_type is None else origin_type.__name__
        error_message = f'The string "{value}" cannot be interpreted as a {type_name} of the specified format.'

        try:
            result = loads(value)
        except JSONDecodeError as e:
            raise TypeError(error_message) from e

        if not check(result, expected_type, strict=True, lists_are_tuples=True):  # type: ignore[operator]
            raise TypeError(error_message)

        return result

    elif expected_type is str:
        return value  # type: ignore[return-value]

    elif expected_type is bool:
        if value in ('True', 'true', 'yes'):
            return True  # type: ignore[return-value]
        elif value in ('False', 'false', 'no'):
            return False  # type: ignore[return-value]
        else:
            raise TypeError(f'The string "{value}" cannot be interpreted as a boolean value.')

    elif expected_type is int:
        try:
            return int(value)  # type: ignore[return-value]
        except ValueError as e:
            raise TypeError(f'The string "{value}" cannot be interpreted as an integer.') from e

    elif expected_type is float:
        if value == '∞':
            value = 'inf'
        elif value == '-∞':
            value = '-inf'

        try:
            return float(value)  # type: ignore[return-value]
        except ValueError as e:
            raise TypeError(f'The string "{value}" cannot be interpreted as a floating point number.') from e

    if not isclass(expected_type):
        raise ValueError('The type must be a valid type object.')

    raise TypeError(f'Serialization of the type {expected_type.__name__} you passed is not supported. Supported types: int, float, bool, list, dict, tuple.')
