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
from dataclasses import replace
from pathlib import Path

from tk2.datatier.policy_source import standing_bar, standing_policy
from tk2.dictionary import build, closure, glosses, keys, matrix, policy, relations
from tk2.dictionary.config import DictionaryConfig, bar_words
from tk2.dictionary.wordnet import (
    LEMMA_SCOPES,
    SCOPE_SYNSET,
    SCOPE_WORD,
    WordNetProvider,
    wordnet_lexicon,
)

#: How many silent rows to print by name. A base key no relation reaches is a FINDING about the
#: resource, so the count is the number and these are the witnesses.
SILENT_SHOWN = 25


def build_base(config: DictionaryConfig, lemma_scope: str,
               antonym_symmetry: str | None = None) -> build.BaseBuild:
    """The base as the rows describe it, with the resource named out loud on the way through.

    The assembly itself is `tk2.dictionary.build`, so it is the same three steps a test can run on a
    handcrafted world; what belongs to a TOOL is naming the resource and saying how long it took.
    """
    started = time.time()
    lexicon = wordnet_lexicon()
    provider = WordNetProvider(lexicon, lemma_scope=lemma_scope)
    print(f"resource      WordNet through nltk — {len(lexicon):,} words after the name refusal")
    if antonym_symmetry is not None:
        print(f"antonym       {antonym_symmetry.upper()}  — a measurement of a reading nobody has ruled; see "
              f"`relations.ANTONYM_SYMMETRIES`")

    def say(step: str) -> None:
        print(f"  {step:<12} ({time.time() - started:.0f}s)", flush=True)

    built = build.build_base(config, provider, say, antonym_symmetry=antonym_symmetry)
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


def compare_antonym_symmetry(config: DictionaryConfig, scope: str) -> dict:
    """Build R three times over ONE key space under the SAME lemma scope — the QM's ordered
    measurements of 2026-08-26, the second of them ordered after the first went wrong.

    `stated` is what the resource said. `overwrite` states the reverse wherever an antonymy exists
    and destroyed four stated relations doing it. `add_only` completes a pair ONLY where R was
    silent, and says so in the cell's own relation name.
    """
    started = time.time()
    lexicon = wordnet_lexicon()
    provider = WordNetProvider(lexicon, lemma_scope=scope)

    print(f"resource      WordNet through nltk — {len(lexicon):,} words · lemma scope {scope!r}")
    print("building the definition digraph and the closure ONCE…", flush=True)
    graph = closure.build_digraph(provider, config.closure)
    result = closure.seed_closure(graph, config.seeds, config.closure)
    dimensions = tuple(glosses.dimensions_of(result.words, provider))
    print(f"  {len(result.words):,} words -> {len(dimensions):,} dimensions "
          f"({time.time() - started:.0f}s)")

    built = {}
    for mode in relations.ANTONYM_SYMMETRIES:
        built[mode] = relations.build(
            dimensions, provider, relations.policy_for(config.relations, mode), antonym_symmetry=mode
        )
        print(f"  {mode:<10} R: {built[mode].stats()['nonzero']:,} cells "
              f"({time.time() - started:.0f}s)", flush=True)
    return built


#: The cells the OVERWRITING reading destroyed (measured 2026-08-26). Named, because «add-only does
#: not do this» is a claim about these four and not about a count.
OVERWRITTEN_BY_SYMMETRY = (
    ("dark.n", "day.n", "holonym"),
    ("engage.v", "fire.v", "hypernym_2"),
    ("get.v", "leave.v", "troponym"),
    ("go.v", "stop.v", "hypernym_1"),
)


def report_symmetry(built: dict, config: DictionaryConfig) -> dict:
    """The three readings side by side, and the four cells the middle one broke."""
    stated = built[relations.SYMMETRY_OFF]
    modes = list(relations.ANTONYM_SYMMETRIES)
    stats = {mode: built[mode].stats() for mode in modes}

    print()
    print("=" * 96)
    print("ANTONYM SYMMETRY — three readings.  stated = WordNet's own · overwrite = both, always · "
          "add_only = both where R was silent")
    print("=" * 96)
    print(f"  {'':<20}" + "".join(f"{mode:>16}" for mode in modes))
    for label, key in (("stated cells", "nonzero"), ("negative", "negative"),
                       ("silent rows", "silent_rows")):
        print(f"  {label:<20}" + "".join(f"{stats[mode][key]:>16,}" for mode in modes))
    print(f"  {'density %':<20}" + "".join(f"{stats[mode]['density_pct']:>16.4f}" for mode in modes))

    print()
    print(f"  {'relation':<20}" + "".join(f"{mode:>16}" for mode in modes))
    names = sorted(set().union(*(stats[mode]["by_relation"] for mode in modes)))
    for name in names:
        counts = [stats[mode]["by_relation"].get(name, 0) for mode in modes]
        mark = "  <-" if len(set(counts)) > 1 else ""
        print(f"  {name:<20}" + "".join(f"{count:>16,}" for count in counts) + mark)

    print()
    print(f"  {'silent rows by POS':<20}" + "".join(f"{mode:>16}" for mode in modes))
    for pos in ("n", "v", "a", "r"):
        counts = []
        for mode in modes:
            counts.append(sum(1 for row in built[mode].rows
                              if row.is_silent and keys.pos_of(row.key) == pos))
        print(f"  {pos:<20}" + "".join(f"{count:>16,}" for count in counts))

    diffs = {mode: matrix.diff(stated, built[mode]) for mode in modes[1:]}
    print()
    print(f"  {'vs stated':<20}{'added':>16}{'removed':>16}{'OVERWRITTEN':>16}")
    for mode in modes[1:]:
        print(f"  {mode:<20}{len(diffs[mode]['added']):>16,}{len(diffs[mode]['removed']):>16,}"
              f"{len(diffs[mode]['changed']):>16,}")

    print()
    print("=" * 96)
    print("THE FOUR CELLS THE OVERWRITING READING DESTROYED")
    print("=" * 96)
    kept = True
    for row, column, relation in OVERWRITTEN_BY_SYMMETRY:
        cells = {mode: built[mode].cell(row, column) for mode in modes}
        line = "  ".join(
            f"{mode}: {cells[mode].relation}{cells[mode].weight:+.2f}" if cells[mode] else f"{mode}: MUTE"
            for mode in modes
        )
        held = cells[relations.SYMMETRY_ADD_ONLY].relation == relation
        kept = kept and held
        print(f"  {row:>10} -> {column:<10} {'KEPT' if held else 'LOST':<5} {line}")
    print(f"  add_only keeps all four stated relations: {kept}")

    print()
    print("=" * 96)
    print("THE BAR — the three readings")
    print("=" * 96)
    print(f"  {'pair':<26} {'exp':<5}" + "".join(f"{'cos ' + mode:>14}" for mode in modes)
          + "   cell (stated -> add_only)")
    pairs = []
    for pair in config.bar:
        cosines = {mode: built[mode].cosine(pair.a, pair.b) for mode in modes}
        cells = {mode: relations.stated_between(built[mode], pair.a, pair.b) for mode in modes}
        text = {mode: _cell_text(cells[mode][0]) + " / " + _cell_text(cells[mode][1]) for mode in modes}
        moved = "*" if len({round(c, 9) for c in cosines.values()}) > 1 else " "
        print(f" {moved}{pair.a + ' ~ ' + pair.b:<26} {pair.verdict:<5}"
              + "".join(f"{cosines[mode]:>+14.3f}" for mode in modes)
              + f"   {text[relations.SYMMETRY_OFF]}  ->  {text[relations.SYMMETRY_ADD_ONLY]}")
        pairs.append({"a": pair.a, "b": pair.b, "verdict": pair.verdict,
                      "cosines": cosines, "cells": text})

    reading = {}
    for mode in modes:
        measured = [
            {"a": p.a, "b": p.b, "verdict": p.verdict,
             "cosine": built[mode].cosine(p.a, p.b),
             "forward": _cell_summary(relations.stated_between(built[mode], p.a, p.b)[0]),
             "reverse": _cell_summary(relations.stated_between(built[mode], p.a, p.b)[1])}
            for p in config.bar
        ]
        order = _local_order(measured)
        mute = [m for m in measured if not m["forward"] and not m["reverse"]]
        one_sided = [m for m in measured if bool(m["forward"]) != bool(m["reverse"])]
        reading[mode] = {"local_order": order, "mute": len(mute),
                         "one_sided": [f"{m['a']}~{m['b']}" for m in one_sided]}
        print()
        print(f"  {mode:<10} MUTE {len(mute)}/{len(measured)} · local order "
              f"{order['held']}/{order['tested']} · stated ONE WAY ONLY: "
              f"{' '.join(reading[mode]['one_sided']) or '(none)'}")

    added = diffs[relations.SYMMETRY_ADD_ONLY]["added"]
    print()
    print("=" * 96)
    print("WHAT ADD-ONLY ADDS")
    print("=" * 96)
    print(f"  cells added                {len(added):,}")
    print(f"  all of them {relations.ANTONYM_INFERRED!r}: "
          f"{all(cell.relation == relations.ANTONYM_INFERRED for _row, cell in added)}")
    print(f"  cells overwritten          {len(diffs[relations.SYMMETRY_ADD_ONLY]['changed'])}")
    print(f"  negatives                  {stats[relations.SYMMETRY_OFF]['negative']:,} -> "
          f"{stats[relations.SYMMETRY_ADD_ONLY]['negative']:,}")
    print(f"  silent rows                {stats[relations.SYMMETRY_OFF]['silent_rows']:,} -> "
          f"{stats[relations.SYMMETRY_ADD_ONLY]['silent_rows']:,}")
    print()
    print("  the first 10 pairs it completes:")
    for row, cell in added[:10]:
        print(f"    {row:>18} -> {cell.column:<18} {cell.weight:+.2f} {cell.relation}")

    return {"stats": stats, "bar": pairs, "reading": reading,
            "added": len(added), "overwritten": {m: len(d["changed"]) for m, d in diffs.items()},
            "four_cells_kept": kept}


def report_two(left, right, labels, config: DictionaryConfig, title: str) -> dict:
    """Two matrices over ONE key space, printed side by side — the shape every ordered measurement
    has taken so far (the lemma scope, and now antonym symmetry) and the one T4's down-weight will.

    The two columns are LABELLED rather than named A and B in the code, because which reading is
    which is the Captain's business and this only counts.
    """
    left_label, right_label = labels
    stats = {left_label: left.stats(), right_label: right.stats()}

    print()
    print("=" * 96)
    print(title)
    print("=" * 96)
    print(f"  {'':<18} {left_label:>16} {right_label:>16} {'delta':>12}")
    for label, key in (("stated cells", "nonzero"), ("negative", "negative"), ("silent rows", "silent_rows")):
        a_value, b_value = stats[left_label][key], stats[right_label][key]
        print(f"  {label:<18} {a_value:>16,} {b_value:>16,} {b_value - a_value:>+12,}")
    print(f"  {'density %':<18} {stats[left_label]['density_pct']:>16.4f} "
          f"{stats[right_label]['density_pct']:>16.4f}")

    print()
    print(f"  {'relation':<16} {left_label:>16} {right_label:>16} {'delta':>10}")
    for name in sorted(set(stats[left_label]["by_relation"]) | set(stats[right_label]["by_relation"])):
        a_value = stats[left_label]["by_relation"].get(name, 0)
        b_value = stats[right_label]["by_relation"].get(name, 0)
        mark = "  <-" if a_value != b_value else ""
        print(f"  {name:<16} {a_value:>16,} {b_value:>16,} {b_value - a_value:>+10,}{mark}")

    silent = {}
    for label, built_matrix in ((left_label, left), (right_label, right)):
        counts = {}
        for row in built_matrix.rows:
            if row.is_silent:
                pos = keys.pos_of(row.key)
                counts[pos] = counts.get(pos, 0) + 1
        silent[label] = counts
    total_by_pos = {}
    for key in left.keys:
        pos = keys.pos_of(key)
        total_by_pos[pos] = total_by_pos.get(pos, 0) + 1
    print()
    print(f"  silent rows by POS {left_label:>16} {right_label:>16}   of")
    for pos in ("n", "v", "a", "r"):
        print(f"  {pos:<18} {silent[left_label].get(pos, 0):>16,} "
              f"{silent[right_label].get(pos, 0):>16,}   {total_by_pos.get(pos, 0):,}")

    moved = matrix.diff(left, right)
    print()
    print(f"  cells {left_label} states and {right_label} does not   {len(moved['removed']):,}")
    print(f"  cells {right_label} states and {left_label} does not   {len(moved['added']):,}")
    print(f"  cells both state, differently             {len(moved['changed']):,}")

    print()
    print("=" * 96)
    print(f"THE BAR — {left_label} beside {right_label}")
    print("=" * 96)
    print(f"  {'pair':<26} {'exp':<5} {'cos ' + left_label:>14} {'cos ' + right_label:>14}   "
          f"{'cell ' + left_label:>26} {'cell ' + right_label:>26}")
    pairs = []
    for pair in config.bar:
        cos_a, cos_b = left.cosine(pair.a, pair.b), right.cosine(pair.a, pair.b)
        cell_a = relations.stated_between(left, pair.a, pair.b)
        cell_b = relations.stated_between(right, pair.a, pair.b)
        text_a = _cell_text(cell_a[0]) + " / " + _cell_text(cell_a[1])
        text_b = _cell_text(cell_b[0]) + " / " + _cell_text(cell_b[1])
        changed = "*" if (abs(cos_a - cos_b) > 1e-9 or text_a != text_b) else " "
        print(f" {changed}{pair.a + ' ~ ' + pair.b:<26} {pair.verdict:<5} "
              f"{cos_a:>+14.3f} {cos_b:>+14.3f}   {text_a:>26} {text_b:>26}")
        pairs.append({"a": pair.a, "b": pair.b, "verdict": pair.verdict,
                      "cosine_left": cos_a, "cosine_right": cos_b,
                      "cell_left": text_a, "cell_right": text_b})

    reading = {}
    for label, built_matrix in ((left_label, left), (right_label, right)):
        measured = [
            {"a": p.a, "b": p.b, "verdict": p.verdict,
             "cosine": built_matrix.cosine(p.a, p.b),
             "forward": _cell_summary(relations.stated_between(built_matrix, p.a, p.b)[0]),
             "reverse": _cell_summary(relations.stated_between(built_matrix, p.a, p.b)[1])}
            for p in config.bar
        ]
        order = _local_order(measured)
        mute = [m for m in measured if not m["forward"] and not m["reverse"]]
        one_sided = [m for m in measured if bool(m["forward"]) != bool(m["reverse"])]
        far_positive = [m for m in measured
                        if m["verdict"] == "FAR" and _positive(m["forward"], m["reverse"])]
        reading[label] = {"local_order": order, "mute": len(mute),
                          "one_sided": [f"{m['a']}~{m['b']}" for m in one_sided],
                          "far_with_positive_cell": [f"{m['a']}~{m['b']}" for m in far_positive]}
        print()
        print(f"  {label:<10} MUTE {len(mute)}/{len(measured)} · local order "
              f"{order['held']}/{order['tested']} · stated ONE WAY ONLY: "
              f"{' '.join(reading[label]['one_sided']) or '(none)'}")
        print(f"  {'':<10} FAR pairs with a positive cell: "
              f"{' '.join(reading[label]['far_with_positive_cell']) or '(none)'}")
        for broken in order["broken"]:
            print(f"      ! {broken}")

    return {"stats": stats, "silent_by_pos": silent, "bar": pairs, "reading": reading,
            "diff": {k: len(v) for k, v in moved.items()}, "moved": moved}


def report_compare(built: dict, config: DictionaryConfig, providers=None) -> dict:
    a, b = built[SCOPE_SYNSET], built[SCOPE_WORD]
    measured = report_two(
        a, b, (SCOPE_SYNSET, SCOPE_WORD), config,
        "A / B — WHOSE LEMMA MAY SPEAK.  synset = every lemma of the synset · word = its own only",
    )
    witnesses = _witnesses(measured.pop("moved")["removed"], a, providers)
    return {**measured, "witnesses": witnesses}


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
        default=None,
        help="reproduce a reading other than the one the rows declare: `synset` (every lemma of the "
             "synset — what the base was built under before 2026-08-26) or `word` (its own only, "
             "ruled standing). Default: whatever policy v4 says. A reading the rows did not declare "
             "may be measured and may not be stored",
    )
    parser.add_argument(
        "--antonym-symmetry",
        choices=relations.ANTONYM_SYMMETRIES,
        default=None,
        help="how a one-sided antonymy is read: `stated` (what the resource said — the standing "
             "reading), `overwrite` (state the reverse always) or `add_only` (complete a pair only "
             "where R is silent, as its own relation `antonym_inferred`). The last two are "
             "measurements nobody has ruled: measurable, never storable",
    )
    parser.add_argument(
        "--compare-antonym-symmetry",
        action="store_true",
        help="build R twice under the SAME lemma scope, symmetrizing antonymy in the second, and "
             "report the two side by side (the QM's ordered measurement, 2026-08-26)",
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
    print(f"lemma scope   {config.relations.lemma_scope or '(not declared by these rows)'}")
    print(f"antonymy      {config.relations.antonym_symmetry or '(not declared by these rows)'}")
    print()
    print(f"config fingerprint   {config.fingerprint()}")
    print(f"policy fingerprint   {policy.policy_fingerprint(rows)}")
    print(f"bar fingerprint      {policy.bar_fingerprint(bar_rows)}")
    print()

    if args.compare_antonym_symmetry:
        if args.apply:
            print("REFUSED: --compare-antonym-symmetry is a MEASUREMENT of three readings, and two "
                  "of them are not the standing law.")
            return 2
        scope = args.lemma_scope or config.relations.lemma_scope
        if scope is None:
            print("REFUSED: no lemma scope declared and none named — see --lemma-scope.")
            return 2
        measured = report_symmetry(compare_antonym_symmetry(config, scope), config)
        print()
        print(f"measured in {time.time() - started:.0f}s")
        if args.json:
            Path(args.json).write_text(
                json.dumps({"policy_source": policy_source, "lemma_scope": scope,
                            "symmetry": measured}, indent=2, ensure_ascii=False, default=str) + "\n",
                encoding="utf-8",
            )
            print(f"wrote {args.json}")
        return 0

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

    # THE SCOPE COMES FROM THE ROWS (policy v4). `--lemma-scope` is how the OTHER reading is
    # reproduced, and a reading the rows did not declare is a measurement that may not be stored.
    declared_scope = config.relations.lemma_scope
    scope = args.lemma_scope or declared_scope
    if scope is None:
        print("REFUSED: this policy version declares no `lemma_scope`, so nothing says whose lemma "
              "may state antonymy and derivation. Policy v4 (db/0007) declares it; to reproduce an "
              "older reading, name it with --lemma-scope (and it cannot be stored).")
        return 2
    if args.apply and scope != declared_scope:
        print(f"REFUSED: --lemma-scope {scope!r} is not what the rows declare ({declared_scope!r}). "
              f"A stored base must be the one its config fingerprint describes.")
        return 2
    if args.apply and args.antonym_symmetry not in (None, config.relations.antonym_symmetry):
        print(f"REFUSED: --antonym-symmetry {args.antonym_symmetry!r} is not what the rows declare "
              f"({config.relations.antonym_symmetry!r}). A stored base must be the one its config "
              f"fingerprint describes; a reading the rows do not declare is a measurement.")
        return 2

    if args.antonym_symmetry is not None:
        config = replace(config, relations=relations.policy_for(config.relations, args.antonym_symmetry))
    built = build_base(config, scope, args.antonym_symmetry)
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
