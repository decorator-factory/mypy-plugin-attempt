from typing import Any, Callable, Generic, TypeVar


T = TypeVar("T")


def struct(*fields) -> Any:
    fields_dict = dict(fields)

    class Struct:
        def __init__(self, **kwargs):
            if extra_keys := kwargs.keys() - fields_dict.keys():
                raise TypeError("Extra arguments to __init__", extra_keys)

            if missing_keys := fields_dict.keys() - kwargs.keys():
                raise TypeError("Missing arguments to __init__", missing_keys)

            self.__dict__.update(kwargs)

    return Struct


class SequenceM(Generic[T]):
    def __init__(self):
        raise NotImplementedError

    def __call__(self, *args):
        raise NotImplementedError


def sequence_m(function: Callable[..., T]) -> SequenceM[T]:
    return function  # type: ignore
