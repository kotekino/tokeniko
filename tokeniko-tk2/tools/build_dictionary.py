"""Build the base from the standing policy rows, and say what was built.

    PYTHONPATH=. ../.venv/bin/python tools/build_dictionary.py [--db NAME] [--json PATH]
    PYTHONPATH=. ../.venv/bin/python tools/build_dictionary.py --db tokeniko_tk2_body --apply \\
        --authorized "the Captain, 2026-08-26"

THE BUILD, and the one door it writes through. The base is `logic` — the body reads it and never
writes it — so a build reaches those rows the way a deploy does: validated by the model, executed by
raw pymongo, through `tk2.datatier.matrix_store`. There is no other path, and `--apply` is the
Captain's hand: without it this runs whole, prints everything, and stores nothing.

POLICY BEFORE RESULTS (tooling req. 4). Every number below is measured under rows read before the
first of them was computed, and the run prints where the rows came from and what they fingerprint
to. The manifest a build leaves behind records the config fingerprint AND the policy and bar
versions it was assembled from, so «two builds were measured under the same policy» is a claim a
reader can check rather than assume.

WHAT IS BUILT TODAY: the key space and R. D is T4's and lands beside it over the same key space —
`base_keys` is written first for exactly that reason, and the store refuses a second matrix whose
dimensions disagree with it.

THE BAR IS READ, NOT SCORED. R is half the geometry: `eat` and `food` have no WordNet relation at
all (finding 4 of the 2026-08-12 review), so a relations-only run is expected to leave the topical
nearnesses mute, and a pass/fail printed here would be a verdict on half a base. What IS printed is
threshold-free and already meaningful: the cosine, both directed cells, and the LOCAL ORDER — does
every NEAR pair out-score every FAR pair it shares a word with. The absolute floors the prototype
used (0.30 / 0.15) are deliberately not restated anywhere in this file: they are curation and they
are not rows yet, and T5 is the task that rules them.
"""

import argparse
import json
import sys
import time
from pathlib import Path

from tk2.datatier.policy_source import standing_bar, standing_policy
from tk2.dictionary import build, closure, glosses, keys, matrix, policy, relations
from tk2.dictionary.config import DictionaryConfig, bar_words
from tk2.dictionary.wordnet import (
    LEMMA_SCOPES,
    SCOPE_SYNSET,
    SCOPE_WORD,
    STANDING_LEMMA_SCOPE,
    WordNetProvider,
    wordnet_lexicon,
)

#: How many silent rows to print by name. A base key no relation reaches is a FINDING about the
#: resource, so the count is the number and these are the witnesses.
SILENT_SHOWN = 25


def build_base(config: DictionaryConfig, lemma_scope: str = STANDING_LEMMA_SCOPE) -> build.BaseBuild:
    """The base as the rows describe it, with the resource named out loud on the way through.

    The assembly itself is `tk2.dictionary.build`, so it is the same three steps a test can run on a
    handcrafted world; what belongs to a TOOL is naming the resource and saying how long it took.
    """
    started = time.time()
    lexicon = wordnet_lexicon()
    provider = WordNetProvider(lexicon, lemma_scope=lemma_scope)
    print(f"resource      WordNet through nltk — {len(lexicon):,} words after the name refusal")
    if lemma_scope != STANDING_LEMMA_SCOPE:
        print(f"lemma scope   {lemma_scope!r} — A VARIANT, not the standing reading. It may be "
              f"measured and it may not be stored.")

    def say(step: str) -> None:
        print(f"  {step:<12} ({time.time() - started:.0f}s)", flush=True)

    built = build.build_base(config, provider, say)
    print(f"  {built.graph_stats['nodes']:,} nodes · {built.graph_stats['edges']:,} edges · "
          f"{built.graph_stats['silent']:,} silent definitions")
    print(f"  closure: {len(built.words):,} words -> {len(built.dimensions):,} dimensions "
          f"(stopped: {built.closure.stopped}, {len(built.one_ring_past):,} one ring past the cut)")
    print(f"  R: {built.relational.stats()['nonzero']:,} cells in {time.time() - started:.0f}s")
    return built


# ------------------------------------------------------------------------------------------------
# the report
# ------------------------------------------------------------------------------------------------


def report_shape(built) -> dict:
    """What was built, in the terms a reader has to be able to ask it."""
    stats = built.stats()
    print()
    print("=" * 96)
    print("R — THE SHAPE OF WHAT WAS BUILT")
    print("=" * 96)
    print(f"  dimensions        {stats['dimensions']:,}")
    print(f"  off-diagonal      {stats['off_diagonal']:,} cells possible")
    print(f"  stated            {stats['nonzero']:,}  ({stats['density_pct']:.4f}%)")
    print(f"  negative          {stats['negative']:,}  (the antonym sign — only R carries it)")
    print(f"  silent rows       {stats['silent_rows']:,}  (a dimension no named relation reaches)")
    print()
    print(f"  {'relation':<16} {'cells':>9}   share of stated")
    for relation, count in stats["by_relation"].items():
        print(f"  {relation:<16} {count:>9,}   {100 * count / max(1, stats['nonzero']):5.1f}%")
    print()
    print(f"  by source         {stats['by_source']}")

    silent = [row.key for row in built.rows if row.is_silent]
    if silent:
        print()
        print(f"  the silent rows ({len(silent):,}), first {min(SILENT_SHOWN, len(silent))}:")
        print(f"    {' '.join(silent[:SILENT_SHOWN])}")
    return stats


def report_bar(built, bar) -> dict:
    """The bar on R alone — read, not scored. See the head of this file for why."""
    print()
    print("=" * 96)
    print("THE BAR ON R ALONE — R is half the geometry, so this is a reading and not a verdict")
    print("=" * 96)
    print(f"  {'pair':<26} {'exp':<5} {'cosine':>8}  {'a->b':>18}  {'b->a':>18}")
    print(f"  {'-' * 26} {'-' * 5} {'-' * 8}  {'-' * 18}  {'-' * 18}")

    measured = []
    for pair in bar:
        cosine = built.cosine(pair.a, pair.b)
        forward, reverse = relations.stated_between(built, pair.a, pair.b)
        measured.append(
            {
                "a": pair.a,
                "b": pair.b,
                "verdict": pair.verdict,
                "cosine": cosine,
                "forward": _cell_summary(forward),
                "reverse": _cell_summary(reverse),
            }
        )
        print(f"  {pair.a + ' ~ ' + pair.b:<26} {pair.verdict:<5} "
              f"{'—' if cosine is None else f'{cosine:+8.3f}':>8}  "
              f"{_cell_text(forward):>18}  {_cell_text(reverse):>18}")

    unscorable = [row for row in measured if row["cosine"] is None]
    mute = [row for row in measured if row["cosine"] == 0.0 and not row["forward"] and not row["reverse"]]
    stated_far = [
        row for row in measured
        if row["verdict"] == "FAR" and _positive(row["forward"], row["reverse"])
    ]
    order = _local_order(measured)

    print()
    print(f"  unscorable (a key is not a dimension)   {len(unscorable)}"
          f"{'  ' + ' '.join(r['a'] + '~' + r['b'] for r in unscorable) if unscorable else ''}")
    print(f"  MUTE (R states nothing, cosine 0)       {len(mute)} of {len(measured)}"
          f"   — an abstention, not a miss")
    print(f"  FAR pairs R states a POSITIVE cell for  {len(stated_far)}"
          f"{'  ' + ' '.join(r['a'] + '~' + r['b'] for r in stated_far) if stated_far else ''}")
    print(f"  LOCAL ORDER (threshold-free): every NEAR pair out-scores every FAR pair it shares a")
    print(f"     word with — {order['held']} of {order['tested']} comparisons hold")
    for broken in order["broken"]:
        print(f"       ! {broken}")
    return {
        "pairs": measured,
        "unscorable": len(unscorable),
        "mute": len(mute),
        "far_with_positive_cell": [f"{r['a']}~{r['b']}" for r in stated_far],
        "local_order": order,
    }


def _cell_summary(cell) -> dict | None:
    if cell is None:
        return None
    return {"relation": cell.relation, "weight": cell.weight, "source": cell.source}


def _cell_text(cell) -> str:
    if cell is None:
        return "MUTE"
    return f"{cell.weight:+.2f} {cell.relation}"


def _positive(forward, reverse) -> bool:
    return any(cell and cell["weight"] > 0 for cell in (forward, reverse))


def _local_order(measured) -> dict:
    """Absolute thresholds drift between runs; the ORDER should not. A NEAR pair sharing a word with
    a FAR pair is the comparison that means something — `want~need` against `want~refuse`."""
    held = tested = 0
    broken = []
    for near in (row for row in measured if row["verdict"] == "NEAR" and row["cosine"] is not None):
        for far in (row for row in measured if row["verdict"] == "FAR" and row["cosine"] is not None):
            if not {near["a"], near["b"]} & {far["a"], far["b"]}:
                continue
            tested += 1
            if near["cosine"] > far["cosine"]:
                held += 1
            else:
                broken.append(
                    f"{near['a']}~{near['b']} (NEAR, {near['cosine']:+.3f}) does not out-score "
                    f"{far['a']}~{far['b']} (FAR, {far['cosine']:+.3f})"
                )
    return {"tested": tested, "held": held, "broken": broken}


# ------------------------------------------------------------------------------------------------
# the A/B — one base, two readings of whose lemma may speak
# ------------------------------------------------------------------------------------------------


def compare_lemma_scope(config: DictionaryConfig) -> dict:
    """Build R twice over ONE key space, changing only which lemmas of a synset speak.

    The Captain ordered this measured before he rules (2026-08-26). The membership half is
    identical by construction — the closure reads GLOSSES, which the scope cannot touch — and that
    is asserted rather than asserted-to: a comparison whose two sides had different dimensions would
    be measuring the base and calling it the relation.
    """
    started = time.time()
    lexicon = wordnet_lexicon()
    providers = {
        SCOPE_SYNSET: WordNetProvider(lexicon, lemma_scope=SCOPE_SYNSET),
        SCOPE_WORD: WordNetProvider(lexicon, lemma_scope=SCOPE_WORD),
    }

    print(f"resource      WordNet through nltk — {len(lexicon):,} words")
    print("building the definition digraph and the closure ONCE…", flush=True)
    graph = closure.build_digraph(providers[SCOPE_SYNSET], config.closure)
    result = closure.seed_closure(graph, config.seeds, config.closure)
    dimensions = tuple(glosses.dimensions_of(result.words, providers[SCOPE_SYNSET]))
    under_b = tuple(glosses.dimensions_of(result.words, providers[SCOPE_WORD]))
    assert dimensions == under_b, "the lemma scope must not move membership"
    print(f"  {len(result.words):,} words -> {len(dimensions):,} dimensions, identical under both "
          f"readings ({time.time() - started:.0f}s)")

    built = {}
    for scope, provider in providers.items():
        built[scope] = relations.build(dimensions, provider, config.relations)
        print(f"  {scope:<7} R: {built[scope].stats()['nonzero']:,} cells "
              f"({time.time() - started:.0f}s)", flush=True)
    return built


def report_compare(built: dict, config: DictionaryConfig, providers=None) -> dict:
    a, b = built[SCOPE_SYNSET], built[SCOPE_WORD]
    stats = {SCOPE_SYNSET: a.stats(), SCOPE_WORD: b.stats()}

    print()
    print("=" * 96)
    print("A / B — WHOSE LEMMA MAY SPEAK.  A = every lemma of the synset (standing) · B = own lemma")
    print("=" * 96)
    print(f"  {'':<18} {'A (synset)':>14} {'B (word)':>14} {'delta':>12}")
    for label, key in (("stated cells", "nonzero"), ("negative", "negative"), ("silent rows", "silent_rows")):
        left, right = stats[SCOPE_SYNSET][key], stats[SCOPE_WORD][key]
        print(f"  {label:<18} {left:>14,} {right:>14,} {right - left:>+12,}")
    print(f"  {'density %':<18} {stats[SCOPE_SYNSET]['density_pct']:>14.4f} "
          f"{stats[SCOPE_WORD]['density_pct']:>14.4f}")

    print()
    print(f"  {'relation':<16} {'A':>10} {'B':>10} {'delta':>10}")
    names = sorted(set(stats[SCOPE_SYNSET]["by_relation"]) | set(stats[SCOPE_WORD]["by_relation"]))
    for name in names:
        left = stats[SCOPE_SYNSET]["by_relation"].get(name, 0)
        right = stats[SCOPE_WORD]["by_relation"].get(name, 0)
        mark = "  <-" if left != right else ""
        print(f"  {name:<16} {left:>10,} {right:>10,} {right - left:>+10,}{mark}")

    print()
    print(f"  silent rows by POS   {'A':>12} {'B':>12}   of")
    silent = {}
    for scope, built_matrix in ((SCOPE_SYNSET, a), (SCOPE_WORD, b)):
        counts = {}
        for row in built_matrix.rows:
            if row.is_silent:
                pos = keys.pos_of(row.key)
                counts[pos] = counts.get(pos, 0) + 1
        silent[scope] = counts
    total_by_pos = {}
    for key in a.keys:
        pos = keys.pos_of(key)
        total_by_pos[pos] = total_by_pos.get(pos, 0) + 1
    for pos in ("n", "v", "a", "r"):
        print(f"  {pos:<20} {silent[SCOPE_SYNSET].get(pos, 0):>12,} "
              f"{silent[SCOPE_WORD].get(pos, 0):>12,}   {total_by_pos.get(pos, 0):,}")

    moved = matrix.diff(a, b)
    print()
    print(f"  cells A states and B does not   {len(moved['removed']):,}")
    print(f"  cells B states and A does not   {len(moved['added']):,}")
    print(f"  cells both state, differently   {len(moved['changed']):,}")

    print()
    print("=" * 96)
    print("THE BAR, A BESIDE B")
    print("=" * 96)
    print(f"  {'pair':<26} {'exp':<5} {'cos A':>8} {'cos B':>8}   {'cell A':>22} {'cell B':>22}")
    pairs = []
    for pair in config.bar:
        cos_a, cos_b = a.cosine(pair.a, pair.b), b.cosine(pair.a, pair.b)
        cell_a = relations.stated_between(a, pair.a, pair.b)
        cell_b = relations.stated_between(b, pair.a, pair.b)
        changed = "*" if (cos_a != cos_b or _cell_text(cell_a[0]) != _cell_text(cell_b[0])) else " "
        print(f" {changed}{pair.a + ' ~ ' + pair.b:<26} {pair.verdict:<5} "
              f"{cos_a:>+8.3f} {cos_b:>+8.3f}   "
              f"{_cell_text(cell_a[0]) + ' / ' + _cell_text(cell_a[1]):>22} "
              f"{_cell_text(cell_b[0]) + ' / ' + _cell_text(cell_b[1]):>22}")
        pairs.append({"a": pair.a, "b": pair.b, "verdict": pair.verdict,
                      "cosine_a": cos_a, "cosine_b": cos_b,
                      "cell_a": _cell_text(cell_a[0]), "cell_b": _cell_text(cell_b[0])})

    reading = {}
    for scope, built_matrix in ((SCOPE_SYNSET, a), (SCOPE_WORD, b)):
        measured = [
            {"a": p.a, "b": p.b, "verdict": p.verdict,
             "cosine": built_matrix.cosine(p.a, p.b),
             "forward": _cell_summary(relations.stated_between(built_matrix, p.a, p.b)[0]),
             "reverse": _cell_summary(relations.stated_between(built_matrix, p.a, p.b)[1])}
            for p in config.bar
        ]
        order = _local_order(measured)
        mute = [m for m in measured if not m["forward"] and not m["reverse"]]
        far_positive = [m for m in measured
                        if m["verdict"] == "FAR" and _positive(m["forward"], m["reverse"])]
        reading[scope] = {"local_order": order, "mute": len(mute),
                          "far_with_positive_cell": [f"{m['a']}~{m['b']}" for m in far_positive]}
        print()
        print(f"  {scope:<8} MUTE {len(mute)}/{len(measured)} · local order "
              f"{order['held']}/{order['tested']} · FAR pairs with a positive cell: "
              f"{' '.join(reading[scope]['far_with_positive_cell']) or '(none)'}")
        for broken in order["broken"]:
            print(f"      ! {broken}")

    witnesses = _witnesses(moved["removed"], a, providers)
    return {"stats": stats, "silent_by_pos": silent, "bar": pairs, "reading": reading,
            "diff": {k: len(v) for k, v in moved.items()}, "witnesses": witnesses}


def _witnesses(removed, built, providers, limit: int = 14) -> list[dict]:
    """The borrowed edges that DIE under B, each naming the lemma that lent it.

    Named rather than counted, because «what was the borrowing actually doing» is the question the
    ruling turns on, and a number cannot answer it.
    """
    if providers is None:
        return []
    provider = providers[SCOPE_SYNSET]
    speakers = {}
    for key in built.keys:
        for sense in provider.senses_of_key(key):
            speakers.setdefault(sense, []).append(key)

    print()
    print("=" * 96)
    print("WHAT THE BORROWING WAS DOING — cells A states, B does not, and the lemma that lent them")
    print("=" * 96)
    out = []
    shown = 0
    for row_key, cell in removed:
        if cell.relation not in ("antonym", "derivational"):
            continue
        word = keys.word_of(row_key)
        lenders = provider.lemma_sources(row_key, cell.relation)
        for sense in provider.senses_of_key(cell.column):
            names = [name for name in lenders.get(sense, ()) if name.lower() != word]
            if not names:
                continue
            out.append({"row": row_key, "column": cell.column, "relation": cell.relation,
                        "weight": cell.weight, "lent_by": names})
            if shown < limit:
                print(f"  {row_key:>16} -> {cell.column:<16} {cell.relation:<14} "
                      f"{cell.weight:+.2f}   lent by {'/'.join(names)}")
                shown += 1
            break
    print(f"  … {len(out):,} such cells in all ({shown} shown)")
    return out[:200]


# ------------------------------------------------------------------------------------------------


def run(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="build the dictionary's base from the policy rows")
    parser.add_argument(
        "--db",
        default=None,
        help="read the standing policy from this database's rows, and write to it with --apply "
             "(default: read the migration files, which needs no body)",
    )
    parser.add_argument(
        "--build",
        default=None,
        help="the build label the rows are stored under (default: the config fingerprint's head, "
             "which is reproducible and cannot name two different policies)",
    )
    parser.add_argument("--json", default=None, help="also write the whole measurement here")
    parser.add_argument(
        "--lemma-scope",
        choices=LEMMA_SCOPES,
        default=STANDING_LEMMA_SCOPE,
        help="whose lemma may state antonymy and derivation: `synset` (every lemma of the synset — "
             "the standing reading) or `word` (only this dimension's own). A variant may be "
             "measured and may not be stored",
    )
    parser.add_argument(
        "--compare-lemma-scope",
        action="store_true",
        help="build R twice over ONE key space and report the two readings side by side "
             "(the Captain's ordered measurement, 2026-08-26)",
    )
    parser.add_argument("--note", default="", help="what this build is, for the manifest")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="THE CAPTAIN'S HAND: write the base and its manifest row. Needs --db and --authorized",
    )
    parser.add_argument(
        "--authorized",
        default="",
        help="who ordered this build and when — recorded in the manifest, which would otherwise be "
             "a log rather than a ledger",
    )
    args = parser.parse_args(argv)

    started = time.time()
    rows, policy_source = standing_policy(args.db)
    bar, bar_rows, bar_source = standing_bar(args.db)
    config = policy.config_from_rows(rows, bar_rows)

    print("=" * 96)
    print("BUILD THE BASE — declared before measuring")
    print("=" * 96)
    print(f"policy        {policy_source}")
    print(f"              {config.closure}")
    print(f"bar           {bar_source}, {len(bar)} pairs ({len(bar_words(bar))} words)")
    if config.relations is None:
        print()
        print("REFUSED: the standing policy declares no relation weights, so there is no R to "
              "build. Policy v3 (db/0006) is what declares them.")
        return 2
    print(f"relations     {len(config.relations.relations)} weighted "
          f"({', '.join(config.relations.relations[:6])}…)")
    print(f"curated       {len(config.relations.curated)} definitional relations · reciprocal "
          f"{config.relations.reciprocal_weight}")
    print(f"alphabet      {'/'.join(config.alphabet.order) if config.alphabet else '(not declared)'}")
    print()
    print(f"config fingerprint   {config.fingerprint()}")
    print(f"policy fingerprint   {policy.policy_fingerprint(rows)}")
    print(f"bar fingerprint      {policy.bar_fingerprint(bar_rows)}")
    print()

    if args.compare_lemma_scope:
        if args.apply:
            print("REFUSED: --compare-lemma-scope is a MEASUREMENT of two readings. Neither of them "
                  "is a build, and one of them is not the standing law.")
            return 2
        providers = None
        comparison = compare_lemma_scope(config)
        from tk2.dictionary.wordnet import WordNetProvider as _P
        providers = {SCOPE_SYNSET: _P(wordnet_lexicon(), lemma_scope=SCOPE_SYNSET)}
        measured = report_compare(comparison, config, providers)
        print()
        print(f"measured in {time.time() - started:.0f}s")
        if args.json:
            Path(args.json).write_text(
                json.dumps({"policy_source": policy_source, "comparison": measured},
                           indent=2, ensure_ascii=False, default=str) + "\n",
                encoding="utf-8",
            )
            print(f"wrote {args.json}")
        return 0

    if args.lemma_scope != STANDING_LEMMA_SCOPE and args.apply:
        print(f"REFUSED: --lemma-scope {args.lemma_scope!r} is a variant of the mining law, and a "
              f"stored base must be the one the config fingerprint describes "
              f"(`config.RELATION_RULES`). Measure it; do not store it.")
        return 2

    built = build_base(config, args.lemma_scope)
    stats = report_shape(built.relational)
    bar_reading = report_bar(built.relational, config.bar)
    counts = built.counts()

    build_label = args.build or config.fingerprint()[:12]
    manifest = policy.manifest_row(
        config,
        rows,
        bar_rows,
        counts=counts,
        authorization=args.authorized or "(unauthorized — dry run)",
        note=args.note,
    )

    print()
    print(f"measured in {time.time() - started:.0f}s · build label {build_label}")

    if args.json:
        Path(args.json).write_text(
            json.dumps(
                {
                    "policy_source": policy_source,
                    "bar_source": bar_source,
                    "build": build_label,
                    "counts": counts,
                    "r": stats,
                    "bar": bar_reading,
                    "manifest": {k: v for k, v in manifest.items() if k != "policy"},
                },
                indent=2,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"wrote {args.json}")

    if not args.apply:
        print()
        print("(dry run — nothing was written. `--apply --db … --authorized …` is the Captain's hand)")
        return 0

    return _apply(args, built.relational, manifest, build_label)


def _apply(args, built, manifest, build_label: str) -> int:
    """The write. Everything above this line is a measurement; this is the only part that lands."""
    if not args.db:
        print("REFUSED: --apply must name the database it writes (--db). The guard refuses "
              "everything not whitelisted, and a build with no name is a build nobody authorized.")
        return 2
    if not args.authorized.strip():
        print("REFUSED: --apply must record who authorized it (--authorized). A manifest that "
              "cannot name the hand that ordered a build is a log, not a ledger.")
        return 2

    from tk2.core.models import DictionaryBuildDoc
    from tk2.datatier import MigrationWriter, database
    from tk2.datatier.matrix_store import MongoMatrixStore

    db = database(args.db)
    store = MongoMatrixStore(db)
    written = store.write(built, build_label)
    MigrationWriter(db).insert(DictionaryBuildDoc, manifest)
    print()
    print(f"written: {args.db}.{built.name} build='{build_label}' — {written:,} rows, "
          f"and one manifest row in {DictionaryBuildDoc.Settings.name}")
    return 0


def main(argv: list[str] | None = None) -> int:
    try:
        return run(argv)
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        return 130


def _say(on: bool, message: str) -> None:
    if on:
        print(message, flush=True)


if __name__ == "__main__":
    raise SystemExit(main())
