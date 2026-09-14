"""THE DICTIONARY BENCH — a page to walk the geometry, and a stopwatch on every query.

    PYTHONPATH=. ../.venv/bin/python tools/dictionary_server.py
    PYTHONPATH=. ../.venv/bin/python tools/dictionary_server.py --db tokeniko_tk2 --port 8770

WHY A SERVER AND NOT A FILE. `tools/base_map.py` writes a self-contained page and that is right for
a map: a projection is a picture and a picture can be baked. This is not a picture. The Captain's
ask was to test the QUERY OPERATIONS — «we lost the pure squared matrix we had in tk1» — and a page
with the answers baked into it would be a page that measures nothing. So the page asks, the process
answers out of the real space, and every reply carries the milliseconds it took.

WHAT IT EXERCISES is `tk2.dictionary.space.DictionarySpace`, which is not scaffolding: it is the
reader E2 and E3 need, and the shape it has is a consequence of numbers rather than taste. The
measurements that decided it are in that module's own head. The short version is that the sparse
trick does not work — `eat.v` shares a D column with 53% of the base — so the dictionary is held
dense and in memory, 83 MB, and every question after that is arithmetic.

NO NEW DEPENDENCY: `http.server` from the standard library, one thread, localhost by default. It is
an instrument on the workshop bench, not a service — there is no auth here and there should not be
one, because the moment it needs auth it has stopped being a bench.
"""

import argparse
import json
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tk2.core import constants
from tk2.core.models import BaseKeyDoc, BaseRelationDoc, BaseDistributionDoc, SenseVectorDoc
from tk2.datatier.guard import guard_db_name
from tk2.datatier.policy_source import standing_bar, standing_policy
from tk2.dictionary import policy
from tk2.dictionary.space import DictionarySpace

PAGE = Path(__file__).resolve().parent / "dictionary_bench.html"


def load(db_name: str, build_label: str | None):
    """The space, out of the body's own rows. Timed, because the load IS one of the measurements."""
    from pymongo import MongoClient

    from tk2.core import config as settings

    guard_db_name(db_name)
    db = MongoClient(settings.MONGO_URI,
                     serverSelectionTimeoutMS=settings.SERVER_SELECTION_TIMEOUT_MS)[db_name]

    rows, policy_source = standing_policy(None)
    _bar, bar_rows, _bar_source = standing_bar(None)
    config = policy.config_from_rows(rows, bar_rows)

    label = build_label
    if label is None:
        seen = db[BaseKeyDoc.Settings.name].find_one({}, {"build": 1})
        if seen is None:
            raise SystemExit(f"{db_name} holds no base — has a build been applied?")
        label = seen["build"]

    from tk2.datatier.matrix_store import MongoMatrixStore

    store = MongoMatrixStore(db)
    version = policy.policy_version(rows)

    started = time.time()
    dimensions = [d["key"] for d in
                  db[BaseKeyDoc.Settings.name].find({"build": label}).sort("index", 1)]
    space = DictionarySpace(
        config,
        dimensions,
        db[BaseRelationDoc.Settings.name].find({"build": label}),
        db[BaseDistributionDoc.Settings.name].find({"build": label}),
        db[SenseVectorDoc.Settings.name].find({"build": label}),
        # The provenance the dirty-check compares against. Recorded at load, so the bench can be
        # asked whether the rows have moved under it — which is the whole point of the check
        # existing before there is a phase to act on it.
        origin=store.origin(label, policy_version=version),
    )
    elapsed = time.time() - started
    return space, config, label, elapsed, policy_source, store, version


def projection(space) -> dict:
    """A 2D layout of the base, and the honesty number beside it.

    PCA rather than the map's t-SNE, and the reason is the bench's own: this reloads on every
    restart and a t-SNE is minutes. What it keeps of D's variance is printed on the page, because a
    projection that does not say how much it threw away is a picture pretending to be a measurement.
    """
    matrix = space._distributional  # D's unit rows — the map is a PROPOSAL, and D is what proposes
    centred = matrix - matrix.mean(axis=0)
    U, S, _ = np.linalg.svd(centred, full_matrices=False)
    xy = U[:, :2] * S[:2]
    kept = float((S[:2] ** 2).sum() / (S ** 2).sum())
    span = np.abs(xy).max() or 1.0
    return {
        "xy": [[round(float(x / span), 4), round(float(y / span), 4)] for x, y in xy],
        "kept": round(kept * 100, 1),
    }


class Bench(BaseHTTPRequestHandler):
    space = None
    config = None
    label = ""
    load_seconds = 0.0
    policy_source = ""
    layout = None
    store = None
    policy_version = None

    def log_message(self, *_args):
        """Silent: the page shows the timings, and a request log would bury them."""

    def do_GET(self):
        route = urlparse(self.path)
        query = {k: v[0] for k, v in parse_qs(route.query).items()}
        if route.path in ("/", "/index.html"):
            return self._send(PAGE.read_text(), "text/html; charset=utf-8")
        handler = getattr(self, "_api" + route.path.replace("/", "_"), None)
        if handler is None:
            return self._send(json.dumps({"error": "no such operation"}), "application/json", 404)

        started = time.perf_counter()
        try:
            payload = handler(query)
        except Exception as error:  # the bench reports its own failures rather than dying silently
            payload = {"error": f"{type(error).__name__}: {error}"}
        payload["ms"] = round((time.perf_counter() - started) * 1000, 3)
        return self._send(json.dumps(payload), "application/json")

    def _send(self, body: str, kind: str, status: int = 200):
        raw = body.encode()
        self.send_response(status)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    # -- the operations, one route each -----------------------------------------------------------

    def _api_about(self, _query):
        stats = self.space.stats()
        reading = self.config.reading
        return {
            "build": self.label,
            "policy_source": self.policy_source,
            "config_fingerprint": self.config.fingerprint(),
            "load_seconds": round(self.load_seconds, 2),
            "resident_mb": round(stats["resident_bytes"] / 1e6, 1),
            "dimensions": stats["dimensions"],
            "senses": stats["senses"],
            "mix": reading.mix,
            "near_floor": reading.near_floor,
            "far_ceiling": reading.far_ceiling,
            "bar": [[p.a, p.b, p.verdict] for p in self.config.bar],
            "layout": self.layout,
            "keys": list(self.space.dimensions),
        }

    def _api_resolve(self, query):
        """word -> the dimensions it occupies, each with its senses. The station's first question."""
        word = query.get("word", "")
        found = self.space.resolve(word)
        return {
            "word": word,
            "dimensions": [
                {
                    "key": key,
                    "relations": [
                        {"column": c, "relation": r, "weight": w}
                        for c, r, w in self.space.relations_of(key)
                    ],
                    "senses": [
                        {"key": s.key, "ordinal": s.ordinal, "synset": s.synset,
                         "definition": s.definition,
                         "relations": [{"column": c, "relation": r, "weight": w}
                                       for c, r, w in s.relations]}
                        for s in self.space.senses_of(key)
                    ],
                }
                for key in found
            ],
            # A word need not be a dimension at all — most are not — and its readings still have a
            # place. This is the half E1c added and the half `resolve` alone cannot show.
            "placed": {
                sense: [{"key": n.key, "cosine": round(n.cosine, 4), "verdict": n.verdict}
                        for n in neighbours]
                for sense, neighbours in self.space.place(word, count=8).items()
            },
        }

    def _api_neighbours(self, query):
        """«memory proposes by cosine» — the operation the brain performs most."""
        key = query.get("key", "")
        count = int(query.get("count", 15))
        return {
            "key": key,
            "held": self.space.holds(key),
            "neighbours": [
                {"key": n.key, "cosine": round(n.cosine, 4), "verdict": n.verdict}
                for n in self.space.neighbours(key, count)
            ],
        }

    def _api_compare(self, query):
        """Two keys, BOTH LAYERS APART, and the verdict — which is R's alone (policy v11)."""
        left, right = query.get("a", ""), query.get("b", "")
        reading = self.space.read(left, right)
        if reading is None:
            return {"a": left, "b": right, "verdict": "ABSTAIN", "known": False, "stated": []}
        return {
            "a": left, "b": right, "known": True,
            "verdict": reading.verdict,
            "source": reading.source,
            "proposal": reading.proposal,
            "relational": {"cosine": round(reading.relational_cosine, 4),
                           "cell": round(reading.relational_cell, 4)},
            "distributional": {"cosine": round(reading.distributional_cosine, 4),
                               "cell": round(reading.distributional_cell, 4)},
            "stated": [
                {"column": c, "relation": r, "weight": w}
                for c, r, w in self.space.relations_of(left) if c == right
            ],
        }

    def _api_anchor(self, query):
        """THE SEMANTIC CATCH: any word to the nearest of a small declared set.

        Takes a WORD rather than a key, because the whole point is arbitrary input — and a word
        outside the base reaches the space through its senses (`place`), which is what E1c bought.
        """
        word = query.get("word", "")
        anchors = [a for a in query.get("anchors", "").split(",") if a]
        direct = self.space.nearest_anchor(word, anchors) if self.space.holds(word) else None
        by_sense = {}
        if direct is None:
            for sense in self.space.place(word, count=1):
                vector = self.space.project(sense)
                if vector is None:
                    continue
                held = [a for a in anchors if self.space.holds(a)]
                if not held:
                    continue
                scored = sorted(
                    ((a, float(vector @ self.space._distributional[self.space._index[a]])) for a in held),
                    key=lambda pair: -pair[1],
                )
                best, reading = scored[0]
                by_sense[sense] = {"anchor": best, "cosine": round(reading, 4),
                                   "verdict": self.config.reading.verdict(reading)}
        return {
            "word": word,
            "anchors": anchors,
            "direct": None if direct is None else
                      {"anchor": direct.key, "cosine": round(direct.cosine, 4),
                       "verdict": direct.verdict},
            "by_sense": by_sense,
        }

    def _api_staleness(self, _query):
        """THE DIRTY-CHECK, as the body will run it on a tick: one cheap read, and the REASON.

        11.8 ms against the body over the network, against seven seconds for a reload — which is
        the ratio that lets a tick ask every time and no tick reload. Three things move it: a new
        build beside the old, a RESEAL under the same label (which is what an approved curated edge
        does), and a policy ruling that changes every verdict without touching a cell.
        """
        current = self.store.origin(self.label, policy_version=self.policy_version)
        return {
            "loaded": {"build": self.space.origin.build,
                       "policy_version": self.space.origin.policy_version,
                       "seals": [[n, f[:12]] for n, f in self.space.origin.seals]},
            "stale": self.space.is_stale(current),
            "moved": list(self.space.staleness(current)),
        }

    def _api_bar(self, _query):
        """The declared bar, read live — the acceptance suite as the page sees it."""
        out = []
        for pair in self.config.bar:
            reading = self.space.read(pair.a, pair.b)
            verdict = "ABSTAIN" if reading is None else reading.verdict
            out.append({
                "a": pair.a, "b": pair.b, "expected": pair.verdict,
                "relational": None if reading is None else round(reading.relational_cosine, 4),
                "distributional": None if reading is None else round(reading.distributional_cosine, 4),
                "source": None if reading is None else reading.source,
                "verdict": verdict,
                "wrong": verdict != "ABSTAIN" and verdict != pair.verdict,
                "why": pair.why,
            })
        return {"pairs": out,
                "decided": sum(1 for p in out if p["verdict"] != "ABSTAIN"),
                "wrong": sum(1 for p in out if p["wrong"])}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="walk the dictionary and time every question")
    parser.add_argument("--db", default=constants.TK2_BODY_DB)
    parser.add_argument("--build", default=None, help="a build label (default: whichever is there)")
    parser.add_argument("--port", type=int, default=8770)
    args = parser.parse_args(argv)

    print(f"loading {args.db} …", flush=True)
    space, config, label, elapsed, source, store, version = load(args.db, args.build)
    stats = space.stats()
    print(f"  build {label} · {stats['dimensions']:,} dimensions · {stats['senses']:,} senses · "
          f"{stats['resident_bytes'] / 1e6:.0f} MB resident · {elapsed:.1f}s")
    print("  projecting …", flush=True)
    layout = projection(space)
    print(f"  PCA keeps {layout['kept']}% of the blend's variance")

    Bench.space, Bench.config, Bench.label = space, config, label
    Bench.load_seconds, Bench.policy_source, Bench.layout = elapsed, source, layout
    Bench.store, Bench.policy_version = store, version

    server = ThreadingHTTPServer(("127.0.0.1", args.port), Bench)
    print(f"\n  http://127.0.0.1:{args.port}   (ctrl-c to stop)\n", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("stopped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
