"""The body's entry point — `task body` / `python -m tk2.body`.

An empty body that BOOTS: it opens its database, loads the r-tier into the cache, and ticks. There
is no mind in here yet — the evaluator, the loop's inner actions and the organs arrive with the
epics after E0 — but the floor they will stand on is doing its job, and doing it observably.

The one property worth watching in the log: **a parameter edited by a migration reaches the running
body on its next slow tick, without a restart** (datatier req. 3, body req. 4). That is what makes
him fixed at any moment and grown only through someone else's hands (body req. 5), and it is the
E0 gate.

The loop's EXISTENCE is dna; its cadence is a row (brain req. 8). So the tick interval is read from
the r-cache on every pass — change `body.loop.tick_seconds` with a migration and the living body
changes speed.
"""

import argparse
import logging
import signal
import time
from types import FrameType

from tk2.core import constants
from tk2.core.models import ALL_MODELS
from tk2.datatier import boot_datatier
from tk2.datatier.rcache import RCache

_log = logging.getLogger("tk2.body")

#: Flipped by SIGTERM/SIGINT. The body finishes the tick it is in and then stops — a being that
#: could be interrupted mid-thought would need every inner action to be crash-safe, and the cheaper
#: honest answer is to never interrupt one.
_stopping = False


def _logging_setup() -> None:
    """The body speaks to a log file on the mini, not to a terminal — so the timestamp is part of
    the line, never something a terminal decorates around it."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-7s %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def _handle_stop(signum: int, _frame: FrameType | None) -> None:
    global _stopping
    _stopping = True
    _log.info("signal %s — stopping after this tick", signal.Signals(signum).name)


def boot(db_name: str | None = None) -> RCache:
    """Open the database, register the models, load the r-tier. Boot = load the r-tables."""
    db, cache = boot_datatier(ALL_MODELS, db_name=db_name)

    params = len(cache.rows("params"))
    anatomy = len(cache.rows("heart_anatomy"))
    _log.info(
        "boot — db=%s · r-cache loaded: %d params, %d anatomy rows · slow tick every %ds",
        db.name,
        params,
        anatomy,
        cache.refresh_seconds,
    )
    if params == 0:
        _log.warning(
            "the r-tier is EMPTY — this database has never been migrated. "
            "Run `python tools/migrate.py --db %s` and start again.",
            db.name,
        )
    return cache


def tick(number: int, cache: RCache) -> None:
    """ONE bounded unit of work, then yield.

    The body never runs an unbounded step: a tick that could outlast its own slow-tick refresh would
    act on parameters that have already changed.

    Today the unit of work is the reconciliation itself plus an honest report of what he is holding.
    The inner actions land in E6; this is the shape they will be called from.
    """
    if cache.maybe_refresh():
        _log.info("slow tick — r-cache refreshed from the db")

    _log.info(
        "tick %d — %s=%s · tick every %ss · refresh every %ss",
        number,
        constants.DICTIONARY_EPOCH_PARAM,
        cache.param(constants.DICTIONARY_EPOCH_PARAM),
        cache.param(constants.BODY_TICK_PARAM, constants.BODY_TICK_DEFAULT),
        cache.refresh_seconds,
    )


def run(cache: RCache, max_ticks: int | None = None) -> int:
    """The loop. Returns how many ticks it ran.

    `max_ticks` is for the gate and the tests; the body itself runs until something stops it.
    """
    number = 0
    while not _stopping and (max_ticks is None or number < max_ticks):
        number += 1
        tick(number, cache)

        if _stopping or (max_ticks is not None and number >= max_ticks):
            break

        # Re-read every pass: the cadence is a row, so a migration can change how fast he lives.
        interval = cache.param(constants.BODY_TICK_PARAM, constants.BODY_TICK_DEFAULT)
        try:
            interval = float(interval)
        except (TypeError, ValueError):
            interval = float(constants.BODY_TICK_DEFAULT)
        if interval <= 0:
            interval = float(constants.BODY_TICK_DEFAULT)

        # Slept in small slices so a stop signal is honoured promptly rather than one interval late.
        slept = 0.0
        while slept < interval and not _stopping:
            step = min(0.25, interval - slept)
            time.sleep(step)
            slept += step

    return number


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="the tokeniko 2 body")
    parser.add_argument("--db", default=None, help="database to boot against (default: the body's)")
    parser.add_argument(
        "--max-ticks",
        type=int,
        default=None,
        help="stop after this many ticks (for the gate and the tests; unset = run until stopped)",
    )
    args = parser.parse_args(argv)

    _logging_setup()
    signal.signal(signal.SIGTERM, _handle_stop)
    signal.signal(signal.SIGINT, _handle_stop)

    _log.info("tokeniko 2 — the body, waking")
    cache = boot(args.db)
    ran = run(cache, max_ticks=args.max_ticks)
    _log.info("the body sleeps — %d tick(s)", ran)


if __name__ == "__main__":
    main()
