from typing import Optional, Callable

from mypy.plugin import Plugin, FunctionContext
from mypy.types import Type as MypyType, TupleType


class CustomPlugin(Plugin):
    def get_function_hook(self, fullname: str) -> Optional[Callable[[FunctionContext], MypyType]]:
        if fullname != "attempt.things.build_tuple":
            return None
        return self._build_tuple_type

    def _build_tuple_type(self, ctx: FunctionContext) -> MypyType:
        fallback = ctx.api.named_generic_type("tuple", [])
        return TupleType(ctx.arg_types[0], fallback)


def plugin(version: str):
    return CustomPlugin

