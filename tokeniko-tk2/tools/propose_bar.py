"""Propose new pairs for the acceptance bar, and say where every one of them came from.

    PYTHONPATH=. ../.venv/bin/python tools/propose_bar.py [--db NAME] [--json PATH]
    PYTHONPATH=. ../.venv/bin/python tools/propose_bar.py --per-class 12 --seed 20260910

THE PROPOSE HALF of «grown generated-then-curated» (the standing law, 2026-08-25), applied to the
BAR. Eighteen pairs is a draft and the Captain has said so; this is how the nineteenth is found —
generated from the resource and the standing policy, curated by a hand, approved by his. Approving
is not in this file and neither is writing a row: bar v2 is a migration, and it is written after the
ruling, never before it.

**WHAT THIS FILE IS NOT ALLOWED TO SEE, and how the prohibition is kept.** «New pairs are added only
BEFORE a run» — a pair proposed after seeing what the base says about it is not an expectation, it
is a description. So this tool builds NO matrix and reads NO reading: it imports the resource, the
closure and the standing rows, and nothing at all from `relations`, `distribution` or `matrix`. The
one thing it asks the resource about a pair is whether an edge EXISTS between the two keys, which is
WordNet's own statement and sits upstream of every weight, the mix and the floors alike. It never
asks how strong, never asks what R made of it, and cannot ask what either matrix reads: a candidate
here is proposed by the CLASS it was generated in and by nothing that a build has measured.

**THE CLASSES ARE THE ARGUMENT.** A bar pair is worth having when its verdict comes from outside the
resource — otherwise the base is being tested against the thing it was mined from, and it will pass
by construction. So the classes below are chosen for what each puts at risk (`why` says it, and the
`why` travels into the row verbatim, because a bar whose reasons are lost is a bar nobody can argue
with):

  `opposition`    the resource STATES the antonymy, so R will state a negative cell — and the pair
                  is still worth its place, because the risk is not R's: it is the DUAL READ burying
                  the sign under a gloss overlap (`enter~leave` turns positive at mix 1.0). A sign
                  witness, and the standing bar has two.
  `collapse`      one word, two parts of speech, a derivation stated between them. The verdict is
                  the meaning's and the resource cannot supply it — `land.n~land.v` is FAR and
                  `cause.n~cause.v` is NEAR over the identical cell — so every one of these is a
                  question only a reader can answer, which is exactly what a bar is for.
  `family`        two words of ONE declared purpose family with no stated relation between their
                  keys. The class the standing bar fails in (`eat~food`, `sleep~bed`): what R cannot
                  say at all and D has to carry alone. The highest-yield class there is.
  `cross_family`  two words from DIFFERENT purpose families, no stated relation. Proposed FAR: the
                  families are supposed to be separable, and nothing has ever tested that they are.
  `sibling`       two keys under one immediate hypernym, no direct edge — `walk~run`'s own shape.
  `control`       a UNIFORMLY RANDOM pair of base keys, drawn from a stated seed. The class T5's
                  floor measurement says the base most needs: a candidate NEAR floor admits 8.9% of
                  all pairs, so a random pair is a coin toss the geometry should be losing and the
                  standing bar has only three witnesses to it.
  `inflection`    two keys whose words are inflections of one another (requirement 21's own defect,
                  the `left` class). Generated and reported; whether a NEAR/FAR bar is the right
                  instrument for it is a question for the Captain, not an answer from here.

The proposed verdict is the CLASS's, uniformly and mechanically — `family` and `sibling` propose
NEAR, `cross_family` and `control` propose FAR, and `collapse` proposes nothing at all. That is
deliberate: a generator that guessed per pair would be curating, and the curation is a separate act
performed by a hand that can be argued with.
"""

import argparse
import json
import random
import sys
import time
from collections import defaultdict
from pathlib import Path

from tk2.datatier.policy_source import standing_bar, standing_policy
from tk2.dictionary import closure, glosses, keys, policy
from tk2.dictionary.wordnet import WordNetProvider, wordnet_lexicon

#: How many candidates of each class are printed when the run is given no number. Enough to curate
#: from, few enough to read — the curation is the expensive half and it is done by eye.
PER_CLASS = 10

#: The sampler's seed. Stated rather than left to the clock for the reason the whole file exists:
#: a proposal that cannot be reproduced is an opinion, and a reviewer has to be able to re-draw the
#: same controls and see that they were not fished for.
SEED = 20260910

#: How much of a gloss is printed as evidence. A curator rules on the MEANING, so the definition has
#: to be in front of him; a full gloss makes the table unreadable and the first clause is the claim.
GLOSS_SHOWN = 64

#: The verdict a class proposes, or `None` where the class exists precisely because the resource
#: cannot supply one.
CLASS_VERDICT = {
    "opposition": "FAR",
    "collapse": None,
    "family": "NEAR",
    "cross_family": "FAR",
    "sibling": "NEAR",
    "control": "FAR",
    "inflection": None,
}

#: What each class puts at risk, in the sentence that would travel into the row's `why`.
CLASS_WHY = {
    "opposition": "the resource states the opposition; the risk is the dual read burying the sign",
    "collapse": "one word, two parts of speech, one stated derivation — the verdict is the meaning's",
    "family": "one purpose family, no stated relation: what R cannot say and D must carry alone",
    "cross_family": "two purpose families, no stated relation: the families must stay separable",
    "sibling": "co-hyponyms of one immediate hypernym, no direct edge — walk~run's own shape",
    "control": "a uniformly random pair of dimensions; the geometry must not call it near",
    "inflection": "two keys that are one word's inflections — requirement 21's own defect class",
}


# ------------------------------------------------------------------------------------------------
# what the resource states between two keys — the ONE thing this tool may ask about a pair
# ------------------------------------------------------------------------------------------------


def stated_edges(dimensions, provider) -> dict[str, dict[str, set[str]]]:
    """`key -> other key -> the relations WordNet states between them`, over the base's dimensions.

    The same walk R's builder performs, stopped one step early: it resolves a relation's target
    senses to the dimensions that speak them and records the relation's NAME. No weight is read, no
    precedence is resolved, no cell is made. That is the line this file keeps — see the head.
    """
    speakers: dict[str, set[str]] = defaultdict(set)
    for key in dimensions:
        for sense in provider.senses_of_key(key):
            speakers[sense].add(key)

    edges: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))

    # SYNONYMY IS AN EDGE and it is not in `relations_of_key`: two dimensions that speak the SAME
    # sense are what synonymy is (`relations._speakers_of_sense`), and a generator that missed it
    # would keep proposing `talking.n ~ talk.n` as a pair the resource says nothing about.
    for sense, spoken in speakers.items():
        spoken = sorted(spoken)
        for i, key in enumerate(spoken):
            for other in spoken[i + 1:]:
                edges[key][other].add("synonym")
                edges[other][key].add("synonym")

    for key in dimensions:
        for relation, senses in provider.relations_of_key(key).items():
            for sense in senses:
                for other in speakers.get(sense, ()):
                    if other == key:
                        continue
                    edges[key][other].add(relation)
                    edges[other][key].add(relation)
    return edges


def hypernym_groups(dimensions, provider) -> dict[str, set[str]]:
    """`an immediate hypernym sense -> the dimensions under it`. The sibling class's generator."""
    groups: dict[str, set[str]] = defaultdict(set)
    for key in dimensions:
        stated = provider.relations_of_key(key)
        for sense in stated.get("hypernym_1", ()):
            groups[sense].add(key)
    return groups


# ------------------------------------------------------------------------------------------------
# the classes
# ------------------------------------------------------------------------------------------------


def candidates(dimensions, provider, families: dict[str, str], edges, standing: set,
               rng: random.Random, per_class: int) -> dict[str, list[dict]]:
    """Every class, generated and sampled. Order within a class is the sampler's, not the base's.

    `standing` holds the pairs the bar already declares, in both directions: a candidate that is
    already an expectation is not a candidate, and a tool that could re-propose one would let a pair
    change its verdict by being proposed twice.
    """
    by_word: dict[str, list[str]] = defaultdict(list)
    for key in dimensions:
        by_word[keys.word_of(key)].append(key)
    in_base = set(dimensions)

    def free(a: str, b: str) -> bool:
        """The pair is available AND the resource states nothing between the two keys."""
        return (a, b) not in standing and (b, a) not in standing and not edges.get(a, {}).get(b)

    found: dict[str, list[tuple]] = {name: [] for name in CLASS_VERDICT}

    # opposition — a stated antonymy between two dimensions
    for key, others in edges.items():
        for other, relations in others.items():
            if key < other and "antonym" in relations and (key, other) not in standing \
                    and (other, key) not in standing:
                found["opposition"].append((key, other, "antonym stated by the resource"))

    # collapse — one word, two parts of speech, a derivation stated between them
    for word, spellings in by_word.items():
        for i, key in enumerate(spellings):
            for other in spellings[i + 1:]:
                if (key, other) in standing or (other, key) in standing:
                    continue
                if "derivational" in edges.get(key, {}).get(other, set()):
                    found["collapse"].append((key, other, "one word, two POS, derivation stated"))

    # family / cross_family — the declared purpose families, over keys with no stated relation
    seeded = [(key, families[keys.word_of(key)]) for key in dimensions
              if keys.word_of(key) in families]
    for i, (key, family) in enumerate(seeded):
        for other, other_family in seeded[i + 1:]:
            if keys.word_of(key) == keys.word_of(other) or not free(key, other):
                continue
            if family == other_family:
                found["family"].append((key, other, f"both declared {family}"))
            else:
                found["cross_family"].append((key, other, f"{family} against {other_family}"))

    # sibling — two dimensions under one immediate hypernym, no direct edge
    for sense, members in hypernym_groups(dimensions, provider).items():
        members = sorted(members)
        if not 2 <= len(members) <= 8:      # a hypernym with fifty children is a category, not a pair
            continue
        for i, key in enumerate(members):
            for other in members[i + 1:]:
                if free(key, other):
                    found["sibling"].append((key, other, f"both under {sense}"))

    # control — uniformly random, and the draw is the evidence
    pool = sorted(in_base)
    while len(found["control"]) < per_class * 3:
        key, other = rng.choice(pool), rng.choice(pool)
        if key != other and free(key, other) and keys.word_of(key) != keys.word_of(other):
            found["control"].append((key, other, "drawn at random from the dimension list"))

    # inflection — two keys whose words are one another's inflections
    for word, _ in by_word.items():
        for pos in ("n", "v", "a", "r"):
            lemma = provider.lemma(word, pos)
            if not lemma or lemma == word or lemma not in by_word:
                continue
            for key in by_word[word]:
                for other in by_word[lemma]:
                    if free(key, other):
                        found["inflection"].append((key, other, f"{word} lemmatises to {lemma}"))

    out: dict[str, list[dict]] = {}
    for name, rows in found.items():
        rng.shuffle(rows)
        seen: set[tuple[str, str]] = set()
        picked = []
        for a, b, evidence in rows:
            if (a, b) in seen or (b, a) in seen:
                continue
            seen.add((a, b))
            picked.append({
                "class": name,
                "a": a,
                "b": b,
                "verdict": CLASS_VERDICT[name],
                "evidence": evidence,
                "why": CLASS_WHY[name],
                "gloss_a": _short(provider.gloss_of_key(a)),
                "gloss_b": _short(provider.gloss_of_key(b)),
                "stated": sorted(edges.get(a, {}).get(b, ())),
            })
            if len(picked) >= per_class:
                break
        out[name] = picked
    return out


def _short(gloss: str) -> str:
    gloss = " ".join(gloss.split())
    return gloss if len(gloss) <= GLOSS_SHOWN else gloss[:GLOSS_SHOWN - 1] + "…"


# ------------------------------------------------------------------------------------------------
# the run
# ------------------------------------------------------------------------------------------------


def run(db_name: str | None, out_path: Path | None, per_class: int, seed: int) -> int:
    started = time.time()
    rows, policy_source = standing_policy(db_name)
    bar, bar_rows, bar_source = standing_bar(db_name)
    config = policy.config_from_rows(rows, bar_rows)

    print("=" * 96)
    print("PROPOSE BAR PAIRS — generated from the resource, curated by a hand, approved by the Captain")
    print("=" * 96)
    print(f"policy        {policy_source}")
    print(f"bar           {bar_source}, {len(bar)} pairs standing  "
          f"(fingerprint {policy.bar_fingerprint(bar_rows)[:12]}…)")
    print(f"sampler       seed {seed}, {per_class} candidates per class")
    print("blindness     no matrix is built and no reading is taken here; the only question asked "
          "of a pair")
    print("              is whether the RESOURCE states an edge between the two keys")
    print()

    lexicon = wordnet_lexicon()
    provider = WordNetProvider(lexicon, lemma_scope=config.relations.lemma_scope)
    graph = closure.build_digraph(provider, config.closure)
    result = closure.seed_closure(graph, config.seeds, config.closure)
    dimensions = tuple(glosses.dimensions_of(result.words, provider))
    print(f"base          {len(result.words):,} words -> {len(dimensions):,} dimensions "
          f"({time.time() - started:.0f}s)")

    families = {row["name"]: row["family"] for row in policy.seed_rows(rows)
                if row.get("family") and row["family"] != policy.FAMILY_STRUCTURE}
    edges = stated_edges(dimensions, provider)
    print(f"resource      {sum(len(v) for v in edges.values()) // 2:,} stated edges between "
          f"dimensions · {len(families)} purpose-family words ({time.time() - started:.0f}s)")

    standing = {(pair.a, pair.b) for pair in bar}
    proposed = candidates(dimensions, provider, families, edges, standing,
                          random.Random(seed), per_class)

    for name, picked in proposed.items():
        verdict = CLASS_VERDICT[name]
        print()
        print("-" * 96)
        proposes = verdict or "NOTHING — the verdict is the meaning's"
        print(f"{name.upper():<14} proposes {proposes}    ({len(picked)} shown)")
        print(f"               {CLASS_WHY[name]}")
        print("-" * 96)
        for row in picked:
            print(f"  {row['a'] + ' ~ ' + row['b']:<28} {(verdict or '?'):<5} {row['evidence']}")
            print(f"    {row['a']:<14} {row['gloss_a']}")
            print(f"    {row['b']:<14} {row['gloss_b']}")

    print()
    print(f"proposed in {time.time() - started:.0f}s — {sum(len(v) for v in proposed.values())} "
          f"candidates over {len(proposed)} classes. NOTHING WAS WRITTEN: the curation is a hand's "
          f"and the approval is the Captain's.")

    if out_path:
        out_path.write_text(
            json.dumps(
                {
                    "policy_source": policy_source,
                    "bar_source": bar_source,
                    "bar_fingerprint": policy.bar_fingerprint(bar_rows),
                    "seed": seed,
                    "per_class": per_class,
                    "candidates": proposed,
                },
                indent=2,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"wrote {out_path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="propose candidate pairs for the acceptance bar")
    parser.add_argument("--db", default=None,
                        help="read the standing policy and bar from this database's rows "
                             "(default: the migration files, which needs no body)")
    parser.add_argument("--json", default=None, help="also write the whole proposal here")
    parser.add_argument("--per-class", type=int, default=PER_CLASS,
                        help=f"how many candidates of each class to show (default {PER_CLASS})")
    parser.add_argument("--seed", type=int, default=SEED,
                        help=f"the sampler's seed, so a proposal can be re-drawn (default {SEED})")
    args = parser.parse_args(argv)
    try:
        return run(args.db, Path(args.json) if args.json else None, args.per_class, args.seed)
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
