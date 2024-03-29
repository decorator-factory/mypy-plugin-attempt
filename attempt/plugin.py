from typing import Optional, Callable

from mypy.plugins.common import add_method_to_class
from mypy.plugin import Plugin, DynamicClassDefContext, MethodContext
from mypy.maptype import map_instance_to_supertype
from mypy.types import (
    TypeOfAny,
    AnyType,
    Type as MypyType,
    Instance,
    NoneType,
    UnionType,
    TupleType,
)

from mypy.nodes import (
    TypeInfo,
    ClassDef,
    SymbolTable,
    SymbolTableNode,
    MDEF,
    GDEF,
    Block,
    StrExpr,
    TupleExpr,
    Var,
    Argument,
    ArgKind,
)


class CustomPlugin(Plugin):
    def get_method_hook(self, fullname: str) -> Optional[Callable[[MethodContext], MypyType]]:
        if not fullname.startswith("attempt."):
            return None

        if fullname == "attempt.things.Gathers.__call__":
            return self._gathers_type

        return None

    def _gathers_type(self, ctx: MethodContext) -> MypyType:
        if not isinstance(ctx.type, Instance):
            ctx.api.fail(f"Expected named type as instance type, got {0}".format(ctx.type), ctx)
            return ctx.default_return_type

        tuple_type = ctx.api.named_generic_type("builtins.tuple", [])

        gathers_param = ctx.type.args[0]
        if not isinstance(gathers_param, Instance):
            ctx.api.fail(f"Expected type constructor as parameter to Gathers", ctx)
            return ctx.default_return_type
        type_constructor = gathers_param.type

        inner_types: list[MypyType] = []
        for t in ctx.arg_types[0]:
            if not isinstance(t, Instance):
                ctx.api.fail("Only support simple types for now, sorry!", t)
                inner_types.append(AnyType(TypeOfAny.explicit))
                continue
            unified = map_instance_to_supertype(t, type_constructor)
            inner_types.append(unified.args[0])

        return Instance(
            type_constructor,
            [TupleType(inner_types, tuple_type)]
        )

    def get_dynamic_class_hook(self, fullname: str) -> Optional[Callable[[DynamicClassDefContext], None]]:
        if fullname == "attempt.things.struct":
            return self._build_struct_type

        return None

    def _build_struct_type(self, ctx: DynamicClassDefContext) -> None:
        field_types: dict[str, MypyType] = {}

        for arg in ctx.call.args:
            if not isinstance(arg, TupleExpr):
                ctx.api.fail("Expected a two-element tuple as struct field", arg)
                return

            count = len(arg.items)
            if count != 2:
                ctx.api.fail("Expected 2 items in struct field tuple, found {0}".format(count), arg)
                return

            key_expr, value_expr = arg.items
            if not isinstance(key_expr, StrExpr):
                ctx.api.fail("Expected string literal as the first element of the tuple", key_expr)
                return

            if not isinstance(value_expr, StrExpr):
                ctx.api.fail("Expected string literal as the second element of the tuple", key_expr)
                return

            key = key_expr.value
            value = value_expr.value

            int_type = ctx.api.named_type("builtins.int")
            str_type = ctx.api.named_type("builtins.str")

            value_type: MypyType

            if value == "string":
                value_type = str_type
            elif value == "string?":
                value_type = UnionType([str_type, NoneType()])
            elif value == "integer":
                value_type = int_type
            elif value == "integer?":
                value_type = UnionType([int_type, NoneType()])
            else:
                ctx.api.fail("Expected string, string?, integer, integer?, got {0}".format(value), value_expr)
                return

            field_types[key] = value_type

        vars = {
            name: Var(name, field_type)
            for name, field_type in field_types.items()
        }

        fields = {
            name: SymbolTableNode(MDEF, var)
            for name, var in vars.items()
        }

        class_def = ClassDef(ctx.name, Block([]))
        class_def.fullname = ctx.api.qualified_name(ctx.name)

        table = SymbolTable(fields)
        info = TypeInfo(table, class_def, ctx.api.cur_mod_id)

        object_type: Instance = ctx.api.named_type("builtins.object")
        info.bases = [object_type]
        info.mro = [info, object_type.type]

        class_def.info = info

        init_args = [
            Argument(Var(name, typ), typ, None, ArgKind.ARG_NAMED)
            for name, typ in field_types.items()
        ]
        add_method_to_class(ctx.api, class_def, "__init__", init_args, return_type=NoneType())

        for var in vars.values():
            var.info = info

        ctx.api.add_symbol_table_node(ctx.name, SymbolTableNode(GDEF, info, plugin_generated=True))


def plugin(version: str):
    return CustomPlugin
