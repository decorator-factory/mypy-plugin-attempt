from attempt.things import struct, sequence_m

UserInfo = struct(
    ("name", "string"),
    ("age", "integer"),
    ("city", "string?"),
)


u1 = UserInfo()  # error

u2 = UserInfo(  # ok
    name="Bob",
    age=42,
    city="St. Petersburg",
)

u3 = UserInfo(  # ok
    name="Bob",
    age=42,
    city=None,
)

u4 = UserInfo(  # error
    name="Bob",
    age=42,
)

u4 = UserInfo(  # error
    name="Charlie",
    age="old",
    city=None
)


def f(u: UserInfo):
    reveal_type(u.name)
    reveal_type(u.city)


###


from typing import Awaitable


@sequence_m
def my_gather(*args) -> Awaitable:
    ...


async def foo() -> int:
    return 42

async def bar() -> str:
    return "hey"

async def main() -> None:
    x = await my_gather(foo(), bar(), bar())
    reveal_type(x)  # tuple[int, str, str]