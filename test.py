from attempt.things import struct

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

