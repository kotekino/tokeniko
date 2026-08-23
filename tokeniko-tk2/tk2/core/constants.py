"""The handful of names the body cannot read out of a row, because it needs them to read rows.

Everything else is data. If a constant here ever wants to become tunable, it becomes a `param` row
and leaves — that migration is the normal direction of travel, not an exception.
"""

# ------------------------------------------------------------------------------------------------
# the databases
# ------------------------------------------------------------------------------------------------

# The running tk2 body's own database. A SANDBOX until go-live (E10 moves the guard's boundary, and
# moving it is a deliberate act with the Captain's hand on it — never a config drift).
TK2_BODY_DB = "tokeniko_tk2_body"

# The dictionary-review instruments' database (`scripts/tk2/`). Named here so it can be recognised,
# NOT so it can be used: the body never writes it, and its assets cross by migration (E1), never by
# a live read across the fence.
TK2_INSTRUMENTS_DB = "tokeniko_tk2"

# tk1's live databases — the BIOGRAPHY. Named here for one reason: so the guard [T3] can refuse them
# by name and a typo in a config can never reach them. Nothing in tk2 opens these.
TK1_BODY_DBS = ("tokeniko", "tokeniko_mem", "tokeniko_memory")
