"""Build the base from the standing policy rows, and say what was built.

    PYTHONPATH=. ../.venv/bin/python tools/build_dictionary.py [--db NAME] [--json PATH]
    PYTHONPATH=. ../.venv/bin/python tools/build_dictionary.py --db tokeniko_tk2 --apply \\
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

WHAT IS BUILT: the key space, R, and — since T4 — D over the very same key space. `base_keys` is
written first for exactly that reason, and the store refuses a second matrix whose dimensions
disagree with it. A policy version that declares no gloss walk (v1-v5) builds no D and the run says
so; it does not invent one.

THE DUAL READ. R and D are two matrices on purpose and nothing here blends them into the stored
base. A READER may still want one number, and the dual read is the only shape in which that is
honest: the two rows are concatenated into one vector (R's columns, then D's, scaled by the mix) and
the cosine is taken over the whole of it, so no cell is ever averaged with another. THE MIX COMES
FROM THE ROWS since policy v7 (the Captain's ruling of 2026-09-09, 0.5); `--mix` is how another
blend is REPRODUCED, and a blend the rows did not declare is a measurement that may not be stored —
exactly the shape `--lemma-scope` and `--antonym-symmetry` took before their rulings.

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
from dataclasses import fields, replace
from pathlib import Path

from tk2.datatier.policy_source import (
    closed_forms,
    standing_bar,
    standing_curated_edges,
    standing_policy,
)
from tk2.dictionary import build, closure, distribution, glosses, keys, matrix, policy, relations, senses
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

#: The blends the dual read is printed at, BESIDE the one the rows declare. 0.0 IS R alone, so the
#: column is not a special case, and the top of the range is deliberately past anything plausible:
#: the point of the table is to show where R's sign stops surviving the blend, which needs the
#: failure IN it. The standing mix is folded in by `mix_columns`, so the table always contains the
#: reading the build was actually measured under — a sweep that could omit it would be a table
#: nobody could locate the policy in.
MIXES = (0.0, 0.25, 0.5, 1.0, 2.0)


def mix_columns(standing: float, mixes=MIXES) -> tuple[float, ...]:
    """The sweep with the declared reading in it, in order and never twice."""
    return tuple(sorted({*mixes, standing}))

#: How many of D's loudest gloss words to print. The words the base's definitions cannot avoid are
#: the whole of the Captain's parked question (b), so they are named and not counted.
VOCABULARY_SHOWN = 20

#: The words the pollution figure is measured against — the residual floor the name refusal left,
#: named in the plan («`in` 27% of base rows, `be` 14%, `by` 14%, `as` 10%»). A stated set rather
#: than a derived one because the figure is a COMPARISON with the 2026-08-25 measurement, and a
#: junk set that moved with the base would compare two different questions.
JUNK_WORDS = frozenset({"in", "be", "by", "as"})


class CuratedEdgesLost(SystemExit):
    """A build was asked to carry an approved edge it cannot place. LOUD, and it stops the run.

    Two edges the Captain approved in August were lost in E1b's rebuild and nothing noticed for a
    month. A rebuild changes MEMBERSHIP — the closure's cut moves — so an approved edge can name a
    key the new base does not have, and that is a decision about to be dropped. The build refuses
    rather than printing a warning nobody reads: this is precisely the silence E1d exists to end.
    """


def build_base(config: DictionaryConfig, lemma_scope: str,
               antonym_symmetry: str | None = None, closed=None, with_senses: bool = False,
               curated_edges=None):
    """The base as the rows describe it, with the resource named out loud on the way through.

    The assembly itself is `tk2.dictionary.build`, so it is the same steps a test can run on a
    handcrafted world; what belongs to a TOOL is naming the resource and saying how long it took.

    Returns the provider beside the build, because D's report is about the VOCABULARY its cells were
    computed from (which words the base's definitions cannot avoid) and that question is asked of
    the resource, not of the matrix.
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

    built = build.build_base(
        config, provider, say, antonym_symmetry=antonym_symmetry, closed_forms=closed,
        with_senses=with_senses, curated_edges=curated_edges,
    )
    print(f"  {built.graph_stats['nodes']:,} nodes · {built.graph_stats['edges']:,} edges · "
          f"{built.graph_stats['silent']:,} silent definitions")
    print(f"  closure: {len(built.words):,} words -> {len(built.dimensions):,} dimensions "
          f"(stopped: {built.closure.stopped}, {len(built.one_ring_past):,} one ring past the cut)")
    print(f"  R: {built.relational.stats()['nonzero']:,} cells in {time.time() - started:.0f}s")
    if built.curated is not None:
        merge = built.curated
        print(f"  curated: {merge.edges} edges -> {merge.cells} cells"
              + (f" · {merge.withdrawn} withdrawn" if merge.withdrawn else ""))
        for source, column, relation in merge.overrode_mined:
            # A DISCOVERY, not an error: the resource stated something and a person disagreed.
            print(f"    override  {source} -> {column}  was `{relation}` (mined)")
        if merge.unresolvable:
            for source, target, why in merge.unresolvable:
                print(f"    LOST      {source} -> {target}  {why}")
            raise CuratedEdgesLost(
                f"{len(merge.unresolvable)} approved edge(s) name dimensions this base does not "
                f"have. A rebuild moves the closure's cut, so an edge can outlive its dimension — "
                f"and dropping an approved decision quietly is the failure E1d was opened to end. "
                f"Withdraw them (`withdrawn_at`) or re-approve them against the new base."
            )
    if built.distributional is not None:
        print(f"  D: {built.distributional.stats()['nonzero']:,} cells in "
              f"{time.time() - started:.0f}s")
    return built, provider


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
# the bar, read under any geometry — R alone, D alone, or the two blended
# ------------------------------------------------------------------------------------------------


def read_bar(bar, cosine_of, cells_of=None) -> dict:
    """One bar, read under ONE geometry, threshold-free.

    Written once and called for every reading there is, because the alternative is three copies of
    the same arithmetic drifting apart — and the whole claim of the dual read is that R alone, D
    alone and the blend are the SAME question asked of different columns.

    Nothing here scores a pass. What it returns is what can be said without an absolute floor: the
    cosine, whether the geometry states anything at all (MUTE is an abstention, not a miss), the
    LOCAL order (does every NEAR pair out-score every FAR pair it shares a word with), the GLOBAL
    order (every NEAR against every FAR, which is harsher and word-blind), and the MARGIN — the gap
    between the worst NEAR and the best FAR. The floors are T5's and the Captain's.
    """
    measured = []
    for pair in bar:
        forward, reverse = cells_of(pair.a, pair.b) if cells_of else (None, None)
        measured.append(
            {
                "a": pair.a,
                "b": pair.b,
                "verdict": pair.verdict,
                "cosine": cosine_of(pair.a, pair.b),
                "forward": _cell_summary(forward),
                "reverse": _cell_summary(reverse),
            }
        )
    near = [m["cosine"] for m in measured if m["verdict"] == "NEAR" and m["cosine"] is not None]
    far = [m["cosine"] for m in measured if m["verdict"] == "FAR" and m["cosine"] is not None]
    held = sum(1 for n in near for f in far if n > f)
    return {
        "pairs": measured,
        "unscorable": [f"{m['a']}~{m['b']}" for m in measured if m["cosine"] is None],
        "mute": [f"{m['a']}~{m['b']}" for m in measured
                 if m["cosine"] is not None and not m["cosine"] and not m["forward"] and not m["reverse"]],
        "local_order": _local_order(measured),
        "global_order": {"tested": len(near) * len(far), "held": held},
        "margin": (min(near) - max(far)) if near and far else None,
        "worst_near": min(near) if near else None,
        "best_far": max(far) if far else None,
    }


def _reading_line(label: str, reading: dict) -> str:
    """One geometry's reading in one line — the shape every table below repeats."""
    order = reading["local_order"]
    globally = reading["global_order"]
    mute = len(reading["mute"])
    return (
        f"  {label:<22} MUTE {mute:>2}  local {order['held']:>2}/{order['tested']:<3} "
        f"global {globally['held']:>3}/{globally['tested']:<4} "
        f"margin {_number(reading['margin']):>8}  worst NEAR {_number(reading['worst_near']):>8}  "
        f"best FAR {_number(reading['best_far']):>8}"
    )


def _number(value, width: str = "+.3f") -> str:
    """A measured number, or the em dash that means «there was nothing to measure»."""
    return "—" if value is None else format(value, width)


# ------------------------------------------------------------------------------------------------
# D — the shape of the second geometry, and the vocabulary its cells are made of
# ------------------------------------------------------------------------------------------------


def report_distribution(built: build.BaseBuild, vectors, config: DictionaryConfig) -> dict:
    """What D is, and what it is made of.

    Two halves on purpose. The first is the matrix — how many cells, how dense, how many rows the
    gloss walk cannot place. The second is the VOCABULARY, and it is the half the Captain's parked
    question (b) is about: after the name refusal took Oregon's `or` off 57.8% of the base's rows,
    what is left is real function words, and the figure that matters is how much of D's evidence is
    nothing but them.
    """
    walk = config.distribution
    matrix_d = built.distributional
    stats = matrix_d.stats()
    frequency = distribution.document_frequency(vectors)
    sizes = sorted(len(words) for words in vectors.values())
    saturated = sum(
        1
        for row in matrix_d.rows
        for cell in row.cells
        if cell.source != matrix.SOURCE_AXIS and abs(cell.weight - walk.cap) < 1e-9
    )

    print()
    print("=" * 96)
    print("D — THE SHAPE OF WHAT WAS BUILT  (gloss overlap: unsigned, symmetric, no relation named)")
    print("=" * 96)
    print(f"  walk              {walk.measure} · {walk.weighting} · vocabulary {walk.vocabulary} · "
          f"senses {walk.senses}")
    print(f"                    min_shared {walk.min_shared} · scale {walk.scale} · cap {walk.cap} "
          f"· floor {walk.floor} · identity {walk.identity}")
    print(f"  dimensions        {stats['dimensions']:,}")
    print(f"  stated            {stats['nonzero']:,}  ({stats['density_pct']:.4f}% of "
          f"{stats['off_diagonal']:,} possible)")
    print(f"  AT THE CAP        {saturated:,}  ({100 * saturated / max(1, stats['nonzero']):.1f}% of "
          f"stated — a saturated cell has stopped saying how much)")
    print(f"  silent rows       {stats['silent_rows']:,}  (a dimension whose definition shares "
          f"nothing with any other)")
    print()
    print(f"  gloss vectors     {len(frequency):,} distinct words · "
          f"mean {sum(sizes) / max(1, len(sizes)):.1f} words per dimension · "
          f"median {sizes[len(sizes) // 2]} · max {sizes[-1]} · "
          f"{sum(1 for n in sizes if not n):,} empty")
    print()
    print(f"  the words the base's definitions cannot avoid (top {VOCABULARY_SHOWN} by rows named):")
    loudest = sorted(frequency.items(), key=lambda item: (-item[1], item[0]))[:VOCABULARY_SHOWN]
    for word, count in loudest:
        print(f"    {word:<16} {count:>6,}  {100 * count / len(built.dimensions):5.1f}% of rows")

    # AT BOTH FLOORS on purpose. The T2b figure the plan carries (84.8% before the name refusal,
    # 59.1% after) counted every pair that shared ANYTHING, so `min_shared = 1` is the column that
    # can be compared with it; the declared floor is the one this base actually runs at. Since the
    # ruling of 2026-09-09 the two are THE SAME floor, and the label says so rather than letting one
    # number wear the other's name.
    pollution = {
        floor: distribution.junk_pollution(
            vectors, JUNK_WORDS, floor, distribution.word_weights(vectors, walk)
        )
        for floor in dict.fromkeys((1, walk.min_shared))
    }
    print()
    print(f"  POLLUTION — pairs whose only shared words are {sorted(JUNK_WORDS)}")
    for floor, measured in pollution.items():
        names = (["the T2b comparison"] if floor == 1 else []) + (
            ["the declared floor"] if floor == walk.min_shared else [])
        note = "  (" + " and ".join(names) + ")"
        print(f"    >= {floor} shared:  {measured['overlapping_pairs']:>9,} pairs   ONLY junk "
              f"{measured['pairs_only_junk']:>8,} ({measured['pairs_only_junk_pct']:>5}%)   "
              f"junk's share of the shared mass {measured['mass_from_junk_pct']}%{note}")
    print("    the first figure is MEMBERSHIP — no weighting can move it, only a filter could; "
          "the second is what a weighting moves")

    return {
        "stats": stats,
        "saturated": saturated,
        "vocabulary": len(frequency),
        "loudest": [[word, count] for word, count in loudest],
        "sizes": {"mean": round(sum(sizes) / max(1, len(sizes)), 2), "max": sizes[-1],
                  "empty": sum(1 for n in sizes if not n)},
        "pollution": {str(floor): measured for floor, measured in pollution.items()},
    }


# ------------------------------------------------------------------------------------------------
# THE DUAL READ — R alone, D alone, and the blend, over one key space
# ------------------------------------------------------------------------------------------------


def report_reading(built: build.BaseBuild, config: DictionaryConfig) -> dict:
    """THE BAR AS THE ENGINE READS IT — through `DictionarySpace`, the same object the body uses.

    This replaced the blend sweep on the default path on 2026-09-14. The sweep called one of its
    seven columns «the declared reading», and since policy v11 there is no blend to declare: R
    decides, D proposes, and a stated cell decides before either. A report that scored a reading
    nobody runs is a report that can only mislead — it printed `mental.a~physical.a`, a declared FAR
    with a stated antonym, at +0.105.

    Built from the matrices in hand rather than from the database, so a DRY RUN is scored exactly as
    the applied build would be: the rows are the same rows, one `as_row()` away from storage.
    """
    from tk2.dictionary.space import DictionarySpace

    if config.reading is None or not config.reading.reads_separately:
        print()
        print("THE BAR AS THE READER SCORES IT — not available: this policy version declares no "
              "`mode = separate`. Policy v11 (db/0003) is what rules it.")
        return {}

    def rows_of(matrix_):
        return [] if matrix_ is None else [
            {"key": row.key, "cells": [cell.as_row() for cell in row.cells]}
            for row in matrix_.rows
        ]

    space = DictionarySpace(config, built.dimensions,
                            rows_of(built.relational), rows_of(built.distributional))

    print()
    print("=" * 96)
    print("THE BAR AS THE READER SCORES IT — R decides · D proposes · ABSTAIN when R is silent")
    print("=" * 96)
    print(f"  NEAR floor {config.reading.near_floor}   FAR below {config.reading.far_ceiling}   "
          f"(a stated cell decides first, except {list(config.reading.structural_relations or ())})")
    print(f"  {'pair':<26} {'exp':<5} {'read':<8} {'by':<11} {'R cos':>8} {'cell':>7}  {'what decided':<26}")
    print(f"  {'-' * 26} {'-' * 5} {'-' * 8} {'-' * 11} {'-' * 8} {'-' * 7}  {'-' * 26}")

    decided = wrong = abstained = 0
    pairs = []
    for pair in config.bar:
        reading = space.read(pair.a, pair.b)
        if reading is None:
            verdict, source, cosine, cell, by = "ABSTAIN", "unknown key", None, None, ""
        else:
            verdict, source = reading.verdict, reading.source
            cosine, cell, by = reading.relational_cosine, reading.relational_cell, reading.relational_relation
        if verdict == "ABSTAIN":
            abstained += 1
            mark = ""
        elif verdict == pair.verdict:
            decided += 1
            mark = ""
        else:
            wrong += 1
            mark = "  <- WRONG"
        pairs.append({"a": pair.a, "b": pair.b, "expected": pair.verdict, "verdict": verdict,
                      "source": source, "relational_cosine": cosine, "relational_cell": cell,
                      "relation": by})
        print(f"  {pair.a + ' ~ ' + pair.b:<26} {pair.verdict:<5} {verdict:<8} {source:<11} "
              f"{_number(cosine):>8} {_number(cell):>7}  {by or '':<26}{mark}")

    total = len(config.bar)
    print()
    print(f"  DECIDED {decided} of {total} · WRONG {wrong} · ABSTAIN {abstained}")
    print(f"  an ABSTENTION is not a miss — «R is silent on this pair» is a diagnosis, and R is "
          f"silent on {sum(1 for p in pairs if p['source'] == 'silent')} of them")
    return {"decided": decided, "wrong": wrong, "abstain": abstained, "pairs": pairs}


def report_dual(built: build.BaseBuild, config: DictionaryConfig, vectors=None, mixes=MIXES,
                standing: float | None = None) -> dict:
    """The bar under both geometries and their blend — the reading T5's gate will be built on.

    HOW THEY ARE COMBINED, and why it is the only honest shape available: the two rows are
    CONCATENATED (R's columns, then D's, scaled by `mix`) and one cosine is taken over the whole
    vector. Nothing is averaged with anything — the review measured what averaging does, and it is
    the reason there are two matrices at all: `enter~leave` reads -0.331 on relations alone and
    +0.519 once a gloss tail is mixed in, because opposites are defined in the same words.

    THE BLEND CAN STILL BURY THE SIGN, which is why the table runs past any plausible setting: a
    mix high enough for D to speak is a mix high enough for a topical overlap to outweigh a stated
    opposition. Where that happens is a NUMBER, printed below — and since the ruling of 2026-09-09
    the sweep says which of its columns is the one the base is read under, because a table where the
    standing reading is indistinguishable from six alternatives is a table nobody can conclude from.
    """
    relational, distributional = built.relational, built.distributional
    readings = {
        "R alone": read_bar(
            config.bar,
            relational.cosine,
            lambda a, b: relations.stated_between(relational, a, b),
        ),
        "D alone": read_bar(
            config.bar,
            distributional.cosine,
            lambda a, b: (distributional.cell(a, b), distributional.cell(b, a)),
        ),
    }
    for mix in mixes:
        readings[f"R+D mix {mix}"] = read_bar(
            config.bar,
            lambda a, b, m=mix: matrix.blended_cosine(relational, distributional, a, b, m),
        )

    print()
    print("=" * 96)
    print("THE DUAL READ — the same bar under R alone, D alone, and the two concatenated")
    print("=" * 96)
    columns = ["R alone", "D alone"] + [f"R+D mix {mix}" for mix in mixes]
    if standing is not None:
        print(f"  the declared reading is mix {standing} — every other column is a measurement")
    print(f"  {'pair':<26} {'exp':<5}" + "".join(f"{name.replace('R+D mix ', 'mix '):>12}" for name in columns))
    print(f"  {'-' * 26} {'-' * 5}" + "".join(f"{'-' * 11:>12}" for _ in columns))
    for position, pair in enumerate(config.bar):
        cells = "".join(
            f"{_number(readings[name]['pairs'][position]['cosine']):>12}" for name in columns
        )
        print(f"  {pair.a + ' ~ ' + pair.b:<26} {pair.verdict:<5}" + cells)

    print()
    for name in columns:
        ruled = standing is not None and name == f"R+D mix {standing}"
        print(_reading_line(name, readings[name]) + ("   <- the declared reading" if ruled else ""))
        for broken in readings[name]["local_order"]["broken"][:3]:
            print(f"      ! {broken}")

    if vectors is not None:
        print()
        print("  WHAT D ACTUALLY SHARES — the bar pairs' DIRECT cell, and the words behind it")
        print("  (the column above is the row COSINE, which is second-order: two dimensions can be")
        print("   near in D without their own definitions sharing a word)")
        for pair in config.bar:
            cell = built.distributional.cell(pair.a, pair.b)
            shared = distribution.shared_words(vectors, pair.a, pair.b)
            print(f"    {pair.a + ' ~ ' + pair.b:<26} {pair.verdict:<5} "
                  f"{_cell_text(cell):>22}   shared: {' '.join(shared) if shared else '(nothing)'}")

    print()
    print("  WHERE THE SIGN GOES: a pair R states as opposition, read at each blend")
    opposed = [
        pair for pair in config.bar
        if any(
            cell is not None and cell.weight < 0
            for cell in relations.stated_between(relational, pair.a, pair.b)
        )
    ]
    for pair in opposed:
        blended = {mix: matrix.blended_cosine(relational, distributional, pair.a, pair.b, mix)
                   for mix in mixes}
        line = "".join(f"{_number(blended[mix]):>12}" for mix in mixes)
        flips = [mix for mix in mixes if (blended[mix] or 0) > 0]
        print(f"    {pair.a + ' ~ ' + pair.b:<26} {pair.verdict:<5}" + line
              + (f"   turns positive at mix {min(flips)}" if flips else "   stays negative throughout"))

    return {name: _reading_summary(reading) for name, reading in readings.items()}


def _reading_summary(reading: dict) -> dict:
    """A reading without its per-pair cells — what the json carries for a table of many readings."""
    return {
        "pairs": [{"a": p["a"], "b": p["b"], "verdict": p["verdict"], "cosine": p["cosine"]}
                  for p in reading["pairs"]],
        "mute": reading["mute"],
        "unscorable": reading["unscorable"],
        "local_order": reading["local_order"],
        "global_order": reading["global_order"],
        "margin": reading["margin"],
        "worst_near": reading["worst_near"],
        "best_far": reading["best_far"],
    }


# ------------------------------------------------------------------------------------------------
# THE ACCEPTANCE FLOORS — MEASURED HERE, DECLARED NOWHERE (T5, the Captain's ruling)
# ------------------------------------------------------------------------------------------------
#
# The bar has been read threshold-free all through E1 on purpose: the cosine, the cells, MUTE, the
# local order. T5 is where NEAR and FAR finally have to mean a number — and this file measures
# candidates and states nothing. The floors are curation, they land in `ReadingPolicy` beside the
# mix (a reading of two matrices, not a property of either), and they arrive as rows when the
# Captain has ruled, exactly as the mix did.
#
# THE PROTOTYPE'S 0.30 / 0.15 IS A CANDIDATE LIKE ANY OTHER AND IS MEASURED AS ONE. It was
# calibrated at 983 dimensions and its own justification has already failed to reproduce at scale
# (`sleep~bed` 0.353 there, 0.154 here), so it is in the table to be read, never to be inherited.
#
# WHAT IS MEASURED AND WHY EACH PART IS HERE:
#   - the POPULATION. A floor is a claim about how much of the base is NEAR, and a threshold read
#     without the distribution behind it is a number nobody can size. This base's median pair reads
#     +0.026 and its top decile starts at +0.131, which is the fact that decides most of the
#     argument.
#   - the FRONTIER over (NEAR floor, FAR ceiling). Every distinct decision boundary the eighteen
#     readings admit, scored as decided-right / decided-WRONG / abstained. ABSTAIN is first-class in
#     this project, so a shape that can say «I do not know» is measured beside the ones that cannot.
#   - the WITNESSES. What a candidate floor actually admits, sampled and printed with the words
#     behind each pair. A floor that reads well on eighteen curated pairs and admits nine hundred
#     thousand junk ones is a floor that has to be seen to be argued with.
#
# numpy enters the project HERE, and only in this tool. Nine and a half million cosines is not a
# pure-python loop, and `tk2/dictionary/` stays free of it: the pure side keeps its sparse rows and
# this densifies a copy for one measurement.

#: Where the population table is cut. Wide at the bottom because that is where the bar sits, and it
#: runs to 0.9 because the top of this distribution is a FINDING and not a tail: rows whose whole
#: gloss is function words are near-parallel, and the reader has to see how many.
FLOOR_GRID = (-0.05, 0.0, 0.02, 0.05, 0.10, 0.15, 0.20, 0.30, 0.50, 0.70, 0.90)

#: The quantiles printed for the population. p99.99 is in it because a floor that admits a tenth of
#: the base and one that admits a ten-thousandth are different KINDS of claim.
FLOOR_QUANTILES = (0.5, 0.75, 0.90, 0.95, 0.99, 0.999, 0.9999)

#: The prototype's pair, kept as a named candidate so the table contains what NOT inheriting it
#: means in numbers rather than as an assertion.
PROTOTYPE_FLOORS = (0.30, 0.15)

#: How many pairs at a candidate floor are sampled to say what it admits. Five thousand rather than
#: fifty: the composition figure is a percentage and a percentage from fifty pairs is a mood.
FLOOR_SAMPLE = 5000

#: How many of those are printed with their evidence. Enough to read, few enough to read.
FLOOR_WITNESSES = 20

#: The sampler's seed, stated so the witnesses are the same witnesses on a re-run. A measurement
#: whose examples change every time it is run is a measurement nobody can quote.
FLOOR_SEED = 20260910


def dual_vectors(built: build.BaseBuild, mix: float):
    """Both matrices as ONE dense, L2-normalised array of 2n columns — the dual read, densified.

    The same concatenation `matrix.blended_row` performs and in the same column order (R's, then D's
    scaled by the mix), so a dot product here and `matrix.blended_cosine` there are the same number;
    the run asserts that on the bar's own pairs rather than trusting it.
    """
    import numpy as np

    keys = built.relational.keys
    index = {key: i for i, key in enumerate(keys)}
    n = len(keys)

    dense = np.zeros((n, 2 * n), dtype=np.float32)
    for row in built.relational.rows:
        for cell in row.cells:
            dense[row.index, index[cell.column]] = cell.weight
    if mix:
        for row in built.distributional.rows:
            for cell in row.cells:
                dense[row.index, n + index[cell.column]] = mix * cell.weight

    norm = np.linalg.norm(dense, axis=1, keepdims=True)
    norm[norm == 0] = 1.0
    dense /= norm
    return dense, index


def population(vectors, grid=FLOOR_GRID, quantiles=FLOOR_QUANTILES, chunk: int = 512) -> dict:
    """The whole upper triangle, as a histogram and the shares above a grid.

    Chunked rather than materialised: the cosine matrix of this base is 79 MB and the next base's
    will not be, and a measurement that only runs while the base is small is a measurement that
    stops being run.
    """
    import numpy as np

    n = vectors.shape[0]
    edges = np.linspace(-1.0, 1.0, 4001)
    hist = np.zeros(len(edges) - 1, dtype=np.int64)
    total = 0
    for start in range(0, n, chunk):
        stop = min(start + chunk, n)
        block = vectors[start:stop] @ vectors.T
        for offset in range(stop - start):
            row = block[offset, start + offset + 1:]
            if row.size:
                hist += np.histogram(row, bins=edges)[0]
                total += row.size

    cumulative = np.cumsum(hist)
    centres = (edges[:-1] + edges[1:]) / 2

    def at_quantile(q: float) -> float:
        return float(centres[min(int(np.searchsorted(cumulative, q * total)), len(centres) - 1)])

    def above(threshold: float) -> int:
        bucket = max(0, min(int(np.searchsorted(edges, threshold)) - 1, len(hist) - 1))
        return int(total - (cumulative[bucket - 1] if bucket else 0))

    return {
        "pairs": total,
        "quantiles": {q: at_quantile(q) for q in quantiles},
        "above": {t: above(t) for t in grid},
        "negative": int(cumulative[int(np.searchsorted(edges, 0.0)) - 1]),
        "_above": above,
    }


def floor_frontier(readings: list[tuple[str, str, float]]) -> list[dict]:
    """Every (NEAR floor, FAR ceiling) the bar itself can distinguish, scored.

    The candidate cuts are the MIDPOINTS between consecutive readings, which is the only honest
    grid: a threshold set exactly on a measured value is a coin toss about that pair, and rounding
    one to two decimals moves it across its own pair as often as not.
    """
    values = sorted({round(float(value), 6) for _a, _b, value in readings})
    cuts = [values[0] - 0.01] + [(x + y) / 2 for x, y in zip(values, values[1:])] + [values[-1] + 0.01]

    out = []
    for near in cuts:
        for far in cuts:
            if far > near:
                continue
            decided = wrong = abstained = 0
            errors = []
            for a, b, value in readings:
                if value >= near:
                    decided += 1
                    if b != "NEAR":
                        wrong += 1
                        errors.append(f"{a} called NEAR")
                elif value <= far:
                    decided += 1
                    if b != "FAR":
                        wrong += 1
                        errors.append(f"{a} called FAR")
                else:
                    abstained += 1
            out.append({"near": near, "far": far, "decided": decided, "wrong": wrong,
                        "abstained": abstained, "errors": errors})
    out.sort(key=lambda row: (row["wrong"], -row["decided"], -row["near"]))
    return out


def floor_composition(built: build.BaseBuild, vectors, gloss_vectors, index, floor: float,
                      sample: int = FLOOR_SAMPLE, seed: int = FLOOR_SEED) -> dict:
    """What sits above a candidate floor: how many pairs, how many of them R states anything about,
    and what a random sample of them is actually made of.

    The composition is the point. `pairs_only_junk` here is not `distribution.junk_pollution`'s
    figure — that one is about every overlapping pair in D, and this one is about the pairs a FLOOR
    would call NEAR, which is the population an acceptance verdict would actually be issued over.
    """
    import numpy as np

    keys = built.relational.keys
    n = len(keys)
    rng = np.random.default_rng(seed)

    above = 0
    with_relation = 0
    picked: list[tuple[float, str, str]] = []
    for start in range(0, n, 512):
        stop = min(start + 512, n)
        block = vectors[start:stop] @ vectors.T
        for offset in range(stop - start):
            row = start + offset
            hits = np.nonzero(block[offset, row + 1:] >= floor)[0] + row + 1
            above += hits.size
            for column in hits:
                key, other = keys[row], keys[int(column)]
                if built.relational.cell(key, other) or built.relational.cell(other, key):
                    with_relation += 1
    if above:
        # A second pass to sample: the first counted, and drawing without knowing the total would
        # weight the early rows. `share` is the acceptance probability that lands ~`sample` pairs.
        share = min(1.0, sample / above)
        for start in range(0, n, 512):
            stop = min(start + 512, n)
            block = vectors[start:stop] @ vectors.T
            for offset in range(stop - start):
                row = start + offset
                hits = np.nonzero(block[offset, row + 1:] >= floor)[0] + row + 1
                if not hits.size:
                    continue
                for column in hits[rng.random(hits.size) < share]:
                    picked.append((float(block[offset, int(column)]), keys[row], keys[int(column)]))

    made_of = {"only_junk": 0, "a_real_word": 0, "nothing_direct": 0}
    witnesses = []
    for value, a, b in picked:
        shared = distribution.shared_words(gloss_vectors, a, b)
        if not shared:
            made_of["nothing_direct"] += 1
        elif set(shared) <= JUNK_WORDS:
            made_of["only_junk"] += 1
        else:
            made_of["a_real_word"] += 1
        cell = built.relational.cell(a, b) or built.relational.cell(b, a)
        witnesses.append({"cosine": value, "a": a, "b": b, "shared": shared,
                          "relation": cell.relation if cell else None})
    rng.shuffle(witnesses)
    return {
        "floor": floor,
        "pairs": above,
        "with_relation": with_relation,
        "sampled": len(picked),
        "made_of": made_of,
        "witnesses": witnesses[:FLOOR_WITNESSES],
    }


def sign_survival(built: build.BaseBuild, vectors, index, mix: float, shown: int = 8) -> dict:
    """What becomes of R's sign in the dual read — the FAR half of any floor, measured.

    D is unsigned, so a negative reading is R's alone and no threshold has to be calibrated for it:
    zero IS the boundary, by construction rather than by fitting. That makes the FAR half of a
    two-sided shape almost free — and it makes THIS the number the shape has to be ruled on, because
    a sign the blend has already buried is a FAR verdict nobody will ever get.
    """
    import numpy as np

    relational = built.relational
    n = len(relational.keys)
    R = np.zeros((n, n), dtype=np.float32)
    for row in relational.rows:
        for cell in row.cells:
            R[row.index, index[cell.column]] = cell.weight
    norm = np.linalg.norm(R, axis=1, keepdims=True)
    norm[norm == 0] = 1.0
    r_only = R / norm

    opposed = np.argwhere(np.triu((R < 0) | (R.T < 0), 1))
    keys_list = relational.keys
    measured = []
    for left, right in opposed:
        measured.append({
            "a": keys_list[left],
            "b": keys_list[right],
            "r": float(r_only[left] @ r_only[right]),
            "dual": float(vectors[left] @ vectors[right]),
        })
    lifted = [row for row in measured if row["r"] < 0 <= row["dual"]]

    # And the other direction: of every pair in the base that READS below zero, how many are an
    # opposition R states between the two, and how many are two rows disagreeing in sign about a
    # third dimension? The second is the antonym column-read working at second order, and it is by
    # far the larger number — which is worth knowing before anybody reads «negative» as «stated».
    stated_negative = (R < 0) | (R.T < 0)
    direct = third = 0
    for start in range(0, n, 512):
        stop = min(start + 512, n)
        block = vectors[start:stop] @ vectors.T
        for offset in range(stop - start):
            row = start + offset
            hits = np.nonzero(block[offset, row + 1:] < 0)[0] + row + 1
            if not hits.size:
                continue
            here = int(stated_negative[row, hits].sum())
            direct += here
            third += hits.size - here

    return {
        "opposed_pairs": len(measured),
        "negative_in_r": sum(1 for row in measured if row["r"] < 0),
        "negative_in_dual": sum(1 for row in measured if row["dual"] < 0),
        "lifted": len(lifted),
        "worst": sorted(lifted, key=lambda row: -row["dual"])[:shown],
        "direct_negative": direct,
        "third_party": third,
    }


def report_floors(built: build.BaseBuild, config: DictionaryConfig, gloss_vectors, mix: float) -> dict:
    """THE FLOOR MEASUREMENT, through the reader. Nothing here rules anything — the floor is the
    Captain's.

    REWRITTEN 2026-09-14 for policy v11. It used to measure a BLENDED population and assert its own
    arithmetic against `matrix.blended_cosine`; under separate reads there is no blend to measure,
    and a floor fitted to one would describe a geometry the engine does not run.

    What a floor can and cannot do is the whole point: a stated cell decides before any threshold,
    so the floor governs exactly the pairs R speaks about through its COSINE — and the honest
    report names the two walls it sits between.
    """
    import numpy as np

    from tk2.dictionary.space import DictionarySpace

    if config.reading is None or not config.reading.reads_separately:
        print()
        print("REFUSED: this policy declares no `mode = separate`, so there is no reading to fit a "
              "floor to. Policy v11 (db/0003) is what rules it.")
        return {}

    def rows_of(matrix_):
        return [] if matrix_ is None else [
            {"key": row.key, "cells": [cell.as_row() for cell in row.cells]}
            for row in matrix_.rows
        ]

    relation_rows, distribution_rows = rows_of(built.relational), rows_of(built.distributional)
    dimensions = built.dimensions

    print()
    print("=" * 96)
    print("THE ACCEPTANCE FLOOR — MEASURED, NOT RULED (the floor is the Captain's)")
    print("=" * 96)
    print(f"  reading           R decides · D proposes · ABSTAIN when R is silent")
    print(f"  dimensions        {len(dimensions):,}")
    print(f"  standing floor    {config.reading.near_floor}")

    # WHERE THE BASE SITS, on R alone — the population the floor is a threshold in.
    space = DictionarySpace(config, dimensions, relation_rows, distribution_rows)
    population_matrix = space._relational                      # the reader's own normalised rows
    sample = population_matrix @ population_matrix.T
    upper = sample[np.triu_indices(len(dimensions), k=1)]
    print()
    print("  WHERE THE WHOLE BASE SITS — R's cosine over every pair of dimensions")
    print("    " + "  ".join(f"p{q:g} {np.percentile(upper, q):+.3f}"
                             for q in (50, 90, 99, 99.9)))
    print(f"    negative {int((upper < 0).sum()):,} of {upper.size:,} "
          f"({100 * (upper < 0).mean():.4f}%) — every one of them R's own sign")

    # THE SWEEP: what each candidate floor decides, and what it gets wrong.
    print()
    print("  WHAT EACH CANDIDATE FLOOR DECIDES")
    print(f"    {'floor':>7} {'decided':>8} {'WRONG':>6} {'abstain':>8}   first misses")
    # Each pair is READ ONCE and the floors are applied to the numbers. Re-reading per floor would
    # rebuild a 166 MB space nine times over to arrive at the same arithmetic.
    once = []
    for pair in config.bar:
        reading = space.read(pair.a, pair.b)
        if reading is None:
            once.append((pair, None, None))
            continue
        settled = (reading.verdict if (reading.relational_cell
                                       and config.reading.decides_by_cell(reading.relational_relation))
                   or reading.source != "relational"
                   or reading.relational_cosine < config.reading.far_ceiling
                   else None)
        once.append((pair, settled, reading.relational_cosine))

    measured = {}
    for floor in FLOOR_GRID:
        if floor <= config.reading.far_ceiling:
            continue
        decided = wrong = abstained = 0
        misses = []
        for pair, settled, cosine in once:
            if settled is not None:
                verdict = settled
            elif cosine is None:
                verdict = "ABSTAIN"
            else:
                verdict = "NEAR" if cosine >= floor else "ABSTAIN"
            if verdict == "ABSTAIN":
                abstained += 1
            elif verdict == pair.verdict:
                decided += 1
            else:
                wrong += 1
                misses.append(f"{pair.a}~{pair.b}")
        measured[floor] = {"decided": decided, "wrong": wrong, "abstain": abstained}
        standing = "  <- the standing floor" if floor == config.reading.near_floor else ""
        print(f"    {floor:>+7.2f} {decided:>8} {wrong:>6} {abstained:>8}   "
              f"{' '.join(misses[:2])}{standing}")

    # THE TWO WALLS. A floor is only ever between them, and `db/0002` failed by sitting on one.
    governed = []
    for pair in config.bar:
        reading = space.read(pair.a, pair.b)
        if reading is None or reading.source != "relational":
            continue
        if reading.relational_cell and config.reading.decides_by_cell(reading.relational_relation):
            continue                                   # its cell decides; no floor touches it
        governed.append((reading.relational_cosine, pair.verdict, f"{pair.a}~{pair.b}"))
    below = sorted((row for row in governed if row[1] == "FAR"), reverse=True)
    wall = below[0][0] if below else config.reading.far_ceiling
    # The wall ABOVE is the lowest declared NEAR that a floor could still admit — one BELOW the FAR
    # wall is not a wall at all, it is a pair no floor can ever decide, and saying otherwise would
    # invite someone to fit a floor to it and get a wrong answer instead of an abstention.
    above = sorted(row for row in governed if row[1] == "NEAR" and row[0] > wall)
    unreachable = sorted(row for row in governed if row[1] == "NEAR" and 0 < row[0] <= wall)
    print()
    print("  THE TWO WALLS — the floor governs the pairs R speaks about through its COSINE")
    if below:
        print(f"    below   {below[0][2]:<24} FAR  {below[0][0]:+.4f}")
    if above:
        print(f"    above   {above[0][2]:<24} NEAR {above[0][0]:+.4f}")
    else:
        print(f"    above   (nothing) — no declared NEAR reads above the FAR wall")
    if unreachable:
        print(f"    NO FLOOR CAN DECIDE these declared NEARs: they read at or below the FAR wall —")
        for cosine, _verdict, pair in unreachable[:4]:
            print(f"      {pair:<24} NEAR {cosine:+.4f}")
        print(f"    they are abstentions by geometry, not by threshold, and moving the floor down to")
        print(f"    reach them buys a WRONG answer on {below[0][2] if below else 'a FAR pair'} first")
    if below and above and below[0][0] < above[0][0]:
        print(f"    the gap is {above[0][0] - below[0][0]:+.4f} wide — a floor belongs in the MIDDLE "
              f"of it, never on a wall")
        print(f"    (db/0002's floor sat 0.0079 above a FAR pair and failed the first time the base "
              f"moved)")
    return {"floors": measured,
            "walls": {"below": below[0] if below else None, "above": above[0] if above else None}}

def _score_floors(readings, near: float, far: float) -> dict:
    """One named pair of floors, scored the way the frontier scores its own."""
    decided = wrong = abstained = 0
    errors = []
    for label, verdict, value in readings:
        if value >= near:
            decided += 1
            if verdict != "NEAR":
                wrong += 1
                errors.append(f"{label} called NEAR")
        elif value <= far:
            decided += 1
            if verdict != "FAR":
                wrong += 1
                errors.append(f"{label} called FAR")
        else:
            abstained += 1
    return {"near": near, "far": far, "decided": decided, "wrong": wrong,
            "abstained": abstained, "errors": errors}


# ------------------------------------------------------------------------------------------------
# THE DERIVATIONAL DOWN-WEIGHT — the open item E1 was chartered to close, MEASURED
# ------------------------------------------------------------------------------------------------

#: The two pairs the whole question is about. `land.n ~ land.v` is declared FAR and
#: `cause.n ~ cause.v` NEAR, and today they are THE SAME CELL — `derivational` at ±0.90 — so any
#: down-weight moves both by the same arithmetic. Named here because the table below is unreadable
#: without knowing which two rows to look at first.
TARGET_PAIRS = (("land.n", "land.v"), ("cause.n", "cause.v"))

#: The candidates the run measures when it is given none. 0.90 IS the standing weight, so the
#: column is not a special case; 0.00 switches the relation off entirely (a cell whose only claim
#: was `derivational` ceases to exist rather than weakening), which is the end of the range and has
#: to be in it.
DOWN_WEIGHTS = (0.90, 0.75, 0.60, 0.45, 0.30, 0.15, 0.00)


def derivational_variants(policy_relations, weights):
    """One `RelationPolicy` per candidate, differing in exactly one number.

    A variant rather than an edited policy: a run that measured seven weights by mutating one object
    would have seven results and one declaration, which is the whole failure `DictionaryConfig`
    exists to prevent.
    """
    variants = {}
    for weight in weights:
        variants[weight] = replace(
            policy_relations,
            weights=tuple(
                (name, weight if name == "derivational" else value)
                for name, value in policy_relations.weights
            ),
        )
    return variants


def compare_derivational(config: DictionaryConfig, scope: str, weights, closed=None) -> dict:
    """Build R once per candidate weight over ONE key space, with D built once beside them.

    The membership half is identical by construction — the closure reads GLOSSES, which no relation
    weight can touch — and D is untouched too, so the comparison is honest cell for cell and the
    dual read can be taken at every candidate without rebuilding the second geometry.
    """
    started = time.time()
    lexicon = wordnet_lexicon()
    provider = WordNetProvider(lexicon, lemma_scope=scope)

    print(f"resource      WordNet through nltk — {len(lexicon):,} words · lemma scope {scope!r}")
    print("building the definition digraph, the closure and D ONCE…", flush=True)
    graph = closure.build_digraph(provider, config.closure)
    result = closure.seed_closure(graph, config.seeds, config.closure)
    dimensions = tuple(glosses.dimensions_of(result.words, provider))
    print(f"  {len(result.words):,} words -> {len(dimensions):,} dimensions "
          f"({time.time() - started:.0f}s)")

    built_d = None
    if config.distribution is not None:
        built_d = distribution.build(dimensions, provider, config.distribution)
        print(f"  D: {built_d.stats()['nonzero']:,} cells ({time.time() - started:.0f}s)", flush=True)

    built = {}
    for weight, variant in derivational_variants(config.relations, weights).items():
        built[weight] = relations.build(dimensions, provider, variant)
        print(f"  derivational {weight:.2f}  R: {built[weight].stats()['nonzero']:,} cells "
              f"({time.time() - started:.0f}s)", flush=True)
    return {"r": built, "d": built_d, "dimensions": dimensions}


def _superseded_reading_notice(what: str) -> None:
    """Printed by every instrument that still scores a BLEND.

    Policy v11 abolished the blend: R decides, D proposes, and a stated cell decides before either.
    These comparisons are kept because they are how their rulings were measured and how they would
    be re-measured — but a reader meeting their numbers today must know the verdict column is not
    the one the engine runs.
    """
    print()
    print(f"  NOTE: {what} is scored under the BLENDED reading, which policy v11 (db/0003) "
          f"superseded.")
    print(f"        The engine reads R and D APART. These columns are a measurement of a reading "
          f"nobody runs;")
    print(f"        `--floors` and the default report score through the engine's own reader.")


def report_derivational(measured: dict, config: DictionaryConfig, mix: float) -> dict:
    """The candidates side by side: the two target pairs first, then the whole bar, then the cost.

    THE COST IS THE HALF THAT DECIDES IT. A down-weight does not only move the pair it was aimed at
    — `derivational` is 11.7% of R's cells — so what every candidate does to the OTHER seventeen
    pairs is printed pair by pair, and the summary says plainly which ones each one costs.
    """
    _superseded_reading_notice("the derivational sweep")
    built = measured["r"]
    built_d = measured["d"]
    weights = list(built)
    standing = weights[0]

    readings = {}
    dual = {}
    for weight in weights:
        matrix_r = built[weight]
        readings[weight] = read_bar(
            config.bar, matrix_r.cosine,
            lambda a, b, m=matrix_r: relations.stated_between(m, a, b),
        )
        if built_d is not None:
            dual[weight] = read_bar(
                config.bar,
                lambda a, b, m=matrix_r: matrix.blended_cosine(m, built_d, a, b, mix),
            )

    print()
    print("=" * 96)
    print("THE DERIVATIONAL DOWN-WEIGHT — the two pairs the question is about")
    print("=" * 96)
    print(f"  {'pair':<26} {'exp':<5}" + "".join(f"{w:>10.2f}" for w in weights))
    for a, b in TARGET_PAIRS:
        declared = next((p for p in config.bar if {p.a, p.b} == {a, b}), None)
        verdict = declared.verdict if declared else "?"
        print(f"  {a + ' ~ ' + b:<26} {verdict:<5}"
              + "".join(f"{_number(built[w].cosine(a, b)):>10}" for w in weights) + "   R alone")
        if built_d is not None:
            print(f"  {'':<26} {'':<5}"
                  + "".join(f"{_number(matrix.blended_cosine(built[w], built_d, a, b, mix)):>10}"
                            for w in weights) + f"   R+D mix {mix}")
        cell = built[standing].cell(a, b)
        print(f"  {'':<26} {'':<5}   stated: {_cell_text(cell)}"
              + (f" / {_cell_text(built[standing].cell(b, a))}" if built[standing].cell(b, a) else ""))
        if built_d is not None:
            print(f"  {'':<26} {'':<5}   D says: {_cell_text(built_d.cell(a, b))}")

    # THE NUMBER THE WHOLE QUESTION TURNS ON. The two pairs are the same cell at the same weight, so
    # a down-weight scales BOTH — and what a ruling needs to know is not where each one lands but
    # whether the distance between them ever opens. Absolute and relative, because they do not
    # answer the same way.
    if len(TARGET_PAIRS) == 2:
        (near_a, near_b), (far_a, far_b) = TARGET_PAIRS[1], TARGET_PAIRS[0]
        print()
        print("  THE GAP BETWEEN THEM — cause.n~cause.v (NEAR) minus land.n~land.v (FAR)")
        for label, cosine_of in (
            ("R alone", lambda w, a, b: built[w].cosine(a, b)),
            *(() if built_d is None else ((
                f"R+D mix {mix}",
                lambda w, a, b: matrix.blended_cosine(built[w], built_d, a, b, mix),
            ),)),
        ):
            gaps = []
            for weight in weights:
                near = cosine_of(weight, near_a, near_b) or 0.0
                far = cosine_of(weight, far_a, far_b) or 0.0
                gaps.append((near - far, (near / far) if far else None))
            print(f"    {label:<16} absolute" + "".join(f"{gap:>10.3f}" for gap, _ratio in gaps))
            print(f"    {'':<16} ratio   "
                  + "".join(f"{'      —' if ratio is None else f'{ratio:>10.3f}'}"
                            for _gap, ratio in gaps))

    print()
    print("=" * 96)
    print(f"THE WHOLE BAR ON R ALONE — one column per candidate weight")
    print("=" * 96)
    print(f"  {'pair':<26} {'exp':<5}" + "".join(f"{w:>10.2f}" for w in weights))
    for position, pair in enumerate(config.bar):
        moved = "*" if len({round(readings[w]["pairs"][position]["cosine"] or 0, 6)
                            for w in weights}) > 1 else " "
        print(f" {moved}{pair.a + ' ~ ' + pair.b:<26} {pair.verdict:<5}"
              + "".join(f"{_number(readings[w]['pairs'][position]['cosine']):>10}" for w in weights))

    print()
    for weight in weights:
        print(_reading_line(f"R alone  {weight:.2f}", readings[weight]))
    if dual:
        print()
        for weight in weights:
            print(_reading_line(f"R+D {mix}  {weight:.2f}", dual[weight]))

    print()
    print("=" * 96)
    print("WHAT EACH CANDIDATE COSTS — the shape of R, and the pairs it moves the wrong way")
    print("=" * 96)
    print(f"  {'weight':>8} {'cells':>10} {'derivational':>14} {'negative':>10} {'silent':>8}   "
          f"pairs whose local order breaks")
    out = {}
    for weight in weights:
        stats = built[weight].stats()
        broken = readings[weight]["local_order"]["broken"]
        regressed = sorted(
            set(_broken_pairs(broken)) - set(_broken_pairs(readings[standing]["local_order"]["broken"]))
        )
        print(f"  {weight:>8.2f} {stats['nonzero']:>10,} "
              f"{stats['by_relation'].get('derivational', 0):>14,} {stats['negative']:>10,} "
              f"{stats['silent_rows']:>8,}   "
              f"{' '.join(regressed) if regressed else '(none beyond the standing weight)'}")
        out[weight] = {
            "stats": stats,
            "r": _reading_summary(readings[weight]),
            "dual": _reading_summary(dual[weight]) if dual else None,
            "newly_broken": regressed,
        }
    return {"mix": mix, "candidates": {str(w): v for w, v in out.items()}}


def _broken_pairs(broken) -> list[str]:
    """The NEAR pair named at the head of each broken-order sentence — what a candidate costs, as
    names rather than as a count."""
    return [line.split(" (NEAR", 1)[0] for line in broken]


# ------------------------------------------------------------------------------------------------
# THE PARKED QUESTION (b) — the high-frequency dimensions, as a WEIGHTING
# ------------------------------------------------------------------------------------------------


def compare_weighting(config: DictionaryConfig, scope: str, closed=None) -> dict:
    """Build D twice over ONE key space, changing only what a shared gloss word is worth.

    A weighting cannot move membership — the closure reads the digraph, and this touches only how
    much each word of a definition counts — so the two Ds are comparable cell for cell, which is
    what `matrix.diff` needs and what makes «this many cells the floor now refuses» a real number.
    """
    started = time.time()
    lexicon = wordnet_lexicon()
    provider = WordNetProvider(lexicon, lemma_scope=scope)

    print(f"resource      WordNet through nltk — {len(lexicon):,} words · lemma scope {scope!r}")
    print("building the definition digraph, the closure and R ONCE…", flush=True)
    graph = closure.build_digraph(provider, config.closure)
    result = closure.seed_closure(graph, config.seeds, config.closure)
    dimensions = tuple(glosses.dimensions_of(result.words, provider))
    relational = relations.build(dimensions, provider, config.relations)
    print(f"  {len(result.words):,} words -> {len(dimensions):,} dimensions · R "
          f"{relational.stats()['nonzero']:,} cells ({time.time() - started:.0f}s)")

    built = {}
    vectors = {}
    for weighting in ("uniform", "idf"):
        walk = replace(config.distribution, weighting=weighting)
        built[weighting] = distribution.build(dimensions, provider, walk, closed=closed)
        vectors[weighting] = distribution.gloss_vectors(dimensions, provider, walk, closed)
        print(f"  {weighting:<8} D: {built[weighting].stats()['nonzero']:,} cells "
              f"({time.time() - started:.0f}s)", flush=True)
    return {"d": built, "r": relational, "vectors": vectors, "walk": config.distribution}


def report_weighting(measured: dict, config: DictionaryConfig, mix: float) -> dict:
    """Uniform against idf: what the down-weight does to D's cells, to the junk, and to the bar."""
    _superseded_reading_notice("the weighting comparison")
    built = measured["d"]
    relational = measured["r"]
    modes = ["uniform", "idf"]
    stats = {mode: built[mode].stats() for mode in modes}
    walk = measured["walk"]

    print()
    print("=" * 96)
    print("D'S DIMENSIONS — one word one vote, against log(1 + N/df)")
    print("=" * 96)
    print(f"  {'':<22}" + "".join(f"{mode:>16}" for mode in modes))
    for label, key in (("stated cells", "nonzero"), ("silent rows", "silent_rows")):
        print(f"  {label:<22}" + "".join(f"{stats[mode][key]:>16,}" for mode in modes))
    print(f"  {'density %':<22}" + "".join(f"{stats[mode]['density_pct']:>16.4f}" for mode in modes))
    saturated = {
        mode: sum(1 for row in built[mode].rows for cell in row.cells
                  if cell.source != matrix.SOURCE_AXIS and abs(cell.weight - walk.cap) < 1e-9)
        for mode in modes
    }
    print(f"  {'at the cap':<22}" + "".join(f"{saturated[mode]:>16,}" for mode in modes))

    moved = matrix.diff(built["uniform"], built["idf"])
    print()
    print(f"  cells uniform states and idf does not   {len(moved['removed']):,}")
    print(f"  cells idf states and uniform does not   {len(moved['added']):,}")
    print(f"  cells both state, at another weight     {len(moved['changed']):,}")

    print()
    print(f"  POLLUTION — pairs whose only shared words are {sorted(JUNK_WORDS)}")
    pollution = {}
    for mode in modes:
        # The mass figure is measured UNDER ITS OWN WEIGHTING — that is the whole comparison. The
        # pair figure cannot move (it is membership), and the two being printed side by side is
        # what shows which half of the pollution a weighting can reach.
        weighted = replace(walk, weighting=mode)
        pollution[mode] = distribution.junk_pollution(
            measured["vectors"][mode], JUNK_WORDS, walk.min_shared,
            distribution.word_weights(measured["vectors"][mode], weighted),
        )
        print(f"    {mode:<8} pairs {pollution[mode]['overlapping_pairs']:>10,}   only junk "
              f"{pollution[mode]['pairs_only_junk']:>8,} ({pollution[mode]['pairs_only_junk_pct']}%)"
              f"   junk's share of the shared mass {pollution[mode]['mass_from_junk_pct']}%")

    print()
    print("=" * 96)
    print("THE BAR — D alone, and R+D, under both weightings")
    print("=" * 96)
    readings = {}
    for mode in modes:
        readings[f"D {mode}"] = read_bar(
            config.bar, built[mode].cosine,
            lambda a, b, m=built[mode]: (m.cell(a, b), m.cell(b, a)),
        )
        readings[f"R+D {mode}"] = read_bar(
            config.bar,
            lambda a, b, m=built[mode]: matrix.blended_cosine(relational, m, a, b, mix),
        )
    columns = list(readings)
    print(f"  {'pair':<26} {'exp':<5}" + "".join(f"{name:>14}" for name in columns))
    for position, pair in enumerate(config.bar):
        print(f"  {pair.a + ' ~ ' + pair.b:<26} {pair.verdict:<5}"
              + "".join(f"{_number(readings[name]['pairs'][position]['cosine']):>14}"
                        for name in columns))
    print()
    for name in columns:
        print(_reading_line(name, readings[name]))

    return {
        "stats": stats,
        "saturated": saturated,
        "diff": {k: len(v) for k, v in moved.items()},
        "pollution": pollution,
        "bar": {name: _reading_summary(reading) for name, reading in readings.items()},
    }


# ------------------------------------------------------------------------------------------------
# THE PARKED QUESTION (a) — the sense mode, WHICH MOVES MEMBERSHIP
# ------------------------------------------------------------------------------------------------


def compare_senses(config: DictionaryConfig, scope: str, closed=None) -> dict:
    """Build the whole base twice — closure, R and D — under `primary` and under `all`.

    THE ONE MEASUREMENT HERE THAT IS NOT LIKE THE OTHERS. The lemma scope, the antonym reading and
    the derivational weight all leave the key space alone, so they can be diffed cell for cell. The
    sense mode cannot: it changes what a word's DEFINITION IS, so it changes the digraph, so it
    changes which words the closure admits and therefore which dimensions exist. Two bases, not two
    readings of one — and that is why this is reported as two columns of counts and never as a diff.
    """
    started = time.time()
    lexicon = wordnet_lexicon()
    provider = WordNetProvider(lexicon, lemma_scope=scope)
    print(f"resource      WordNet through nltk — {len(lexicon):,} words · lemma scope {scope!r}")

    built = {}
    for mode in ("primary", "all"):
        variant = config.with_closure(senses=mode)
        if variant.distribution is not None:
            variant = variant.with_distribution(senses=mode)
        graph = closure.build_digraph(provider, variant.closure)
        graph_stats = closure.digraph_stats(graph)
        result = closure.seed_closure(graph, variant.seeds, variant.closure)
        dimensions = tuple(glosses.dimensions_of(result.words, provider))
        print(f"  {mode:<8} {graph_stats['nodes']:,} nodes · {graph_stats['edges']:,} edges · "
              f"{len(result.words):,} words -> {len(dimensions):,} dimensions "
              f"({time.time() - started:.0f}s)", flush=True)
        relational = relations.build(dimensions, provider, variant.relations)
        print(f"  {'':<8} R: {relational.stats()['nonzero']:,} cells "
              f"({time.time() - started:.0f}s)", flush=True)
        distributional = None
        if variant.distribution is not None:
            distributional = distribution.build(dimensions, provider, variant.distribution)
            print(f"  {'':<8} D: {distributional.stats()['nonzero']:,} cells "
                  f"({time.time() - started:.0f}s)", flush=True)
        built[mode] = build.BaseBuild(
            words=result.words,
            dimensions=dimensions,
            relational=relational,
            distributional=distributional,
            closure=result,
            graph_stats=graph_stats,
            one_ring_past=result.one_ring_past(graph),
        )
    return built


def report_senses(built: dict, config: DictionaryConfig, provider, mix: float, closed=None) -> dict:
    """Two bases side by side — and the membership question said out loud if it moved."""
    _superseded_reading_notice("the sense-mode comparison")
    modes = ["primary", "all"]

    print()
    print("=" * 96)
    print("THE SENSE MODE — `primary` (the first synset per POS) against `all` (every reading)")
    print("=" * 96)
    print(f"  {'':<24}" + "".join(f"{mode:>16}" for mode in modes))
    for label, value in (
        ("digraph nodes", lambda b: b.graph_stats["nodes"]),
        ("digraph edges", lambda b: b.graph_stats["edges"]),
        ("silent definitions", lambda b: b.graph_stats["silent"]),
        ("closure words", lambda b: len(b.words)),
        ("dimensions", lambda b: len(b.dimensions)),
        ("one ring past the cut", lambda b: len(b.one_ring_past)),
        ("R cells", lambda b: b.relational.stats()["nonzero"]),
        ("R negative", lambda b: b.relational.stats()["negative"]),
        ("R silent rows", lambda b: b.relational.stats()["silent_rows"]),
        ("D cells", lambda b: b.distributional.stats()["nonzero"] if b.distributional else 0),
        ("D silent rows", lambda b: b.distributional.stats()["silent_rows"] if b.distributional else 0),
    ):
        print(f"  {label:<24}" + "".join(f"{value(built[mode]):>16,}" for mode in modes))

    primary, every = set(built["primary"].dimensions), set(built["all"].dimensions)
    print()
    print(f"  MEMBERSHIP MOVED: {primary != every}")
    print(f"    dimensions only under `primary`   {len(primary - every):,}  "
          f"{' '.join(sorted(primary - every)[:12])}")
    print(f"    dimensions only under `all`       {len(every - primary):,}  "
          f"{' '.join(sorted(every - primary)[:12])}")

    readings = {}
    for mode in modes:
        base = built[mode]
        readings[f"R {mode}"] = read_bar(
            config.bar, base.relational.cosine,
            lambda a, b, m=base.relational: relations.stated_between(m, a, b),
        )
        if base.distributional is not None:
            readings[f"D {mode}"] = read_bar(config.bar, base.distributional.cosine)
            readings[f"R+D {mode}"] = read_bar(
                config.bar,
                lambda a, b, r=base.relational, d=base.distributional:
                    matrix.blended_cosine(r, d, a, b, mix),
            )

    columns = list(readings)
    print()
    print("=" * 96)
    print("THE BAR UNDER BOTH — a dash is a pair whose key is not a dimension of that base")
    print("=" * 96)
    print(f"  {'pair':<26} {'exp':<5}" + "".join(f"{name:>14}" for name in columns))
    for position, pair in enumerate(config.bar):
        print(f"  {pair.a + ' ~ ' + pair.b:<26} {pair.verdict:<5}"
              + "".join(f"{_number(readings[name]['pairs'][position]['cosine']):>14}"
                        for name in columns))
    print()
    for name in columns:
        print(_reading_line(name, readings[name]))

    vocabulary = {}
    for mode in modes:
        base = built[mode]
        if base.distributional is None:
            continue
        walk = config.distribution if mode == "primary" else replace(config.distribution, senses="all")
        vectors = distribution.gloss_vectors(base.dimensions, provider, walk, closed)
        frequency = distribution.document_frequency(vectors)
        loudest = sorted(frequency.items(), key=lambda item: (-item[1], item[0]))[:8]
        vocabulary[mode] = {
            "loudest": [[word, count, round(100 * count / len(base.dimensions), 1)]
                        for word, count in loudest],
            "pollution": distribution.junk_pollution(
                vectors, JUNK_WORDS, walk.min_shared,
                distribution.word_weights(vectors, walk),
            ),
        }
        print()
        print(f"  {mode}: loudest gloss words  "
              + "  ".join(f"{word} {share}%" for word, _count, share in vocabulary[mode]["loudest"]))
        print(f"  {mode}: pollution  only junk "
              f"{vocabulary[mode]['pollution']['pairs_only_junk_pct']}% of "
              f"{vocabulary[mode]['pollution']['overlapping_pairs']:,} overlapping pairs")

    return {
        "counts": {mode: built[mode].counts() for mode in modes},
        "membership_moved": primary != every,
        "only_primary": sorted(primary - every)[:200],
        "only_all": sorted(every - primary)[:200],
        "bar": {name: _reading_summary(reading) for name, reading in readings.items()},
        "vocabulary": vocabulary,
    }


# ------------------------------------------------------------------------------------------------
# the A/B — one base, two readings of whose lemma may speak
# ------------------------------------------------------------------------------------------------


def compare_lemma_scope(config: DictionaryConfig, closed=None) -> dict:
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


def compare_antonym_symmetry(config: DictionaryConfig, scope: str, closed=None) -> dict:
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
    _superseded_reading_notice("the antonym-symmetry comparison")
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
    has taken so far — the lemma scope, antonym symmetry, and T4's derivational down-weight.

    The two columns are LABELLED rather than named A and B in the code, because which reading is
    which is the Captain's business and this only counts.
    """
    _superseded_reading_notice("this comparison")
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
    parser.add_argument(
        "--senses",
        choices=("primary", "all"),
        default=None,
        help="reproduce a sense mode other than the one the rows declare. It moves MEMBERSHIP (the "
             "closure reads definitions), so it is a different base and not a different reading of "
             "one: measurable, never storable",
    )
    parser.add_argument(
        "--compare-senses",
        action="store_true",
        help="build the whole base twice — closure, R and D — under `primary` and under `all`, and "
             "report the two side by side (the Captain's parked question (a), 2026-08-25)",
    )
    parser.add_argument(
        "--compare-derivational",
        default=None,
        metavar="W,W,…",
        help="build R once per candidate `derivational` weight over ONE key space and report the "
             "bar at each (the E1 open item: land.n~land.v is FAR, cause.n~cause.v is NEAR, and "
             "today they are the same cell). Empty or `default` measures "
             + ",".join(f"{w:.2f}" for w in DOWN_WEIGHTS),
    )
    parser.add_argument(
        "--compare-weighting",
        action="store_true",
        help="build D twice over ONE key space, uniform against an idf-shaped down-weight on its "
             "gloss dimensions, and report both (the Captain's parked question (b), 2026-08-25)",
    )
    parser.add_argument(
        "--floors",
        action="store_true",
        help="measure the ACCEPTANCE FLOORS the bar would be scored against: where every pair sits "
             "in the population of all 9.9M pairs, what any single threshold can and cannot do, the "
             "(NEAR floor, FAR ceiling) frontier with an abstention band, and what a candidate "
             "floor actually admits. Measures candidates and declares nothing — the floors are the "
             "Captain's, and they land in `ReadingPolicy` beside the mix when he has ruled",
    )
    parser.add_argument(
        "--walk",
        action="append",
        default=[],
        metavar="NAME=VALUE",
        help="reproduce a gloss walk other than the one the rows declare, one parameter at a time "
             "(e.g. --walk scale=1 --walk cap=1 for a plain Jaccard, or --walk measure=dice). The "
             "names are the `distribution` policy rows; a walk the rows did not declare is a "
             "measurement and may not be stored",
    )
    parser.add_argument(
        "--mix",
        type=float,
        default=None,
        help="reproduce a dual read other than the one the rows declare: D's columns are scaled by "
             "this, the two rows are concatenated and one cosine is taken over the whole vector. "
             "Default: whatever policy v7 says (0.5, the Captain's ruling of 2026-09-09). THERE IS "
             "NO FALLBACK — a policy that declares no mix and a run that names none is a refusal, "
             "never a silent 1.0. A blend the rows did not declare may be measured and not stored",
    )
    parser.add_argument(
        "--senses-layer",
        action="store_true",
        help="also place every SENSE against the base — the dictionary's second floor (E1c). "
             "120,475 senses, about four minutes, and the base itself is unchanged by it: the "
             "layer rides ON the dimensions and is never square",
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
    # The closed classes reach D only when the policy asks for them; read either way so the header
    # can say WHICH table a `compiled` reading was taken against.
    structure_forms, structure_source = closed_forms(args.db)
    structure_forms = frozenset(structure_forms)

    print("=" * 96)
    print("BUILD THE BASE — declared before measuring")
    print("=" * 96)
    print(f"policy        {policy_source}")
    print(f"              {config.closure}")
    print(f"bar           {bar_source}, {len(bar)} pairs ({len(bar_words(bar))} words)")
    if config.distribution is not None:
        reading = config.distribution.structure
        if reading == "compiled":
            print(f"structure     COMPILED — {len(structure_forms)} closed-class forms leave D's "
                  f"vocabulary ({structure_source})")
        else:
            print("structure     ADMITTED — a closed-class form counts like any other shared word")
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
    print(f"dual read     mix {config.reading.mix if config.reading else '(not declared by these rows)'}")
    print()
    print(f"config fingerprint   {config.fingerprint()}")
    print(f"policy fingerprint   {policy.policy_fingerprint(rows)}")
    print(f"bar fingerprint      {policy.bar_fingerprint(bar_rows)}")
    print()

    # THE MIX COMES FROM THE ROWS (policy v7), and there is NO fallback: an undeclared mix is a
    # refusal, exactly as an undeclared lemma scope is. The round 1.0 this tool printed for a
    # fortnight was a measurement's convenience, and the day it was ruled it stopped being available
    # as a default — a reading nobody declared must not be able to reach a manifest.
    declared_mix = config.reading.mix if config.reading is not None else None
    mix = args.mix if args.mix is not None else declared_mix
    if mix is None:
        print("REFUSED: this policy version declares no dual read, so nothing says how loudly D "
              "speaks. Policy v7 (db/0010) declares it; to reproduce another blend, name it with "
              "--mix (and it cannot be stored).")
        return 2
    if args.apply and mix != declared_mix:
        print(f"REFUSED: --mix {mix} is not what the rows declare ({declared_mix}). A stored base "
              f"must be the one its config fingerprint describes; a blend the rows do not declare "
              f"is a measurement.")
        return 2
    if args.mix is not None and mix != declared_mix:
        if config.reading is not None:
            config = config.with_reading(mix=mix)
        print(f"dual read     MIX {mix}  — a reading nobody has ruled; measurable, never storable")
        print(f"config fingerprint   {config.fingerprint()}   (the variant's, not the rows')")
        print()

    if args.walk:
        if config.distribution is None:
            print("REFUSED: this policy declares no gloss walk, so there is nothing to vary. "
                  "Policy v6 (db/0009) is what declares it.")
            return 2
        try:
            changes = _walk_overrides(args.walk, config.distribution)
        except ValueError as error:
            print(f"REFUSED: {error}")
            return 2
        if args.apply:
            print(f"REFUSED: --walk {sorted(changes)} is not what the rows declare. A stored base "
                  f"must be the one its config fingerprint describes; a walk the rows do not "
                  f"declare is a measurement.")
            return 2
        config = config.with_distribution(**changes)
        print(f"gloss walk    {config.distribution}")
        print("              a walk nobody has ruled — measurable, never storable")
        print(f"config fingerprint   {config.fingerprint()}   (the variant's, not the rows')")
        print()

    if args.senses is not None:
        if args.compare_senses:
            print("REFUSED: --compare-senses measures both modes; naming one with --senses would "
                  "be an argument with the measurement it is asking for.")
            return 2
        if args.apply and args.senses != config.closure.senses:
            print(f"REFUSED: --senses {args.senses!r} is not what the rows declare "
                  f"({config.closure.senses!r}). It moves MEMBERSHIP, so it is a different base "
                  f"entirely; a stored base must be the one its config fingerprint describes.")
            return 2
        # BOTH cuts move together: the closure's decides which senses write a definition for
        # MEMBERSHIP, D's decides which write one for the GEOMETRY, and a run that moved one alone
        # would be measuring a policy nobody has proposed.
        config = config.with_closure(senses=args.senses)
        if config.distribution is not None:
            config = config.with_distribution(senses=args.senses)
        print(f"senses        {args.senses.upper()}  — a base nobody has ruled; membership moves "
              f"with it, and it may not be stored")
        print(f"config fingerprint   {config.fingerprint()}   (the variant's, not the rows')")
        print()

    if args.compare_derivational is not None:
        if args.apply:
            print("REFUSED: --compare-derivational is a MEASUREMENT of candidate weights, and only "
                  "one of them is the standing law.")
            return 2
        scope = args.lemma_scope or config.relations.lemma_scope
        if scope is None:
            print("REFUSED: no lemma scope declared and none named — see --lemma-scope.")
            return 2
        named = [w.strip() for w in args.compare_derivational.split(",") if w.strip()]
        candidates = DOWN_WEIGHTS if not named or named == ["default"] else tuple(
            float(w) for w in named
        )
        measured = report_derivational(
            compare_derivational(config, scope, candidates, structure_forms), config, mix
        )
        print()
        print(f"measured in {time.time() - started:.0f}s")
        _write_json(args.json, {"policy_source": policy_source, "lemma_scope": scope,
                                "derivational": measured})
        return 0

    if args.floors:
        if args.apply:
            print("REFUSED: --floors MEASURES candidate floors. None of them is declared, and a "
                  "build cannot be stored under a reading nobody has ruled.")
            return 2
        if config.distribution is None:
            print("REFUSED: this policy declares no gloss walk, so there is no dual read to set a "
                  "floor on. Policy v6 (db/0009) is what declares D.")
            return 2
        scope = args.lemma_scope or config.relations.lemma_scope
        if scope is None:
            print("REFUSED: no lemma scope declared and none named — see --lemma-scope.")
            return 2
        curated, curated_source = standing_curated_edges(args.db)
        print(f"curated       {curated_source}")
        built, provider = build_base(config, scope, args.antonym_symmetry, closed=structure_forms,
                                 with_senses=args.senses_layer, curated_edges=curated)
        vectors = distribution.gloss_vectors(
            built.dimensions, provider, config.distribution, structure_forms
        )
        measured = report_floors(built, config, vectors, mix)
        print()
        print(f"measured in {time.time() - started:.0f}s")
        _write_json(args.json, {"policy_source": policy_source, "bar_source": bar_source,
                                "lemma_scope": scope, "floors": measured})
        return 0

    if args.compare_weighting:
        if args.apply:
            print("REFUSED: --compare-weighting is a MEASUREMENT of two readings of D's "
                  "dimensions, and one of them is not the standing law.")
            return 2
        if config.distribution is None:
            print("REFUSED: this policy declares no gloss walk, so there is no D to weight. "
                  "Policy v6 (db/0009) is what declares it.")
            return 2
        scope = args.lemma_scope or config.relations.lemma_scope
        if scope is None:
            print("REFUSED: no lemma scope declared and none named — see --lemma-scope.")
            return 2
        measured = report_weighting(compare_weighting(config, scope, structure_forms), config, mix)
        print()
        print(f"measured in {time.time() - started:.0f}s")
        _write_json(args.json, {"policy_source": policy_source, "lemma_scope": scope,
                                "weighting": measured})
        return 0

    if args.compare_senses:
        if args.apply:
            print("REFUSED: --compare-senses builds TWO BASES over two key spaces. Neither of them "
                  "is a build of the standing policy, and one of them is not the standing law.")
            return 2
        scope = args.lemma_scope or config.relations.lemma_scope
        if scope is None:
            print("REFUSED: no lemma scope declared and none named — see --lemma-scope.")
            return 2
        from tk2.dictionary.wordnet import WordNetProvider as _P

        measured = report_senses(
            compare_senses(config, scope, structure_forms), config,
            _P(wordnet_lexicon(), lemma_scope=scope), mix, structure_forms
        )
        print()
        print(f"measured in {time.time() - started:.0f}s")
        _write_json(args.json, {"policy_source": policy_source, "lemma_scope": scope,
                                "senses": measured})
        return 0

    if args.compare_antonym_symmetry:
        if args.apply:
            print("REFUSED: --compare-antonym-symmetry is a MEASUREMENT of three readings, and two "
                  "of them are not the standing law.")
            return 2
        scope = args.lemma_scope or config.relations.lemma_scope
        if scope is None:
            print("REFUSED: no lemma scope declared and none named — see --lemma-scope.")
            return 2
        measured = report_symmetry(compare_antonym_symmetry(config, scope, structure_forms), config)
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
        comparison = compare_lemma_scope(config, structure_forms)
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
    # THE APPROVED EDGES, read as INPUTS. Offline runs carry none and say so; a run against a
    # database carries every standing approval, and refuses if one of them cannot be placed.
    curated, curated_source = standing_curated_edges(args.db)
    print(f"curated       {curated_source}")
    built, provider = build_base(config, scope, args.antonym_symmetry, closed=structure_forms,
                                 with_senses=args.senses_layer, curated_edges=curated)
    stats = report_shape(built.relational)
    d_stats = None
    dual = None
    if built.distributional is None:
        print()
        print("D — NOT BUILT: this policy version declares no gloss walk, so there is nothing to "
              "build it from. Policy v6 (db/0009) is what declares it.")
    else:
        # Computed once and handed to both readings: the vocabulary D's cells are made of is the
        # answer to the parked weighting question AND the evidence behind every bar pair, and two
        # derivations of it would be two chances to report one and measure the other.
        vectors = distribution.gloss_vectors(
            built.dimensions, provider, config.distribution, structure_forms
        )
        d_stats = report_distribution(built, vectors, config)
    bar_reading = report_bar(built.relational, config.bar)
    reading = report_reading(built, config)
    if args.mix is not None and built.distributional is not None:
        # A NAMED mix is a measurement of a reading nobody has ruled, and the blend sweep is the
        # instrument for exactly that. It is no longer printed by default: policy v11 abolished the
        # blend, and a default report that scored one was the misleading half of this tool.
        dual = report_dual(built, config, vectors, mix_columns(mix), standing=mix)
    counts = built.counts()

    build_label = args.build or config.fingerprint()[:12]
    manifest = policy.manifest_row(
        config,
        rows,
        bar_rows,
        counts=counts,
        authorization=args.authorized or "(unauthorized — dry run)",
        note=args.note,
        build=build_label,
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
                    "mix": mix,
                    "r": stats,
                    "d": d_stats,
                    "bar": bar_reading,
                    "reading": reading,
                    "dual": dual,
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

    return _apply(args, built, manifest, build_label)


def _walk_overrides(named, walk) -> dict:
    """`name=value` arguments read against the walk's own fields, typed by what is already there.

    Typed from the DECLARATION rather than from a table here, so a parameter added to the policy is
    overridable the day it exists and a name that is not a parameter is refused rather than silently
    added to a dataclass that has no room for it.
    """
    changes: dict = {}
    for argument in named:
        name, _, value = argument.partition("=")
        name = name.strip()
        if not hasattr(walk, name):
            raise ValueError(
                f"{name!r} is not a parameter of the gloss walk. They are "
                f"{[f.name for f in fields(walk)]}."
            )
        current = getattr(walk, name)
        changes[name] = type(current)(value.strip()) if not isinstance(current, str) else value.strip()
    return changes


def _write_json(path, payload) -> None:
    """The measurement, whole, beside what was printed. Here rather than five times over: every
    comparison writes the same document shape, and five copies of `json.dumps` is five chances for
    one of them to lose a field nobody notices is missing."""
    if not path:
        return
    Path(path).write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8"
    )
    print(f"wrote {path}")


def _apply(args, built: build.BaseBuild, manifest, build_label: str) -> int:
    """The write. Everything above this line is a measurement; this is the only part that lands.

    BOTH MATRICES, under one build label and one key registry — the store writes the dimension order
    first and refuses a second matrix that disagrees with it, which is what makes «R and D are over
    one key space» a checked property rather than a promise.

    AND EACH ONE SEALED (T5). D is 218 MB across a network; the store chunks it, counts the rows
    back out of the database and only then writes the row that says the matrix is whole. An
    interruption here therefore leaves a base that DOES NOT READ rather than one that reads wrong,
    and the recovery is to run this command again. The manifest row is written last of all, after
    both seals — so a manifest row in the ledger means the base under it was complete when it was
    made, which is the claim the whole ledger rests on.
    """
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
    print()
    for built_matrix in (built.relational, built.distributional):
        if built_matrix is None:
            continue
        started = time.time()

        def say(chunk: int, chunks: int, rows: int, name=built_matrix.name, at=started) -> None:
            print(f"  {name}  chunk {chunk:>3}/{chunks:<3} {rows:>6,} rows "
                  f"({time.time() - at:.0f}s)", flush=True)

        written = store.write(built_matrix, build_label, progress=say)
        sealed = store.seal(build_label, built_matrix.name)
        print(f"written: {args.db}.{built_matrix.name} build='{build_label}' — {written:,} rows, "
              f"{sealed['cells']:,} cells in {time.time() - started:.0f}s")
        print(f"         SEALED {sealed['fingerprint'][:16]}…  ({sealed['note']})")
    if built.senses is not None:
        started = time.time()

        def say_senses(chunk: int, chunks: int, rows: int, at=started) -> None:
            print(f"  {senses.SENSE_LAYER}  chunk {chunk:>3}/{chunks:<3} {rows:>7,} senses "
                  f"({time.time() - at:.0f}s)", flush=True)

        written = store.write_senses(built.senses, build_label, progress=say_senses)
        sealed = store.seal(build_label, senses.SENSE_LAYER)
        print(f"written: {args.db}.{senses.SENSE_LAYER} build='{build_label}' — {written:,} senses, "
              f"{sealed['cells']:,} cells in {time.time() - started:.0f}s")
        print(f"         SEALED {sealed['fingerprint'][:16]}…  ({sealed['note']})")

    MigrationWriter(db).insert(DictionaryBuildDoc, manifest)
    print(f"         one manifest row in {DictionaryBuildDoc.Settings.name}")
    print()
    print(f"VERIFY IT: PYTHONPATH=. ../.venv/bin/python tools/verify_base.py --db {args.db} "
          f"--build {build_label}")
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
