from attempt.things import struct

UserInfo = struct(
    ("name", "string"),
    ("city", "string?"),
)

def f(u: UserInfo):
    reveal_type(u.name)
    reveal_type(u.city)

