from inspect import isclass

try:
    from types import UnionType  # type: ignore[attr-defined]
except ImportError:  # pragma: no cover
    from typing import Union as UnionType  # type: ignore[assignment]

try:
    from typing import TypeIs  # type: ignore[attr-defined]
except ImportError:  # pragma: no cover
    from typing_extensions import TypeIs

from typing import List, Type, Union, Any, get_args, get_origin

from simtypes.typing import ExpectedType


def check(value: Any, type: Type[ExpectedType], strict: bool = False, lists_are_tuples: bool = False) -> TypeIs[ExpectedType]:
    if type is Any:  # type: ignore[attr-defined]
        return True

    elif type is None:
        return value is None

    origin_type = get_origin(type)

    if origin_type is Union or origin_type is UnionType:
        return any(check(value, argument, strict=strict, lists_are_tuples=lists_are_tuples) for argument in get_args(type))

    elif origin_type is list and strict:
        if not isinstance(value, list):
            return False
        arguments = get_args(type)
        if not arguments:
            return True
        return all(check(subvalue, arguments[0], strict=strict, lists_are_tuples=lists_are_tuples) for subvalue in value)

    elif origin_type is dict and strict:
        if not isinstance(value, dict):
            return False
        arguments = get_args(type)
        if not arguments:
            return True
        return all(check(key, arguments[0], strict=strict, lists_are_tuples=lists_are_tuples) and check(subvalue, arguments[1], strict=strict, lists_are_tuples=lists_are_tuples) for key, subvalue in value.items())

    elif origin_type is tuple and strict:
        types_to_check: List[Union[Type[list], Type[tuple]]] = [tuple] if not lists_are_tuples else [tuple, list]
        if all(not isinstance(value, x) for x in types_to_check):
            return False

        arguments = get_args(type)

        if not arguments:
            return True

        if len(arguments) == 2 and arguments[1] is Ellipsis:
            return all(check(subvalue, arguments[0], strict=strict, lists_are_tuples=lists_are_tuples) for subvalue in value)

        if len(arguments) != len(value):
            return False

        return all(check(subvalue, expected_subtype, strict=strict, lists_are_tuples=lists_are_tuples) for subvalue, expected_subtype in zip(value, arguments))

    else:
        if origin_type is not None:
            return isinstance(value, origin_type)

        if not isclass(type):
            raise ValueError('Type must be a valid type object.')

        if type is tuple and lists_are_tuples:
            return isinstance(value, tuple) or isinstance(value, list)  # pragma: no cover

        return isinstance(value, type)
