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

# The tests' database. Named — not patterned — because a guard that accepts a SHAPE accepts every
# typo that happens to fit it. The test suite creates and drops this one and nothing else.
TK2_BODY_TEST_DB = "tokeniko_tk2_body_test"

# The dictionary-review instruments' database (`scripts/tk2/`). Named here so it can be recognised,
# NOT so it can be used: the body never writes it, and its assets cross by migration (E1), never by
# a live read across the fence.
TK2_INSTRUMENTS_DB = "tokeniko_tk2"

# tk1's live databases — the BIOGRAPHY. Named here for one reason: so the guard can refuse them by
# name and a typo in a config can never reach them. Nothing in tk2 opens these.
TK1_BODY_DBS = ("tokeniko", "tokeniko_mem", "tokeniko_memory")

# THE WHITELIST. The guard opens these and refuses every other name in existence — the refusal is
# the default, and being allowed is the thing that must be written down. Growing this tuple is a
# deliberate act; go-live (E10) is the one planned occasion.
DB_WHITELIST = frozenset({TK2_BODY_DB, TK2_BODY_TEST_DB})

# ------------------------------------------------------------------------------------------------
# the parameter store — the shape the r-cache reads
# ------------------------------------------------------------------------------------------------

# A `param` collection is a key/value store, and the r-cache indexes it by these two fields. The
# collection model itself lands in T4; this is the seam it has to honour, declared where the reader
# lives rather than left as a thing both sides happen to agree on.
PARAM_KEY_FIELD = "key"
PARAM_VALUE_FIELD = "value"

# The slow tick's own interval is a parameter row like any other — the refresh rate is itself
# refreshable, which is the honest version of "parameter edits land live" (body req. 4). The default
# below is the BOOTSTRAP value only: it holds until the first load finds the row, and it exists
# because the cache has to be able to read the db before it can read its own settings.
RCACHE_INTERVAL_PARAM = "datatier.rcache.refresh_seconds"
RCACHE_INTERVAL_DEFAULT = 60
