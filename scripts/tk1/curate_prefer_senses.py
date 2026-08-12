# ------------------------------------------------------------------------------------------------
# curate_prefer_senses.py — set the curated DEFAULT sense per (word,pos) (operator-gated curation).
#
# M3 (the third harvest, 2026-07-16): WordNet orders senses by corpus frequency, and for several
# everyday words that order contradicts the word's plain conversational reading — squid.n.01 is
# the FOOD, calculator.n.01 the PERSON — so the WSD frequency prior picks them honestly and
# wrongly whenever context is silent. The `preferred` flag on a dictionary row is the crew's
# ruling on the plain reading. The WSD ladder consults it AFTER Lesk (textual gloss evidence
# still wins — «I ate squid with lemon» can still reach the food sense) and BEFORE the context
# centroid (curated human data outranks sparse-vector co-occurrence guessing: the centroid ranked
# pisces.n.02, the FISH SIGN, above the actual fish at cosine 0.755).
#
# Idempotent: for each (word,pos) the flag is CLEARED on all rows first, then set on exactly the
# curated sense — re-running converges; changing a ruling here and re-applying moves the flag.
#
# Usage (from the repo root):
#   python scripts/tk1/curate_prefer_senses.py           # DRY RUN: report current vs curated
#   python scripts/tk1/curate_prefer_senses.py --apply   # write the flags
# ------------------------------------------------------------------------------------------------
import os
import sys

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", "tokeniko", ".env"))

# ---- the curation batch: (word, pos, preferred synset key) — the author's per-word rulings ------
BATCH = [
    ("squid",      "n", "squid.n.02"),       # the animal, not the Italian-cuisine food
    ("calculator", "n", "calculator.n.02"),  # the machine, not the expert person
    ("being",      "n", "organism.n.01"),    # a creature («human being»), not the state of existing
    ("form",       "n", "kind.n.01"),        # «a form of X» = a kind, not the phonological word-form
    ("live",       "v", "populate.v.01"),    # inhabit («I live in Japan»), not lead-a-lifestyle
    ("fish",       "n", "fish.n.01"),        # the animal — pins the pisces.n.02 centroid residual
    ("whale",      "n", "whale.n.02"),       # the cetacean (belt-and-braces; fix A already selects it)
    ("gill",       "n", "gill.n.04"),        # the respiratory organ (curated in via add batch 2)
    ("channel",    "n", "channel.n.05"),     # the communication channel (curated in via add batch 2)
    # batch 2 (the second-harvest strays, 2026-07-16 second session):
    ("bit",        "n", "bit.n.06"),         # the information unit («a coin stores bits» read the
                                             # fragment bit.n.02 context-less; Lesk still reaches
                                             # the fragment when the text supports it — «a bit of
                                             # cake». is_a unit_of_measurement.n.01 already in the
                                             # graph, so the definition grounds TRUE)

    # ---- BATCH 3 (the §2 microscope pass, 2026-08-10) -------------------------------------------
    # Harvested from the 43 `wrong-sense` leads in tkzipdebug (corpus 2026-07-17 → 08-09, i.e. all
    # POST-M3 and confirmed live by replay: «you are right!» still picks the direction of the sun).
    # The pattern is the same one M3 named — WordNet's corpus-frequency order contradicts the plain
    # conversational reading — and the lead counts show how concentrated it is: five words carry
    # half the cluster. Candidate pools span BOTH adjective codes ("ADJ": ["a","s"] in TKPosMapper),
    # so a ruling reaches a satellite sense from a head one and vice versa.
    ("right",      "a", "correct.a.01"),     # 6 LEADS. «you are right!» → the side of the body
                                             # toward the east. The single worst offender in the pass.
    ("property",   "n", "property.n.02"),    # 5 leads. «more than one property» = an attribute, not
                                             # a possession — and he reasons ABOUT properties, so
                                             # the ownership sense poisons the differentia rules.
    ("gold",       "n", "gold.n.03"),        # 4 leads. the metal, not «coins made of gold»
    ("think",      "v", "think.v.03"),       # 4 leads. cogitate — not «judge or regard». The wrong
                                             # one needs a complement, so «a machine thinks» limps.
    ("wrong",      "a", "incorrect.a.01"),   # 2 leads. mistaken, not «contrary to conscience»
    ("curious",    "a", "curious.a.02"),     # 2 leads. inquisitive, not «deviating from the usual»
    ("learning",   "n", "learning.n.01"),    # 2 leads. the process — not «profound scholarly
                                             # knowledge». He is BUILT to learn; the noun matters.
    ("base",       "v", "establish.v.08"),   # 2 leads. «based on past experience» = founded on,
                                             # not «situate as a center of operations»
    ("value",      "n", "value.n.02"),       # 2 leads. worth, not a computed numerical quantity
    ("wake",       "v", "wake_up.v.02"),     # 2 leads. «you woke up» is the transition, not the
                                             # stative «be awake» — and he wakes every day
    ("opposite",   "s", "opposite.s.03"),    # 2 leads. «the other one of a complementary pair» —
                                             # the antonymic reading, not «directly across, facing»
    ("trust",      "n", "reliance.n.01"),    # «what trust is» → the fiduciary property sense. NB:
                                             # reliance.n.01 glosses as «certainty based on past
                                             # experience», which is VERBATIM what he was taught on
                                             # 2026-08-09 — the curated pick and the KB now agree.
    ("cute",       "s", "cunning.s.01"),     # attractive by smallness/prettiness, not «contrived»
    ("sure",       "a", "certain.a.02"),     # «I'm sure» = confident, not «physically secure»
    ("thought",    "n", "idea.n.01"),        # «a nice thought» is one mental content, not the
                                             # organized beliefs of a period or group
    ("lot",        "n", "batch.n.02"),       # «a lot of notions» is a quantity, not a plot of land
    ("nice",       "a", "nice.a.01"),        # pleasant — not «socially or conventionally correct»
    ("salutation", "n", "greeting.n.01"),    # a spoken greeting, not the opening line of a LETTER
    ("make",       "v", "make.v.03"),        # «I made improvements» = cause to be, not «engage in»
    ("want",       "v", "desire.v.01"),      # «I wanted to be polite» = desire, not «have need of»
    ("person",     "n", "person.n.01"),      # a human being, not «a human body including clothing»

    # ---- BATCH 4 (§2 gerunds, 2026-08-11) -------------------------------------------------------
    # The `-ing` nominalization cluster: a gerund used as a bare predicate nominal («computing is
    # not thinking») reads as the ACTIVITY, but WordNet's frequency order hands over the FIELD of
    # study. Distinct from the VBG tagging problem in the same cluster (a `preferred` flag cannot
    # reach a noun sense the parser never puts in the candidate pool) — this entry only fixes the
    # words that DO arrive tagged NOUN.
    ("computing",  "n", "calculation.n.01"),  # «the procedure of calculating» — the activity, not
                                              # computer_science.n.01, the branch of engineering

    # ---- BATCH 5 (the modifier surface, 2026-08-12) — PROPOSED, awaiting the author's ruling -----
    # Residue of the property-path repair (the WSD ladder replacing the bare find_one, + the
    # prenominal-participle gate). These are WSD PICKS, not pool holes: in every row below the right
    # sense IS in the candidate pool and the ladder walks past it, so a `preferred` flag reaches it.
    # NB the pos code is the TARGET ROW's own — the script matches (word,pos) exactly, while the
    # ladder pools 'a' and 's' together, so an 's' ruling still reaches an 'a' query.
    ("used",       "s", "secondhand.s.02"),  # «a USED car» = previously owned, not used.a.01
                                             # «employed in accomplishing something» (which is just
                                             # the verb reading wearing an adjective coat)
    ("canned",     "s", "canned.s.02"),      # «CANNED soup» = sealed in a can, not «recorded for
                                             # broadcast» (the canned-laughter sense)
    ("sealed",     "a", "sealed.a.02"),      # «a SEALED envelope» = closed with a seal, not
                                             # «established irrevocably» (a sealed fate)
    ("drawn",      "s", "drawn.s.02"),       # «the DRAWN curtain» = pulled shut — the gloss is
                                             # verbatim; rank 0 is careworn.s.01, an exhausted FACE
    ("opened",     "s", "opened.s.01"),      # «the OPENED door» = made open, not open.a.05
                                             # «used of mouth or eyes»
    ("beaten",     "s", "beaten.s.01"),      # «the BEATEN path» = much trodden, not beaten.a.01
                                             # «formed or made thin by hammering» (metalwork)
    ("sharp",      "a", "sharp.a.09"),       # «a SHARP knife» = made by a thin edge, suitable for
                                             # cutting; rank 0 is crisp.s.01, «clearly defined»
    ("car",        "n", "car.n.01"),         # the motor vehicle. Not a frequency problem — rank 0
                                             # is already right — but the context centroid overrode
                                             # it at 0.652 in «a CAR door» and picked car.n.03, the
                                             # compartment slung under an AIRSHIP. Curated outranks
                                             # the centroid, which is exactly the lever for this.
]


def main():
    apply = "--apply" in sys.argv
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client[os.getenv("MONGO_DB_NAME")]
    coll = db["dictionary"]
    print(f"mode: {'APPLY' if apply else 'DRY RUN'}\n")

    for word, pos, sense_key in BATCH:
        rows = list(coll.find({"word": word, "pos": pos}, {"sense": 1, "preferred": 1}))
        if not rows:
            print(f"MISS {word}/{pos}: no dictionary rows at all — run curate_add_senses first?")
            continue
        target = next((r for r in rows if r["sense"] == sense_key), None)
        if target is None:
            print(f"MISS {word}/{pos}: {sense_key} not in the dictionary "
                  f"(has: {[r['sense'] for r in rows]}) — run curate_add_senses first")
            continue
        current = [r["sense"] for r in rows if r.get("preferred")]
        state = "already set" if current == [sense_key] else f"currently {current or 'unset'}"
        print(f"{word}/{pos} -> {sense_key}  ({state})")
        if apply:
            coll.update_many({"word": word, "pos": pos}, {"$unset": {"preferred": ""}})
            coll.update_one({"_id": target["_id"]}, {"$set": {"preferred": True}})

    if apply:
        flagged = list(coll.find({"preferred": True}, {"word": 1, "pos": 1, "sense": 1}))
        print(f"\ndone — {len(flagged)} preferred rows live:")
        for r in flagged:
            print(f"  {r['word']}/{r['pos']} = {r['sense']}")
    else:
        print("\n(dry run — nothing written; re-run with --apply)")


if __name__ == "__main__":
    main()
