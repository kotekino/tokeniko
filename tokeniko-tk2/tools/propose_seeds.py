"""Propose the dictionary's seeds and simulate what each proposal closes to.

    PYTHONPATH=. ../.venv/bin/python tools/propose_seeds.py [--db NAME] [--json PATH]
    PYTHONPATH=. ../.venv/bin/python tools/propose_seeds.py --verify [--db NAME]

THE PROPOSE-AND-SIMULATE HALF of «grown generated-then-curated» (the standing law, 2026-08-25).
Approving is the Captain's hand and is not in this file; nothing here writes a row, reads a
password or touches the base. It measures, and it prints what it measured under.

POLICY BEFORE RESULTS (tooling req. 4), which for a proposal means three declarations made before
the first number is computed and printed at the head of every run:

  1. THE PURPOSE FAMILIES — read from the STANDING POLICY ROWS (the newest version in `--db`, or in
     the migration files when there is no body). They used to be declared here, in the tool, for the
     one run that existed to replace them; the moment the Captain ruled, a copy in code became a
     second declaration that could only ever go stale. What this tool re-argues is the STRUCTURAL
     half: the purpose rows are read, the structural rows are set aside, and every cut `k` is
     measured against the purpose set as it really stands.
  2. THE CLOSURE CUTS — read from the same rows, so the simulation runs under the depth the base is
     actually built at. The size cap is measured twice, under the standing value and under a rail
     far above it: since the 2026-08-25 ruling the two agree, and that they agree on words and keys
     while disagreeing on the fingerprint is exactly what «the cap is a rail, not a knob» means.
  3. THE EXCLUSIONS — the closed classes (rows, migration 0004) and the de-inflection guard
     (`tk2.dictionary.proposal.inflection_of`). What each removed is printed with its rank, because
     an exclusion is only as good as what it costs.

WHY IN-DEGREE. A word's in-degree in the definition digraph is the number of the lexicon's
definitions that name it, and the definitional core is what everything else is defined in terms of.
It is the resource arguing for itself, which is what makes it a second source rather than a second
opinion — and the first source (purpose) is precisely the argument the resource cannot make.

`--verify` IS THE OTHER JOB, and it is the reason a ruled policy may hold a materialised list at
all: it re-derives the standing structural seeds through the migration's own
`derive_structural_seeds()`, diffs them against the rows that were written down, then builds the
base from those rows and prints what it measured. A list that cannot be regenerated is a paste; this
is the command that says it is not.
"""

import argparse
import json
import sys
import time
from pathlib import Path

from tk2.dictionary import closure, glosses, policy, proposal
from tk2.dictionary.config import ClosurePolicy, DictionaryConfig, bar_words
from tk2.dictionary.wordnet import WordNetProvider, wordnet_lexicon

# ------------------------------------------------------------------------------------------------
# 1 — what is declared here, which is as little as possible
# ------------------------------------------------------------------------------------------------

#: The cuts of the structural ranking the Captain is asked to choose between. 0 is the control: the
#: purpose families alone, which is what the base would be if the resource were given no vote.
#: Whichever of them reproduces the standing rows is marked in the printed table — recognised by
#: what it derives to rather than by a number typed here, which is the same rule as everywhere else
#: in this file.
CUTS = (0, 50, 100, 200, 400)

#: Words watched into every simulated base by name. `right` is T1's own regression: at depth 2 it
#: sat exactly one ring outside a subset that already held `left`, the word that names it, and a
#: seed ruling that quietly loses it again should say so out loud.
NAMED_WATCH = ("right",)

#: A size cap set far above any intended base — «off» said as a number, so the run still has a cut
#: it could report having hit rather than a promise that it cannot.
RAIL = 1_000_000


# ------------------------------------------------------------------------------------------------
# 2 — where the rows come from
# ------------------------------------------------------------------------------------------------


def _migration(number: int):
    """Load a migration by number, as `tests/seed.py` does — the rows read off the file that will
    write them, so a proposal can be measured before the Captain's hand applies it."""
    from tk2.migrations import discover

    found = next((m for m in discover() if m.number == number), None)
    if found is None:
        raise SystemExit(f"no migration numbered {number:04d}")
    return found.load()


def _newest_policy_migration():
    """The migration file declaring the newest policy version — 0003 wrote v1, 0005 v2, and the next
    ruling will write the one after.

    Found by asking the files rather than by naming one: a tool that had a migration number in it
    would have to be edited every time the Captain rules, and the edit that got forgotten would make
    it quietly measure a superseded policy.
    """
    from tk2.migrations import discover

    best = None
    for found in discover():
        module = found.load()
        if hasattr(module, "POLICY_ROWS") and (
            best is None or module.POLICY_VERSION > best[1].POLICY_VERSION
        ):
            best = (found, module)
    if best is None:
        raise SystemExit("no migration declares POLICY_ROWS — there is no policy to read")
    return best


def standing_policy(db_name: str | None) -> tuple[list[dict], str]:
    """The policy rows AS THEY STAND, newest version only — live rows, or the migration's.

    Returns the source too, and prints it: a measurement whose inputs came from an unnamed place is
    not reproducible, and the whole difference between a proposal and an opinion is that one can be
    run again.
    """
    if db_name:
        from tk2.core.models import ALL_MODELS, DictionaryPolicyDoc
        from tk2.datatier import boot_datatier, traps

        boot_datatier(ALL_MODELS, db_name=db_name)
        rows = [r.model_dump() for r in traps.find_all(DictionaryPolicyDoc)]
        if not rows:
            raise SystemExit(f"{db_name} holds no policy rows — has migration 0003 been applied?")
        rows = policy.latest_version(rows)
        return rows, f"{db_name}.dictionary_policy v{policy.policy_version(rows)}"

    found, module = _newest_policy_migration()
    return (
        [dict(row) for row in module.POLICY_ROWS],
        f"db/{found.label} (policy v{module.POLICY_VERSION}, not read from a database)",
    )


def purpose_and_structure(rows) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """The two sources of the standing seed set, told apart by the family that argued for each.

    The purpose half is what this tool holds fixed; the structural half is what it re-argues at
    every `k`, so it is set aside rather than seeded — feeding the standing structural seeds back in
    as if they were purpose would make every cut measure the same thing.
    """
    seeds = policy.seed_rows(rows)
    purpose = tuple(r["name"] for r in seeds if r.get("family") != policy.FAMILY_STRUCTURE)
    structure = tuple(r["name"] for r in seeds if r.get("family") == policy.FAMILY_STRUCTURE)
    return purpose, structure


def closed_forms(db_name: str | None) -> tuple[tuple[str, ...], str]:
    """The closed-class forms to exclude — live rows if there are any, else migration 0004's.

    The fallback is not a convenience: on the day this proposal is measured 0004 has been WRITTEN
    and not applied, because applying it is the Captain's hand. The tool says which source spoke.
    """
    if db_name:
        from tk2.core.models import ClosedClassDoc
        from tk2.datatier import traps

        rows = [r.model_dump() for r in traps.find_all(ClosedClassDoc)]
        if rows:
            version = max(r["version"] for r in rows)
            forms = tuple(sorted({r["form"] for r in rows if " " not in r["form"]}))
            return forms, f"{db_name}.closed_classes v{version}"

    module = _migration(4)
    return module.FORMS, f"db/0004 v{module.VERSION} (not applied)"


# ------------------------------------------------------------------------------------------------
# 3 — the simulation
# ------------------------------------------------------------------------------------------------


def simulate(graph, provider, config: DictionaryConfig, watch=()) -> dict:
    """One candidate policy, run to a base. The numbers the ruling is made on.

    `keys` is counted through `dimensions_of` rather than by multiplying words by an average,
    because the POS split is the whole reason a word count and a dimension count are two different
    questions — and because the base-form rule (requirement 21) means some words mint none at all.

    `watch` is the honesty check on the two exclusions: they remove a word from the SEEDS, and a
    seed is a starting point, not a membership ruling. Handing in the words the exclusions removed
    answers «did they end up in the base anyway?» with a number instead of a reassurance.
    """
    result = closure.seed_closure(graph, config.seeds, config.closure)
    dimensions = glosses.dimensions_of(result.words, provider)
    expected = bar_words(config.bar)
    inside = set(result.words)
    return {
        "seeds": len(config.seeds),
        "missing_seeds": list(result.missing),
        "words": len(result.words),
        "keys": len(dimensions),
        "stopped": result.stopped,
        "one_ring_past": len(result.one_ring_past(graph)),
        "bar_words_inside": sum(1 for w in expected if w in inside),
        "bar_words": len(expected),
        "bar_missing": [w for w in expected if w not in inside],
        "watched_inside": sorted(w for w in watch if w in inside),
        "watched_outside": sorted(w for w in watch if w not in inside),
        "fingerprint": config.fingerprint()[:12],
    }


def run(db_name: str | None, out_path: Path | None) -> int:
    started = time.time()
    rows, policy_source = standing_policy(db_name)
    standing_closure = policy.closure_from_rows(rows)
    purpose_seeds, standing_structure = purpose_and_structure(rows)
    forms, forms_source = closed_forms(db_name)
    bar = policy.snapshot_bar()

    families: dict[str, list[str]] = {}
    for row in policy.seed_rows(rows):
        if row.get("family") != policy.FAMILY_STRUCTURE:
            families.setdefault(row.get("family") or "(none)", []).append(row["name"])

    print("=" * 96)
    print("SEED PROPOSAL — declared before measuring")
    print("=" * 96)
    print(f"standing policy   {policy_source}")
    print(f"                  {standing_closure}")
    print(f"closed classes    {forms_source} — {len(forms)} single-word forms excluded by principle")
    print(f"bar               v{policy.bar_snapshot()['version']}, {len(bar)} pairs "
          f"({len(bar_words(bar))} words, seeded by requirement 12)")
    print()
    print(f"PURPOSE, read from the rows ({len(purpose_seeds)} words)")
    for family, words in families.items():
        print(f"  {family:<12} {' '.join(words)}")
    print(f"STRUCTURE         in-degree over the whole digraph, cuts at k = {CUTS}")
    print(f"                  the rows already declare {len(standing_structure)} structural seeds; "
          f"they are set aside and re-argued here")
    print(f"                  size cap measured twice: standing {standing_closure.max_size:,} "
          f"and a rail at {RAIL:,}")
    print()

    # --- the digraph, once ----------------------------------------------------------------------
    lexicon = wordnet_lexicon()
    provider = WordNetProvider(lexicon)
    print(f"building the definition digraph over {len(lexicon):,} words…", flush=True)
    graph = closure.build_digraph(provider, standing_closure)
    stats = closure.digraph_stats(graph)
    print(f"  {stats['nodes']:,} nodes · {stats['edges']:,} edges · "
          f"mean out-degree {stats['mean_out_degree']:.1f} · {stats['silent']:,} silent "
          f"({time.time() - started:.0f}s)")
    print()

    ranking = proposal.structural_ranking(graph, provider, forms)
    clean = [c for c in ranking if c.is_candidate]
    rank_of = {c.word: i for i, c in enumerate(ranking, 1)}

    # --- what the ranking says ------------------------------------------------------------------
    print("=" * 96)
    print("THE CLEANED STRUCTURAL RANKING — top 100, what the Captain approves")
    print("=" * 96)
    print(f"{'#':>4}  {'word':<16} {'in-deg':>7}  {'dims':<8} gloss")
    for i, c in enumerate(clean[:100], 1):
        print(f"{i:>4}  {c.word:<16} {c.in_degree:>7}  {'/'.join(c.dimensions) or '—':<8} {c.gloss}")
    print()

    for reason, title in (
        (proposal.CLOSED_CLASS, "EXCLUDED BY PRINCIPLE — the closed classes, highest in-degree first"),
        (proposal.INFLECTION, "REMOVED BY THE DE-INFLECTION GUARD — highest in-degree first"),
    ):
        removed = proposal.excluded_head(ranking, reason, limit=40)
        print("=" * 96)
        print(title)
        print("=" * 96)
        for c in removed:
            rank = rank_of[c.word]
            share = f"{c.inflection_share:.2f}" if c.inflection_share is not None else "—"
            of = "/".join(c.inflection_of) or "—"
            print(f"{rank:>6}  {c.word:<16} {c.in_degree:>7}  of={of:<14} share={share:<6} {c.gloss}")
        print()

    # --- the simulation -------------------------------------------------------------------------
    print("=" * 96)
    print("THE SIMULATION — purpose ∪ bar ∪ structure(top k), under two size caps")
    print("=" * 96)
    header = (f"{'k':>5}  {'cap':>9}  {'seeds':>6}  {'words':>7}  {'keys':>7}  {'stopped':<10}"
              f"{'ring+1':>8}  {'bar in':>8}  fingerprint")
    print(header)
    # The exclusions' own honesty check: the words they took out of the running, watched through
    # every simulation. An exclusion that also cost MEMBERSHIP would be a much larger claim than the
    # one being made, and this is where that would show.
    watch = tuple(
        c.word
        for reason in (proposal.CLOSED_CLASS, proposal.INFLECTION)
        for c in proposal.excluded_head(ranking, reason, limit=40)
    ) + NAMED_WATCH

    rows: list[dict] = []
    for k in CUTS:
        extra = proposal.structural_seeds(ranking, k)
        for cap in (standing_closure.max_size, RAIL):
            cuts = ClosurePolicy(
                max_depth=standing_closure.max_depth,
                max_size=cap,
                senses=standing_closure.senses,
                extra_seeds=extra,
            )
            config = DictionaryConfig(closure=cuts, declared_seeds=purpose_seeds, bar=bar)
            measured = simulate(graph, provider, config, watch)
            measured["k"] = k
            measured["cap"] = cap
            measured["structural_seeds"] = list(extra)
            rows.append(measured)
            label = "standing" if cap == standing_closure.max_size else "rail"
            # Which cut the rows already hold, recognised by the seed SET it produces: the standing
            # structural rows are 200 minus the ones purpose had already claimed, so counting them
            # would answer 193 and match no k at all.
            mark = "  <- the standing rows" if (
                set(extra) | set(purpose_seeds) == set(standing_structure) | set(purpose_seeds)
            ) else ""
            print(f"{k:>5}  {label:>9}  {measured['seeds']:>6}  {measured['words']:>7,}  "
                  f"{measured['keys']:>7,}  {measured['stopped']:<10}"
                  f"{measured['one_ring_past']:>8,}  "
                  f"{measured['bar_words_inside']:>3}/{measured['bar_words']:<4}  "
                  f"{measured['fingerprint']}{mark}")
        print()

    print("=" * 96)
    print("WHAT THE EXCLUSIONS COST — the words they removed, watched into the base")
    print("=" * 96)
    print("An exclusion removes a word from the SEEDS. Whether it also removed it from the base is")
    print("a different question, and the only one that would be expensive to get wrong.")
    for row in rows:
        if row["cap"] != RAIL:
            continue
        outside = row["watched_outside"]
        named = "in" if all(w in row["watched_inside"] for w in NAMED_WATCH) else "OUT"
        print(f"  k={row['k']:<4} rail: {len(row['watched_inside'])}/{len(watch)} in the base anyway"
              f"   ({' '.join(NAMED_WATCH)}: {named})"
              f"   still out: {' '.join(outside) if outside else '(none)'}")
    print()

    missing = {w for row in rows for w in row["missing_seeds"]}
    if missing:
        print(f"SEEDS THE LEXICON DOES NOT HAVE: {' '.join(sorted(missing))}")
        print("  (reported, never silently dropped — requirement 15: membership is a defect too)")
        print()
    print(f"measured in {time.time() - started:.0f}s")

    if out_path is not None:
        out_path.write_text(
            json.dumps(
                {
                    "policy_source": policy_source,
                    "closed_class_source": forms_source,
                    "standing_closure": {
                        "max_depth": standing_closure.max_depth,
                        "max_size": standing_closure.max_size,
                        "senses": standing_closure.senses,
                    },
                    "purpose": {k: list(v) for k, v in families.items()},
                    "digraph": stats,
                    "ranking": [
                        {
                            "rank": i,
                            "word": c.word,
                            "in_degree": c.in_degree,
                            "dimensions": list(c.dimensions),
                            "excluded": c.excluded,
                            "inflection_of": list(c.inflection_of),
                            "inflection_share": c.inflection_share,
                            "gloss": c.gloss,
                        }
                        for i, c in enumerate(ranking[:1000], 1)
                    ],
                    "watched": list(watch),
                    "simulation": rows,
                },
                indent=2,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"wrote {out_path}")
    return 0


# ------------------------------------------------------------------------------------------------
# 4 — the verification: the written-down list, re-derived, and the base it really produces
# ------------------------------------------------------------------------------------------------


def standing_bar(db_name: str | None):
    """The bar as it stands — the database's rows if there are any, else the pinned snapshot.

    Both are returned as ROWS as well as pairs, because the fingerprint is taken over rows and the
    whole point of printing it is that it can be compared with a manifest's.
    """
    if db_name:
        from tk2.core.models import DictionaryBarDoc
        from tk2.datatier import traps

        rows = [r.model_dump() for r in traps.find_all(DictionaryBarDoc)]
        if rows:
            return policy.bar_from_rows(rows), rows, f"{db_name}.dictionary_bar v{policy.bar_version(rows)}"

    document = policy.bar_snapshot()
    return policy.snapshot_bar(), document["pairs"], f"bar_snapshot.json v{document['version']}"


def verify(db_name: str | None) -> int:
    """Re-derive the standing structural seeds, diff them against the rows, and rebuild the base.

    Three claims, checked in the order they can fail:

      1. THE LIST IS DERIVED. `derive_structural_seeds()` re-runs the ranking from the resource and
         must return exactly what the migration wrote down — word, rank and in-degree.
      2. THE ROWS ARE THAT LIST. A correct literal written into the rows incorrectly is the second
         failure, and it is invisible to the first check.
      3. THE BASE IS WHAT WAS RULED ON. The closure is run from the standing rows and the numbers
         are printed: words, keys, why it stopped, the bar inside it, and all three fingerprints.
    """
    started = time.time()
    rows, policy_source = standing_policy(db_name)
    found, module = _newest_policy_migration()
    bar, bar_rows, bar_source = standing_bar(db_name)

    print("=" * 96)
    print("VERIFY — the standing policy, re-derived and re-measured")
    print("=" * 96)
    print(f"policy       {policy_source}")
    print(f"derivation   db/{found.label}.derive_structural_seeds(k={module.STRUCTURAL_K})")
    print(f"bar          {bar_source}")
    print()

    if module.POLICY_VERSION != policy.policy_version(rows):
        print(f"  ! the rows are policy v{policy.policy_version(rows)} and the derivation lives in "
              f"a file declaring v{module.POLICY_VERSION} — one of the two is behind")
        return 1

    # --- 1. the list is derived ------------------------------------------------------------------
    print(f"re-deriving {module.STRUCTURAL_K} structural seeds from the resource…", flush=True)
    derived = module.derive_structural_seeds()
    written = tuple(tuple(entry) for entry in module.STRUCTURAL_SEEDS)
    if derived != written:
        print(f"  ! the derivation and the written list DISAGREE ({time.time() - started:.0f}s)")
        for position, (a, b) in enumerate(zip(derived, written), 1):
            if a != b:
                print(f"    at position {position}: derived {a}, written {b}")
        if len(derived) != len(written):
            print(f"    lengths differ: derived {len(derived)}, written {len(written)}")
        return 1
    print(f"  OK {len(derived)} seeds, identical to the list written down — rank and in-degree too "
          f"({time.time() - started:.0f}s)")

    # --- 2. the rows are that list ---------------------------------------------------------------
    declared = policy.seeds_from_rows(rows)
    missing = [word for word, _rank, _degree in derived if word not in declared]
    if missing:
        print(f"  ! derived seeds that no row declares: {' '.join(missing)}")
        return 1
    structural_rows = [r for r in policy.seed_rows(rows) if r.get("family") == policy.FAMILY_STRUCTURE]
    print(f"  OK every one of them is a declared seed ({len(structural_rows)} rows carry the "
          f"`{policy.FAMILY_STRUCTURE}` family; the rest were already purpose seeds)")
    print()

    # --- 3. the base is what was ruled on --------------------------------------------------------
    config = DictionaryConfig(
        closure=policy.closure_from_rows(rows),
        declared_seeds=declared,
        bar=bar,
    )
    print(f"building the base under {config.closure}…", flush=True)
    lexicon = wordnet_lexicon()
    provider = WordNetProvider(lexicon)
    graph = closure.build_digraph(provider, config.closure)
    measured = simulate(graph, provider, config, NAMED_WATCH)

    print()
    print(f"  lexicon        {len(lexicon):,} words")
    print(f"  seeds          {measured['seeds']}  (declared {len(declared)} + the bar's own words)")
    print(f"  words          {measured['words']:,}")
    print(f"  keys           {measured['keys']:,}")
    print(f"  stopped        {measured['stopped']}"
          f"{'   <- THE CAP BOUND: it is not a rail' if measured['stopped'] == 'size' else ''}")
    print(f"  one ring past  {measured['one_ring_past']:,}")
    print(f"  bar inside     {measured['bar_words_inside']}/{measured['bar_words']}"
          f"{'   missing: ' + ' '.join(measured['bar_missing']) if measured['bar_missing'] else ''}")
    print(f"  {' '.join(NAMED_WATCH)}          "
          f"{'in' if measured['watched_inside'] else 'OUT'}")
    if measured["missing_seeds"]:
        print(f"  ! seeds the lexicon does not have: {' '.join(measured['missing_seeds'])}")
    print()
    print(f"  config fingerprint   {config.fingerprint()}")
    print(f"  policy fingerprint   {policy.policy_fingerprint(rows)}")
    print(f"  bar fingerprint      {policy.bar_fingerprint(bar_rows)}")
    print()
    print(f"verified in {time.time() - started:.0f}s")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="propose the dictionary's seeds and simulate them")
    parser.add_argument(
        "--db",
        default=None,
        help="read the standing policy and the closed classes from this database's rows "
             "(default: from the migration files, which needs no body)",
    )
    parser.add_argument("--json", default=None, help="also write the whole measurement here")
    parser.add_argument(
        "--verify",
        action="store_true",
        help="re-derive the standing structural seeds, diff them against the rows, and rebuild the "
             "base from them (no proposal, no sweep)",
    )
    args = parser.parse_args(argv)

    try:
        if args.verify:
            return verify(args.db)
        return run(args.db, Path(args.json) if args.json else None)
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
