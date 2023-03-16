# mypy-plugin-attempt

Turns out it's not very easy, because there's not a lot of documentation on `mypy`'s part; and the internals of `mypy` are a bit messy and hard to understand.

I hope it's at least somewhat helpful if you're making your own `mypy` plugin. You can see a brief demo in `test.py`.
I have tested this plugin with `mypy==1.1.1` and `mypy==0.931`.

I was able to achieve two humble goals with this plugin:

## Defining "structs" with typed fields

Something similar to `dataclasses` or `namedtuple`.

```py
UserInfo = struct(
    ("name", "string"),
    ("age", "integer"),
    ("city", "string?"),
)

###

u3 = UserInfo(  # ok
    name="Bob",
    age=42,
    city=None,
)

u4 = UserInfo(  # error
    name="Charlie",
    age="old",
    city=None
)


def f(u: UserInfo):
    reveal_type(u.name)  # inferred type: str
    reveal_type(u.city)  # inferred type: str | None
```

## Typing `asyncio.gather`

Python's "type system" doesn't support this kind of transformation:
```
() -> Aw[tuple()]
(Aw[T1]) -> Aw[tuple[T1,]]
(Aw[T1], Aw[T2]) -> Aw[tuple[T1, T2]]
(Aw[T1], Aw[T2], Aw[T3]) -> Aw[tuple[T1, T2, T3]]
```
So pretty fundamental functions like `asyncio.gather` have to resort to a [staircase of overloads](https://github.com/python/typeshed/blob/bcff9cd51f1f1572e235b7d9e2c23411711491e1/stdlib/asyncio/tasks.pyi#L66-L235).

The `gathers` decorator lets you express this transformation. It doesn't do anything at runtime.

```py
@gathers
def my_gather(*args) -> Awaitable:
    ...


async def foo() -> int:
    return 42

async def bar() -> str:
    return "hey"

async def main() -> None:
    x = await my_gather(foo(), bar(), bar())
    reveal_type(x)  # tuple[int, str, str]
```
