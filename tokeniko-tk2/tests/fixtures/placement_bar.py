"""THE PLACEMENT BAR — forty placements the Captain ruled, 2026-09-19. **E3 task 6.**

**WHAT A PLACEMENT IS, AND WHY THE BASE'S BAR CANNOT JUDGE ONE.** The base's 37 pairs are
dimension-to-dimension: «is `walk.v` near `run.v`». A PLACEMENT is a sense the base does not hold,
projected into the base and ranked among its dimensions — `devour.v.01` landing next to `eat.v`. The
station's question about an unknown word is that one, and nothing had ever measured it: `place()`
issued a verdict through the BASE's floor, which was fitted on base-to-base cosines where p90 is
+0.000. On the placement population that floor says NEAR to 99.5% of R and 91.1% of D. *A floor that
says NEAR to everything is not a floor.*

**WHY THIS IS A FIXTURE AND NOT A MIGRATION — TWO REASONS, EITHER SUFFICIENT.**

1. **EVIDENCE, NOT KNOWLEDGE** (the third kingdom, the Captain 2026-09-17): *«a test is by its nature
   a curated set of circumstances: it can't be knowledge, it is curated, and it should be isolated by
   the app itself»*. These forty judge the geometry; nothing at runtime may read them.
2. **AND `dictionary_bar` WOULD HAVE EATEN THEM.** Every bar word becomes a SEED (dictionary req 12,
   `DictionaryConfig.seeds`), so declaring these pairs there would pull *involve*, *abbot* and *wary*
   into the base as DIMENSIONS — and a placement that becomes a dimension is no longer a placement.
   The bar would have destroyed its own subject, moved membership, and invalidated build
   `969766250c02`. `db/0007` wrote the warning down; this is the first case that met it.

**HOW THE FORTY WERE DRAWN.** Every one of the 116,725 placed senses on build `969766250c02` was
projected and ranked in the half that placed it (`tools/placement_bench.py`). The sample is stratified
by half and by cosine band (p0-10, p10-30, p30-55, p55-80, p80-100) so that no band could be argued
away as unrepresentative, and is restricted to senses WordNet's own corpus attests (SemCor count ≥ 2)
— **a deliberate bias, recorded**: the station meets words people SAY, and a bar of botanical
taxonomy would measure a population it will never be asked about.

**THE VERDICT IS THE BAR'S OWN VOCABULARY, READ AS THE STATION WOULD ASK IT**: NEAR = this placement
says something TRUE about the sense, and a station may trust it; FAR = it does not, whatever the
number beside it.

**RULED BY THE CAPTAIN ON 2026-09-19**, against the QM's own lean on all forty — *«I tried to
disagree on some… but your judgement is not different than mine»*. Where the two eyes agreed the row
carries one `why`; the reasoning is kept verbatim because it is what a later reader argues WITH.
"""

from dataclasses import dataclass

#: The build these cosines were measured on. A placement's number is a reading OF a base, so a
#: different build makes every cosine here a historical figure rather than a current one.
BUILD = "969766250c02"

#: The policy whose projection produced them — v14, the base's own floor at +0.15.
POLICY_VERSION = 14

RELATIONAL, DISTRIBUTIONAL = "relational", "distributional"
NEAR, FAR = "NEAR", "FAR"


@dataclass(frozen=True, slots=True)
class Placement:
    """One sense, where it landed, and whether that landing may be trusted."""

    sense: str
    dimension: str
    cosine: float
    half: str
    also: tuple[str, ...]
    gloss: str
    verdict: str
    why: str
    #: Whether R STATES an edge from this sense to this dimension, measured on the build above.
    #: It is evidence, not a derivation: it took the body's own sense rows to read it, and it is
    #: what the placement rule turned out to be (req 22). False for every D row BY CONSTRUCTION —
    #: a sense reaches D precisely because it states no relations.
    stated: bool = False


PLACEMENTS = (
    # ---- R, the relations half: the sense STATES an edge, and the projection rides it -----------
    Placement("involve.v.05", "include.v", 0.2606, RELATIONAL, ("admit.v", "comprise.v"),
              "contain as a part", NEAR,
              "exact — and the LOWEST cosine in the whole sample, which is the finding", True),
    Placement("outperform.v.01", "improve.v", 0.2945, RELATIONAL, ("sole.v", "better.v"),
              "be or do something to a greater degree", NEAR,
              "the right family: both are «better», one comparatively"),
    Placement("metamorphose.v.02", "warm.v", 0.3518, RELATIONAL, ("aggregate.v", "felt.v"),
              "change in outward structure or looks", FAR,
              "a sibling under «change», and a sibling of a sibling says nothing"),
    Placement("idler.n.01", "closer.n", 0.3634, RELATIONAL, ("convert.n", "cripple.n"),
              "person who does no work", FAR,
              "shares only the shape «person who —s»; an idler is not a closer"),
    Placement("image.v.02", "infer.v", 0.3846, RELATIONAL, ("picture.v", "sense.v"),
              "imagine; conceive of; see in one's mind", FAR,
              "wrong at rank 1 while `picture.v`, which is right, sits at rank 2"),
    Placement("philia.n.01", "affect.n", 0.4048, RELATIONAL, ("wish.n", "happiness.n"),
              "a positive feeling of liking", NEAR, "affect IS feeling, in the psychological sense"),
    Placement("cockle.v.02", "inhale.v", 0.4088, RELATIONAL, ("knit.v", "attract.v"),
              "to gather something into small wrinkles or folds", FAR, "unrelated"),
    Placement("deposit.v.03", "space.v", 0.4203, RELATIONAL, ("middle.v", "situate.v"),
              "put (something somewhere) firmly", FAR,
              "`situate.v` at rank 3 is the placement; rank 1 is not"),
    Placement("switch.v.04", "strengthen.v", 0.4454, RELATIONAL, ("warm.v", "shift.v"),
              "make a shift in or exchange of", FAR, "`shift.v` at rank 3 is right; rank 1 is not"),
    Placement("hurler.n.01", "performer.n", 0.4555, RELATIONAL, ("actor.n", "player.n"),
              "(baseball) the person who does the pitching", NEAR, "a player, and filed as one"),
    Placement("learn.v.01", "major.v", 0.4824, RELATIONAL, ("experiment.v", "bone.v"),
              "gain knowledge or skills", NEAR, "the study family, reached through its hyponyms"),
    Placement("sidetrack.n.01", "runway.n", 0.4891, RELATIONAL, ("steps.n", "groove.n"),
              "a short stretch of railroad track", NEAR, "weak but true: a track is a track"),
    Placement("picture.n.07", "television.n", 0.5033, RELATIONAL, ("audio.n", "prose.n"),
              "the visible part of a television transmission", NEAR,
              "exact, and `audio.n` beside it is the sibling that proves it", True),
    Placement("customary.a.02", "usual.a", 0.5241, RELATIONAL, ("common.a", "regular.a"),
              "commonly used or practiced; usual", NEAR, "exact", True),
    Placement("following.a.03", "following.a", 0.5241, RELATIONAL, ("able.a", "abnormal.a"),
              "going or proceeding or coming after", NEAR,
              "the control: a sense of a dimension's own word must land on that word"),
    Placement("schoolhouse.n.01", "outbuilding.n", 0.5462, RELATIONAL, ("skeleton.n", "ruin.n"),
              "a building where young people receive education", NEAR, "a building, which is true"),
    Placement("mutuality.n.02", "intercourse.n", 0.5959, RELATIONAL, ("sharing.n", "giving.n"),
              "a reciprocal relation between interdependent entities", NEAR,
              "exchange — and `sharing`/`giving` beside it say the same"),
    Placement("unemployment.n.01", "employ.n", 0.6172, RELATIONAL, ("wild.n", "freedom.n"),
              "the state of being unemployed or not having a job", NEAR,
              "right topic, opposite polarity — this space measures antonyms NEAR by construction"),
    Placement("dirt.n.02", "infected.a", 0.6247, RELATIONAL, ("dirty.a", "illegal.a"),
              "the state of being covered with unclean things", NEAR,
              "the uncleanness axis, with `dirty.a` at rank 2"),
    Placement("abbot.n.01", "religious.n", 0.7293, RELATIONAL, ("superior.n", "better.n"),
              "the superior of an abbey of monks", NEAR, "exact: a religious is a member of an order", True),

    # ---- D, the distribution half: the projection rides the DEFINITION's words ------------------
    Placement("qualified.a.01", "meeting.n", 0.1078, DISTRIBUTIONAL, ("task.v", "train.v"),
              "MEETING the proper standards and requirements", FAR,
              "the gloss's verb «meeting», read as a noun"),
    Placement("dollar.n.02", "piece.v", 0.1365, DISTRIBUTIONAL, ("abuse.v", "medicine.v"),
              "a PIECE of paper money worth one dollar", FAR, "a gloss word, and the wrong sense of it"),
    Placement("patrol.n.01", "guide.n", 0.1374, DISTRIBUTIONAL, ("used.a", "use.n"),
              "a detachment used for security or reconnaissance", FAR, "unrelated"),
    Placement("mount.n.03", "project.v", 0.1491, DISTRIBUTIONAL, ("higher.a", "likely.a"),
              "a land mass that PROJECTS well above its surroundings", FAR, "a gloss word"),
    Placement("recuperation.n.01", "orderly.a", 0.1581, DISTRIBUTIONAL, ("last.a", "gradual.a"),
              "gradual healing (through rest) after sickness or injury", FAR, "unrelated"),
    Placement("attack.n.05", "act.n", 0.1654, DISTRIBUTIONAL, ("divorce.n", "socially.r"),
              "the ACT of attacking", NEAR,
              "right — an attack IS an act — and right for the same gloss reading that makes the "
              "others wrong, which is why the number cannot be the judge"),
    Placement("barbarity.n.02", "act.n", 0.1654, DISTRIBUTIONAL, ("divorce.n", "socially.r"),
              "a brutal barbarous savage ACT", NEAR, "the same, at the same cosine"),
    Placement("engrossed.a.01", "mark.v", 0.1888, DISTRIBUTIONAL, ("give.n", "done.a"),
              "giving or MARKED by complete attention to", FAR, "«marked by» — the gloss's grammar"),
    Placement("triumphant.a.01", "enjoyable.a", 0.2004, DISTRIBUTIONAL, ("proud.a", "prevailing.a"),
              "joyful and proud especially because of triumph", FAR,
              "borderline: the affect axis is right, but `proud.a` at rank 2 was the placement"),
    Placement("splendiferous.a.01", "reward.v", 0.2132, DISTRIBUTIONAL, ("honor.n", "desirable.a"),
              "having great beauty and splendor", FAR, "unrelated"),
    Placement("inquiring.a.01", "give.n", 0.2175, DISTRIBUTIONAL, ("inquiry.n", "end.n"),
              "GIVEN to inquiry", FAR,
              "a function word wins over `inquiry.n`, which is the word the gloss is about"),
    Placement("idolise.v.01", "excess.a", 0.2208, DISTRIBUTIONAL, ("excess.n", "formal.n"),
              "love uncritically or to EXCESS; venerate as an idol", FAR, "a gloss word, and a modifier"),
    Placement("transcendental.a.01", "accordance.n", 0.2500, DISTRIBUTIONAL, ("exist.v", "existing.a"),
              "existing outside of or NOT IN ACCORDANCE with nature", FAR,
              "a gloss word — and the NEGATION it sat inside is dropped, which D cannot see"),
    Placement("neutralization.n.01", "possible.n", 0.3162, DISTRIBUTIONAL, ("action.v", "standing.n"),
              "action intended to keep a country politically neutral", FAR, "unrelated"),
    Placement("fin.n.01", "four.a", 0.3243, DISTRIBUTIONAL, ("sum.v", "cubic.a"),
              "the cardinal number that is the sum of FOUR and one", FAR,
              "off by one, by definition-word: a fin is five"),
    Placement("keen.a.01", "draw.n", 0.3333, DISTRIBUTIONAL, ("fine.v", "subject.a"),
              "ability to recognize or DRAW fine distinctions", FAR, "a gloss word"),
    Placement("corticoefferent.a.01", "outward.r", 0.3333, DISTRIBUTIONAL, ("bowl.v", "pass.a"),
              "of a nerve fiber passing OUTWARD from the cerebral cortex", FAR,
              "keeps the modifier and drops the subject: half a meaning is not a placement"),
    Placement("shocking.a.01", "mark.v", 0.3448, DISTRIBUTIONAL, ("affix.v", "code.v"),
              "glaringly vivid; MARKED by sensationalism", FAR, "«marked by» again"),
    Placement("wary.a.01", "mark.v", 0.3448, DISTRIBUTIONAL, ("affix.v", "code.v"),
              "MARKED by keen caution and watchful prudence", FAR,
              "«marked by» a third time, on a third unrelated sense"),
    Placement("strategical.a.01", "concern.v", 0.3780, DISTRIBUTIONAL, ("pertain.v", "concern.n"),
              "relating to or CONCERNED with strategy", FAR,
              "every one of the top three is a relating-word, and «strategy» appears in none"),
)


def of_half(half: str) -> tuple[Placement, ...]:
    return tuple(p for p in PLACEMENTS if p.half == half)


def _check() -> None:
    """The fixture's own invariants — evidence with a hole in it judges nothing."""
    if len(PLACEMENTS) != 40:
        raise ValueError(f"the bar is forty pairs, ruled together — got {len(PLACEMENTS)}")
    if len({p.sense for p in PLACEMENTS}) != len(PLACEMENTS):
        raise ValueError("a sense appears twice")
    for placement in PLACEMENTS:
        if placement.verdict not in (NEAR, FAR):
            raise ValueError(f"{placement.sense}: {placement.verdict!r} is not a verdict")
        if not placement.why:
            raise ValueError(f"{placement.sense}: a pair with no reasoning cannot be argued with")


_check()
