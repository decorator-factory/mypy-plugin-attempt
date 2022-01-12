from typing import Any


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
