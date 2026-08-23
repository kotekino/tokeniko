"""The body's entry point — `task body` / `python -m tk2.body`.

STUB (E0/T1). It boots, ticks once, and exits clean. That is the whole claim: the keel floats.

What it deliberately does NOT do yet: open Mongo, load the r-tables, or loop. Boot = load the
r-tables and a slow tick reconciles (body req. 4) — that is T3's datatier and T5's migrations. The
shape below is the shape that grows: boot() acquires what the body needs, tick() does ONE bounded
unit of work, main() sequences them. When the loop arrives it replaces the single call in main(),
and nothing else moves.
"""

import logging

from tk2.core.constants import TK2_BODY_DB

_log = logging.getLogger("tk2.body")


def _logging_setup() -> None:
    """The body speaks to a log file on the mini, not to a terminal — so the timestamp is part of
    the line, never something a terminal decorates around it."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-7s %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def boot() -> None:
    """Everything the body needs before its first tick. Empty by construction until there is a
    datatier to boot [T3]."""
    _log.info("boot — db=%s (not opened yet: the loop is wired to the datatier in T5)", TK2_BODY_DB)


def tick(n: int) -> None:
    """ONE bounded unit of work, then yield. The body never runs an unbounded step: a tick that can
    outlast its own slow-tick refresh could act on parameters that have already changed."""
    _log.info("tick %d — nothing to do yet, and saying so honestly", n)


def main() -> None:
    _logging_setup()
    _log.info("tokeniko 2 — the body, waking")
    boot()
    tick(1)
    _log.info("the body sleeps (stub: one tick, then a clean exit)")


if __name__ == "__main__":
    main()
