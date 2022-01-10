from attempt.things import build_tuple


# Revealed type is "Tuple[builtins.str, builtins.int, builtins.str]"
bob = build_tuple("Bob", 42, "St. Petersburg")
reveal_type(bob)