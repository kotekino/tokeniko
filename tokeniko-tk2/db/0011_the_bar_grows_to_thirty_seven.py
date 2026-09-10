"""0011 — bar version 2: the acceptance bar grows from eighteen pairs to thirty-seven.

**WHY IT GROWS AT ALL.** Eighteen pairs was a draft and the Captain said so when he moved the bar
into rows: «it is not complete, not even far, and it should be — we can't get completeness in code,
and most of all completeness is an iterative process, so it is db by definition». This is the first
iteration, and it is the one E1 needed: **every ruling of the last two days was fitted to eighteen
pairs**, and T5 proved those eighteen cannot see the space. At the ruled mix of 0.5, R states an
opposition for 405 pairs and only 208 still read negative — **167 oppositions are lifted to zero or
above by D**, `here.r ~ there.r` from -1.000 to +0.926. Not one of them is on the bar, because the
bar's only two opposition pairs are verbs. A bar that cannot see a defect is not a bar; it is a
habit. So: rule the bar first, then re-measure the floors, the mix and the closed-class question
against something that can fail them.

**HOW THE PAIRS WERE CHOSEN, and the honesty this file has to carry.** Generated-then-curated, the
way the seeds were grown — never typed longer. The generator (`tools/propose_bar.py`) is
**structurally blind**: it imports nothing from `relations`, `distribution` or `matrix`, builds no
matrix and takes no reading. The only pair-level question it asks is whether WordNet STATES an edge
between two keys — a fact upstream of every weight, the mix and the floors. Seven classes, each
chosen for what it puts at risk; the verdict a class proposes is mechanical and uniform, because a
generator that guessed per pair would be curating.

The curation was the officer's and then mine, and neither of us was blind to the standing eighteen —
we had read their numbers all epic. What we had NOT seen was any reading of any candidate: the list
was frozen to `/tmp/t5/bar_v2_proposal.json`, **sha256 `ed33961e9b17bb5e…`, 2026-09-10 11:08:50**,
and measured only afterwards. Two verdicts were flipped against the generator on the meaning alone
(`land.v ~ leave.v` and `bed.n ~ drink.n`, both to FAR) before that freeze.

**THE TWO ADVERB PAIRS AND WHY THEY ARE NOT CHEATING.** The seventeen frozen candidates contained no
adverb opposition, which is exactly the class the sign-burial finding lives in. Adding
`here.r ~ there.r` — a pair whose bad reading we had just seen — would have been fitting the bar to
a result, and «a pair proposed after seeing a result is not a bar pair». So the CLASS was named as
structurally missing and the pairs were drawn BLIND from WordNet's stated adverb antonymy (37 exist
in the base), seed 20260910, taking the draw as it came. `big.r ~ small.r` came out of the same draw
and was DROPPED, not because it reads badly — it was never read — but because its primary senses
(«extremely well» / «on a small scale») do not oppose: the `senses="primary"` rot, visible in the
glosses before any measurement.

**WHAT MOVES.** The bar only. Nineteen rows at version 2; v1's eighteen keep their `version`, their
`position` and their `why` verbatim and are never retired — the collection is an append-mostly
LEDGER, so «was this pair declared before that run?» stays machine-checkable. The policy rows do not
move at all: no version 8 here. The bar fingerprint moves and the config fingerprint with it, which
is the mechanism working — a build measured against 37 pairs must not be able to present the hash of
one measured against 18.

**WHAT IT IS NOT.** It declares no acceptance floor. The floors were the other half of T5 and they
are deliberately NOT here: measured against the standing eighteen, no single threshold does better
than 14 of 18, every zero-error shape needs a negative FAR ceiling, and the zero-error window is
0.011 wide — a number fitted to two pairs. Adding these nineteen moves the FAR wall from +0.1377 to
+0.2142 before anything else is decided. The floor is ruled after this lands and is re-measured, not
before.

**NOT APPLIED BY THE OFFICER OR THE QM.** Written and reported; the apply is the Captain's hand.
"""

from tk2.core.models import ALL_MODELS, BASE_MODELS, LEDGER_MODELS, DictionaryBarDoc
from tk2.dictionary import policy
from tk2.dictionary.config import BarPair
from tk2.migrations import ensure_collections

BAR_VERSION = 2

#: The frozen proposal's own hash, carried so the claim above can be checked rather than believed.
PROPOSAL_SHA256 = "ed33961e9b17bb5ee78cb4f1"

#: The blind draw's seed, for the two adverb pairs and the four controls alike.
DRAW_SEED = 20260910


# ------------------------------------------------------------------------------------------------
# the nineteen new pairs — approved by the Captain, 2026-09-10, none cut
# ------------------------------------------------------------------------------------------------

NEW_PAIRS = (
    # --- opposition: does the sign survive topical nearness, and does it survive OUTSIDE verbs? ---
    BarPair("open.v", "shut.v", "FAR",
            "stated antonymy, and both definitions are about the same act — the sign against the "
            "gloss overlap in one pair"),
    BarPair("employee.n", "employer.n", "FAR",
            "a NOUN opposition: R's antonymy is overwhelmingly adjectival and nothing tested the "
            "sign on nouns. Topically as near as two words get — an employer is defined by "
            "employing, an employee by being employed — so it is the sign or nothing"),
    BarPair("mental.a", "physical.a", "FAR",
            "stated antonymy between two abstract adjectives, the ground R is quietest about"),
    BarPair("externally.r", "internally.r", "FAR",
            "an ADVERB opposition, drawn blind from WordNet's stated adverb antonymy (seed "
            "20260910) after the class was found missing from the frozen seventeen. The class is "
            "where the sign burial is worst — 167 of 405 stated oppositions read at or above zero "
            "at mix 0.5, and the ones that break loudest are adverbs"),
    BarPair("agreeably.r", "unpleasantly.r", "FAR",
            "the second of the blind adverb draw. «In an enjoyable manner» against «in an "
            "unpleasant manner»: near-identical gloss shape, opposite meaning — the exact case a "
            "gloss-overlap floor gets wrong and a sign gets right"),

    # --- collapse: land.n~land.v's shape, generalised past the one pair it was found on ---
    BarPair("fast.n", "fast.v", "NEAR",
            "abstaining from food, and to abstain from food: one act, two parts of speech"),
    BarPair("compass.n", "compass.v", "FAR",
            "a navigational instrument against to bring about — land.n~land.v's shape over the "
            "identical derivational cell, and the pair that becomes the new FAR wall"),
    BarPair("buy.n", "buy.v", "NEAR",
            "an advantageous purchase, and to obtain by purchase"),
    BarPair("play.n", "play.v", "FAR",
            "a dramatic work against to participate in games — one spelling, two unrelated "
            "readings. The most arguable pair of the nineteen and kept deliberately: a bar whose "
            "every pair is obvious tests nothing"),

    # --- family: the axes R is mute about, which is what D was built for ---
    BarPair("food.n", "hungry.a", "NEAR",
            "the effect axis, second witness beside eat.v~hungry.a"),
    BarPair("intend.v", "wish.v", "NEAR",
            "volitional: action selection resolves these against each other and R states nothing "
            "between them"),
    BarPair("must.n", "need.n", "NEAR",
            "the volitional family in its noun readings"),
    BarPair("land.v", "leave.v", "FAR",
            "one family, opposite endpoints: to come to rest against to go away. The generator "
            "proposed NEAR from the family alone; the meaning says FAR, and the flip was made "
            "before the freeze"),
    BarPair("bed.n", "drink.n", "FAR",
            "one family is not one neighbourhood: furniture against a serving of a beverage. Also "
            "flipped against the generator before the freeze"),

    # --- sibling: can R reach a co-hyponym pair it states no direct edge for? ---
    BarPair("affliction.n", "injury.n", "NEAR",
            "co-hyponyms of ill_health with no direct edge — R can only reach it through shared "
            "hypernym columns, as it reaches walk.v~run.v"),

    # --- controls: uniformly random, and the junk plateau's tripwire ---
    BarPair("impairment.n", "nonsweet.a", "FAR",
            "drawn uniformly at random from the dimension list (seed 20260910)"),
    BarPair("thoroughly.r", "swinging.n", "FAR",
            "drawn uniformly at random from the dimension list (seed 20260910)"),
    BarPair("shadow.n", "upward.a", "FAR",
            "drawn uniformly at random from the dimension list (seed 20260910)"),
    BarPair("interlace.v", "aged.n", "FAR",
            "drawn uniformly at random from the dimension list (seed 20260910)"),
)


BAR_ROWS = policy.bar_rows_of(NEW_PAIRS, BAR_VERSION)


def up(writer, db) -> None:
    # v1's rows are not touched: append-mostly is what makes the ledger readable backwards.
    ensure_collections(db, [*ALL_MODELS, *LEDGER_MODELS, *BASE_MODELS])

    writer.insert_many(DictionaryBarDoc, BAR_ROWS)
