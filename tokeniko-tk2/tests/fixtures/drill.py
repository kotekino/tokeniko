"""THE SEVENTY-FIVE SENTENCE DRILL — E2's acceptance gate, drilled BY HAND.

The bar and the scoring rules were declared and committed BEFORE this file existed:
`docs/tkzip/202609140917_the-drill-bar.md`, commit `1a68337`. Nothing here may quietly move them.

  PASS     every content element lands in a slot and the zip's structure is the sentence's
  PARTIAL  something could not be placed AND the zip says so honestly — counts against the 90%
  FAIL     the zip is complete and confident and says something the sentence does not

Three halves, as allocated: the six ruled CLUSTERS (each exists to decide something genuinely open),
real TRAFFIC from `tokeniko_mem.tkzipdebug` (sentences he actually heard), and AWKWARD cases chosen
to be hard (README §6, plus the Captain's own first-draft rows).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from tk2.tkzip.schema import (
    AttitudeRow, Box, ContentRow, Determination, DomainRow, JoinRow, Modality,
    ModalityRow, NegationRow, Open, Operator, Pov, QuantifierRow, Quantity, Ref, Role,
    Theatre,
    Var, Zip,
)

Verdict = Literal["pass", "partial", "fail"]


@dataclass(frozen=True)
class Case:
    id: str
    sentence: str
    source: str
    zip: Zip
    verdict: Verdict
    note: str = ""
    # Ids this zip must NOT equal — two readings that must stay two zips.
    distinct_from: tuple[str, ...] = field(default_factory=tuple)


# ------------------------------------------------------------------------------------------------
# helpers — so a case reads as the sentence it encodes
# ------------------------------------------------------------------------------------------------

def n(head=None, **kw) -> Box:
    """A filled box. `head` may be a key, a Var, an Open, or omitted (degree-only)."""
    return Box(head=head, **kw)


def the(head, **kw) -> Box:
    return Box(head=head, determination=Determination.DEFINITE, **kw)


def a(head, **kw) -> Box:
    return Box(head=head, determination=Determination.INDEFINITE, **kw)


def generic(head, **kw) -> Box:
    return Box(head=head, determination=Determination.GENERIC, **kw)


def _box(v) -> Box:
    """Fixture ergonomics only: a bare key, Var or Open in a box position means «that, alone».

    The schema itself stays strict — this coerces at the fixture boundary so a case reads as the
    sentence it encodes rather than as constructor noise.
    """
    return v if isinstance(v, Box) else Box(head=v)


def c(name, predicate=None, truth=1.0, pov=None, **boxes) -> ContentRow:
    return ContentRow(
        name=name, predicate=predicate, truth=truth, pov=pov,
        boxes={Role(k): _box(v) for k, v in boxes.items()},
    )


def j(name, op, left, right, truth=1.0) -> JoinRow:
    return JoinRow(name=name, operator=op, operands=[left, right], truth=truth)


def all_of(name, var, restriction, scopes, **kw) -> QuantifierRow:
    return QuantifierRow(name=name, binds=var, quantity=Quantity.UNIVERSAL,
                         restriction=restriction, scopes=scopes, **kw)


def some_of(name, var, restriction, scopes, **kw) -> QuantifierRow:
    return QuantifierRow(name=name, binds=var, quantity=Quantity.EXISTENTIAL,
                         restriction=restriction, scopes=scopes, **kw)


def no_(name, var, restriction, scopes, **kw) -> QuantifierRow:
    return QuantifierRow(name=name, binds=var, quantity=Quantity.NEGATIVE,
                         restriction=restriction, scopes=scopes, **kw)


def thinks(name, who, scopes, verb="think.v", **kw) -> AttitudeRow:
    return AttitudeRow(name=name, holder=who, verb=verb, scopes=scopes, **kw)


def not_(name, scopes) -> NegationRow:
    return NegationRow(name=name, scopes=scopes)


def must(name, scopes) -> ModalityRow:
    return ModalityRow(name=name, modality=Modality.NECESSITY, scopes=scopes)


def can(name, scopes) -> ModalityRow:
    return ModalityRow(name=name, modality=Modality.POSSIBILITY, scopes=scopes)


def within(name, domain, scopes) -> DomainRow:
    return DomainRow(name=name, domain=domain, scopes=scopes)


def V(x) -> Var:
    return Var(name=x)


CASES: list[Case] = []


def case(*args, **kw) -> None:
    CASES.append(Case(*args, **kw))




# ================================================================================================
# CLUSTER 1 — «only»: is it a SIXTH PREFIX ELEMENT, or does it collapse?
# ================================================================================================

case("only-1", "Smoking causes cancer.", "cluster:only",
     Zip(rows=[all_of("bP", "P", generic("person.n"), scopes="jn"),
               c("s", "smoke.v", agent=V("P")),
               c("k", "develop.v", experiencer=V("P"), patient=generic("cancer.n")),
               j("jn", Operator.IMPLY, "s", "k")]),
     "pass", "«causes» IS implication read with the theatre's arrow (req 37), so both halves are "
             "PROPOSITIONS over a person. The first encoding used bare nominalisations and the "
             "self-audit rejected it.")

case("only-2", "Only smoking causes cancer.", "cluster:only",
     Zip(rows=[all_of("bP", "P", generic("person.n"), scopes="jn"),
               c("s", "smoke.v", agent=V("P")),
               c("k", "develop.v", experiencer=V("P"), patient=generic("cancer.n")),
               j("jn", Operator.CONV, "s", "k")]),
     "pass", "«only» over the CAUSE flips the arrow: cancer ⇒ smoking. No sixth prefix element — the "
             "operator set already carried it, and CONV surviving task 2 turned out to be load-bearing.",
     distinct_from=("only-1", "only-3"))

case("only-3", "Smoking only causes cancer.", "cluster:only",
     Zip(rows=[all_of("bY", "Y", generic("effect.n"), scopes="jn"),
               c("s", "cause.v", agent=generic("smoking.n"), patient=V("Y")),
               c("y", patient=V("Y"), complement=generic("cancer.n")),
               j("jn", Operator.IMPLY, "s", "y")]),
     "pass", "«only» over the EFFECT is a universal over effects plus an identity — quantification, "
             "not a new element. Same word, different scope, different zip.",
     distinct_from=("only-2",))

case("only-4", "I stayed home only because it rained.", "cluster:only",
     Zip(rows=[c("r", "rain.v"), c("s", "stay.v", agent=n("me.n"), location=n("home.n", marker="at")),
               j("jn", Operator.EQ, "r", "s")]),
     "pass", "«only because» = the biconditional. The Captain's test: «…but I'd have stayed anyway» "
             "is coherent after «because» and contradictory after «only because».",
     distinct_from=("only-5",))

case("only-5", "If and only if it rains, I stay home.", "cluster:only",
     Zip(rows=[c("r", "rain.v", truth=None),
               c("s", "stay.v", truth=None, agent=n("me.n"), location=n("home.n", marker="at")),
               j("jn", Operator.EQ, "r", "s")]),
     "pass", "the same EQ as only-4 and a different zip, because «iff» claims neither half — "
             "assertion status separating them, exactly as at task 2")

case("only-6", "Only cats eat fish.", "cluster:only",
     Zip(rows=[all_of("bX", "X", n("eater.n"), scopes="jn"),
               c("e", "eat.v", agent=V("X"), patient=generic("fish.n")),
               c("x", patient=V("X"), complement=generic("cat.n")),
               j("jn", Operator.IMPLY, "e", "x")]),
     "pass", "restriction on a binder: ∀X(eats-fish(X) → cat(X))")


# ================================================================================================
# CLUSTER 2 — «to / toward / into / onto»: is `direction` a MISSING BOX?   → YES. Forced change #1.
# ================================================================================================

case("dir-1", "I walk to the station.", "cluster:direction",
     Zip(rows=[c("w", "walk.v", agent=n("me.n"), destination=the("station.n", marker="to"))]),
     "pass", "the marker records WHICH closed-class row was matched")

case("dir-2", "I walk toward the station.", "cluster:direction",
     Zip(rows=[c("w", "walk.v", agent=n("me.n"), destination=the("station.n", marker="toward"))]),
     "pass", "same box, different marker — and the marker row is where «no arrival entailed» lives. "
             "Without req 65 this would be the same zip as dir-1.",
     distinct_from=("dir-1",))

case("dir-3", "I walked as far as the bridge.", "cluster:direction",
     Zip(rows=[c("w", "walk.v", agent=n("me.n"), destination=the("bridge.n", marker="as far as"))]),
     "pass", "a multi-word marker; the closed-class rows are rows, so length costs nothing")

case("dir-4", "He looked up.", "cluster:direction",
     Zip(rows=[c("l", "look.v", agent=n("he.n"), direction=n("up.r"))]),
     "pass", "FORCED CHANGE #1 — a direction with NO ENDPOINT. Before the box existed this was an "
             "honest PARTIAL: not a destination (he does not arrive at *up*), not a path, not a manner.")

case("dir-5", "She turned left.", "cluster:direction",
     Zip(rows=[c("t", "turn.v", agent=n("she.n"), direction=n("left.r"))]),
     "pass", "the second witness, a different verb — so it was not an idiom of «look»")


# ================================================================================================
# CLUSTER 3 — existential `be`: content, not copular glue
# ================================================================================================

case("exist-1", "There is a cat.", "cluster:existential",
     Zip(rows=[some_of("bX", "X", n("cat.n"), scopes="e"), c("e", "exist.v", patient=V("X"))]),
     "pass", "a binder alone is not a claim — binders are not claimable — so existence must be "
             "asserted by a content row, which is what «existential be is content» means structurally")

case("exist-2", "There are no cats.", "cluster:existential",
     Zip(rows=[no_("bX", "X", generic("cat.n"), scopes="e"), c("e", "exist.v", patient=V("X"))]),
     "pass", "negative quantity; no negation row needed")

case("exist-3", "God exists.", "cluster:existential",
     Zip(rows=[c("e", "exist.v", patient=n("god.n"))]),
     "pass", "the same predicate without the «there is» frame — one zip shape, two surfaces")

case("exist-4", "Is there a cat?", "cluster:existential",
     Zip(rows=[some_of("bX", "X", n("cat.n"), scopes="e"),
               c("e", "exist.v", truth=Open(), patient=V("X"))]),
     "pass", "polar question: every box bound, the TRUTH open", distinct_from=("exist-1",))


# ================================================================================================
# CLUSTER 4 — never · hardly · almost: «structure, not description» (req 23) — tested
# ================================================================================================

case("nha-1", "He never works.", "cluster:never-hardly-almost",
     Zip(rows=[all_of("bT", "T", generic("time.n"), scopes="w"), not_("neg", "w"),
               c("w", "work.v", agent=n("he.n"), time=V("T"))]),
     "pass", "∀T ¬work — a universal over the time variable and a negation, both in the prefix. "
             "`never` collapses exactly as req 23 says.")

case("nha-2", "A calculator never thinks.", "cluster:never-hardly-almost",
     Zip(rows=[all_of("bX", "X", generic("calculator.n"), scopes="t"),
               all_of("bT", "T", generic("time.n"), scopes="t"), not_("neg", "t"),
               c("t", "think.v", agent=V("X"), time=V("T"))]),
     "pass", "his own traffic (missed-negation): two binders and a negation, all scoping one row")

case("nha-3", "He hardly works.", "cluster:never-hardly-almost",
     Zip(rows=[c("w", "work.v", agent=n("he.n"), manner=Box(degree=0.1))]),
     "pass", "a manner box carrying ONLY a degree — «works, to a small degree». FINDING: `hardly` is "
             "not structure in the way `never` is; it is a degree on the manner.")

case("nha-4", "He almost died.", "cluster:never-hardly-almost",
     Zip(rows=[c("d", "die.v", truth=0.0, patient=n("he.n"))],
         unplaced=["almost"], parse_confidence=0.6),
     "partial", "FINDING: req 23 over-grouped. `almost` is neither negation-plus-quantifier (`never`) "
                "nor a degree on a manner (`hardly`): «he almost died» asserts he did NOT die AND "
                "that the event was close, and closeness-to-an-event-not-occurring has no home. "
                "Honestly partial rather than silently dropped.")

case("nha-5", "I almost finished.", "cluster:never-hardly-almost",
     Zip(rows=[c("f", "finish.v", truth=0.0, agent=n("me.n"))],
         unplaced=["almost"], parse_confidence=0.6),
     "partial", "the second witness — different verb, different aspect, same gap")


# ================================================================================================
# CLUSTER 5 — «twice a week»: does `count` hold it, or does `frequency` come back as a box?
# ================================================================================================

case("freq-1", "I work twice a week.", "cluster:frequency",
     Zip(rows=[some_of("bT", "T", Box(head="occasion.n", marker="in", quantity=Quantity.UNIVERSAL,
                                      relation="week.n"), scopes="w", count=2),
               c("w", "work.v", agent=n("me.n"), time=V("T"))]),
     "pass", "the binder carries count=2 and its restriction carries the universal over weeks: "
             "∀week ∃²occasion. Strained but expressible — `count` holds it and `frequency` stays "
             "structure, as req 32 ruled.")

case("freq-2", "I work every day.", "cluster:frequency",
     Zip(rows=[all_of("bT", "T", generic("day.n"), scopes="w"),
               c("w", "work.v", agent=n("me.n"), time=V("T"))]),
     "pass", "the clean case: a universal over the time variable, no count needed")

case("freq-3", "I worked three times.", "cluster:frequency",
     Zip(rows=[some_of("bT", "T", n("occasion.n"), scopes="w", count=3),
               c("w", "work.v", agent=n("me.n"), time=V("T"))]),
     "pass", "count without a period")

case("freq-4", "How often do you work?", "cluster:frequency",
     Zip(rows=[some_of("bT", "T", n("occasion.n"), scopes="w", count=Open()),
               c("w", "work.v", agent=n("you.n"), time=V("T"))]),
     "pass", "the COUNT is the open slot — which is why `count` needed a binding state and not "
             "merely a number")


# ================================================================================================
# CLUSTER 6 — de re / de dicto: does the prefix actually express both?
# ================================================================================================

case("dere-1", "He thinks a cat is in the garden.  [de dicto]", "cluster:de-re",
     Zip(rows=[thinks("att", n("he.n"), scopes="g"),
               some_of("bC", "C", n("cat.n"), scopes="g"),
               c("g", patient=V("C"), location=the("garden.n", marker="in"))]),
     "pass", "the binder sits INSIDE the attitude's scope: no cat is asserted to exist",
     distinct_from=("dere-2",))

case("dere-2", "He thinks a cat is in the garden.  [de re]", "cluster:de-re",
     Zip(rows=[some_of("bC", "C", n("cat.n"), scopes="g"),
               thinks("att", n("he.n"), scopes="g"),
               c("g", patient=V("C"), location=the("garden.n", marker="in"))]),
     "pass", "the binder sits OUTSIDE: a particular cat exists and he is wrong about where it is")

case("dere-3", "He wants to marry a Norwegian.  [de dicto]", "cluster:de-re",
     Zip(rows=[thinks("att", n("he.n"), scopes="m", verb="want.v"),
               some_of("bN", "N", n("norwegian.n"), scopes="m"),
               c("m", "marry.v", agent=n("he.n"), patient=V("N"))]),
     "pass", "the textbook case, and the reason a flat-only POV was refused: it would have asserted "
             "that a particular Norwegian exists")

case("dere-4", "I don't know who ate the fish.", "cluster:de-re",
     Zip(rows=[not_("neg", "e"), thinks("att", n("me.n"), scopes="e", verb="know.v"),
               c("e", "eat.v", agent=Open(), patient=the("fish.n"))]),
     "pass", "an OPEN variable inside a negated attitude — req 4's unfinished thought, stored")


# ================================================================================================
# TRAFFIC — drawn from `tokeniko_mem.tkzipdebug`: 583 stored journeys, 245 mismatches, of which 114
# are FORMAT failures. These are sentences he actually heard, and the category is v1's own verdict
# on what its schema could not hold.
# ================================================================================================

# ---- wrong-structure (59 leads) -----------------------------------------------------------------

case("t-ws-1", "I go to sleep because I'm tired.", "traffic:wrong-structure",
     Zip(rows=[c("t", complement=n("tired.a"), experiencer=n("me.n")),
               c("s", "sleep.v", agent=n("me.n")),
               j("jn", Operator.IMPLY, "t", "s")]),
     "pass", "both halves claimed, joined by IMPLY — «because» with nothing left over")

case("t-ws-2", "I live in Asia because Japan is in Asia.", "traffic:wrong-structure",
     Zip(rows=[c("ja", complement=n("asia.n", marker="in"), patient=n("japan.n")),
               c("me", "live.v", agent=n("me.n"), location=n("asia.n", marker="in")),
               j("jn", Operator.IMPLY, "ja", "me")]),
     "pass", "the marker does real work here — «in» is containment, and req 65 is why it survives")

case("t-ws-3", "A person is wrong when he says false.", "traffic:wrong-structure",
     Zip(rows=[all_of("bP", "P", generic("person.n"), scopes="jn"),
               c("sf", "say.v", agent=V("P"), patient=generic("falsehood.n")),
               c("wr", patient=V("P"), complement=n("wrong.a")),
               j("jn", Operator.IMPLY, "sf", "wr")]),
     "pass", "«when» is a generic conditional here, not a time — and the drill says so because the "
             "time box stays EMPTY while IMPLY carries it")

case("t-ws-4", "Clouds can produce rain but not every cloud produces rain.", "traffic:wrong-structure",
     Zip(rows=[all_of("bC", "C", generic("cloud.n"), scopes="pr"),
               can("mod", "pr"),
               c("pr", "produce.v", agent=V("C"), patient=generic("rain.n")),
               all_of("bD", "D", generic("cloud.n"), scopes="ev"),
               c("ev", "produce.v", agent=V("D"), patient=generic("rain.n")),
               j("jn", Operator.NIMPLY, "pr", "ev")]),
     "pass", "◇∀ produce, AND NOT ∀ produce. `NIMPLY` is `A ∧ ¬B` — the Captain's own «regardless» "
             "encoding — and it is the compact spelling of «but» when the second half is negative.")

case("t-ws-5", "A calculator is a software but a calculator is not a mind.", "traffic:wrong-structure",
     Zip(rows=[all_of("bX", "X", generic("calculator.n"), scopes="jn"),
               c("sw", patient=V("X"), complement=generic("software.n")),
               c("mi", patient=V("X"), complement=generic("mind.n")),
               j("jn", Operator.NIMPLY, "sw", "mi")]),
     "pass", "one binder scoping the join, so both halves speak about the same calculator")

case("t-ws-6",
     "I'm not a software but I am a mind, because I'm a human being and all human beings are "
     "animals and all animals are minds.", "traffic:wrong-structure",
     Zip(rows=[all_of("bH", "H", generic("human.n"), scopes="ha"),
               all_of("bA", "A", generic("animal.n"), scopes="am"),
               c("sw", truth=0.0, patient=n("me.n"), complement=generic("software.n")),
               c("mi", patient=n("me.n"), complement=generic("mind.n")),
               c("hu", patient=n("me.n"), complement=generic("human.n")),
               c("ha", patient=V("H"), complement=generic("animal.n")),
               c("am", patient=V("A"), complement=generic("mind.n")),
               j("j1", Operator.AND, "hu", "ha"),
               j("j2", Operator.AND, "j1", "am"),
               j("j3", Operator.IMPLY, "j2", "mi"),
               j("j4", Operator.AND, "sw", "mi")]),
     "pass", "five content rows, four joins, two binders — and SINGLE-ROW NEGATION IS truth=0.0, "
             "not a negation row. That division was settled by this sentence.")

case("t-ws-7", "It doesn't contradict, because a mind can be an animal or a mind can be a software.",
     "traffic:wrong-structure",
     Zip(rows=[all_of("bM", "M", generic("mind.n"), scopes="an"),
               all_of("bN", "N", generic("mind.n"), scopes="so"),
               can("m1", "an"), can("m2", "so"),
               c("an", patient=V("M"), complement=generic("animal.n")),
               c("so", patient=V("N"), complement=generic("software.n")),
               j("jn", Operator.OR, "an", "so")]),
     "pass", "TWO modality rows scoping two different matrices — impossible before forced change #2")

case("t-ws-8", "If I tell you something you don't know, you learn it.", "traffic:wrong-structure",
     Zip(rows=[some_of("bS", "S", n("thing.n"), scopes="jn"),
               c("kn", truth=0.0, experiencer=n("you.n"), patient=V("S")),
               c("te", "tell.v", truth=None, agent=n("me.n"), recipient=n("you.n"), patient=V("S")),
               c("le", "learn.v", truth=None, experiencer=n("you.n"), patient=V("S")),
               j("j1", Operator.AND, "te", "kn"),
               j("jn", Operator.IMPLY, "j1", "le")]),
     "pass", "«if» — the halves are NOT claimed, only the join is. Same IMPLY as «because» (t-ws-1), "
             "and assertion status is the whole difference.",
     distinct_from=("t-ws-1",))

# ---- dropped-content (22 leads) ------------------------------------------------------------------

case("t-dc-1", "I live in a human body in Japan and you live in a computer in Japan.",
     "traffic:dropped-content",
     Zip(rows=[some_of("bB", "B", n("body.n"), scopes="jn"),
               some_of("bC", "C", n("computer.n"), scopes="jn"),
               c("hu", patient=V("B"), complement=generic("human.a")),
               c("me", "live.v", agent=n("me.n"), location=Box(head=V("B"), marker="in")),
               c("yo", "live.v", agent=n("you.n"), location=Box(head=V("C"), marker="in")),
               c("mj", patient=V("B"), complement=n("japan.n", marker="in")),
               c("yj", patient=V("C"), complement=n("japan.n", marker="in")),
               j("j1", Operator.AND, "hu", "me"), j("j2", Operator.AND, "j1", "mj"),
               j("j3", Operator.AND, "yo", "yj"), j("jn", Operator.AND, "j2", "j3")]),
     "pass", "TWO locations per clause — the thing v1 dropped — and ATTRIBUTIVE ADJECTIVES ARE "
             "SECOND ROWS: «a human body» is ∃B(body(B) ∧ human(B)). The first encoding put «human» "
             "in `relation`, which is the POSSESSOR slot; the self-audit caught it. No new field "
             "was needed — the machinery already existed.")

case("t-dc-2", "A whale is a mammal and it feeds milk to its cubs.", "traffic:dropped-content",
     Zip(rows=[all_of("bW", "W", generic("whale.n"), scopes="jn"),
               c("ma", patient=V("W"), complement=generic("mammal.n")),
               c("fe", "feed.v", agent=V("W"), patient=generic("milk.n"),
                 recipient=Box(head="cub.n", relation=V("W"), determination=Determination.DEFINITE,
                               marker="to")),
               j("jn", Operator.AND, "ma", "fe")]),
     "pass", "«its cubs» — the possessor is a VARIABLE inside the record, which is what `relation` "
             "being a bindable field buys")

case("t-dc-3", "Cognition is the psychological result of perception and learning and reasoning.",
     "traffic:dropped-content",
     Zip(rows=[all_of("bP", "P", generic("person.n"), scopes="jn"),
               c("pe", "perceive.v", agent=V("P")), c("le", "learn.v", agent=V("P")),
               c("re", "reason.v", agent=V("P")),
               j("j1", Operator.AND, "pe", "le"), j("j2", Operator.AND, "j1", "re"),
               some_of("bR", "R", the("result.n", relation=Ref(row="j2"), marker="of"), scopes="jn"),
               c("ps", patient=V("R"), complement=generic("psychological.a")),
               c("co", patient=generic("cognition.n"), complement=V("R")),
               j("jn", Operator.AND, "ps", "co")]),
     "pass", "THE SENTENCE THAT FORCED CHANGE #3. A three-way coordination INSIDE a box — «the "
             "result OF [perception and learning and reasoning]» — needs the `relation` to name a "
             "JOIN ROW. Before `Ref` the row name validated as a bare dictionary key and the "
             "evaluator would have gone looking for «j2» in the dictionary.")

case("t-dc-4", "You learn only from minds you trust.", "traffic:dropped-content",
     Zip(rows=[all_of("bM", "M", generic("mind.n"), scopes="jn"),
               c("le", "learn.v", experiencer=n("you.n"), source=Box(head=V("M"), marker="from")),
               c("tr", "trust.v", experiencer=n("you.n"), patient=V("M")),
               j("jn", Operator.IMPLY, "le", "tr")]),
     "pass", "«only» again, from real traffic and unprompted — restriction on a binder, the same "
             "shape as only-6")

case("t-dc-5", "Osaka is where you live and it is also the name of a big city.",
     "traffic:dropped-content",
     Zip(rows=[some_of("bC", "C", n("city.n"), scopes="jn"),
               c("bg", patient=V("C"), complement=generic("big.a")),
               c("li", "live.v", agent=n("you.n"), location=n("osaka.n", marker="in")),
               c("na", patient=n("osaka.n"),
                 complement=Box(head="name.n", relation=V("C"), marker="of",
                                determination=Determination.DEFINITE)),
               j("j1", Operator.AND, "bg", "na"), j("jn", Operator.AND, "j1", "li")]),
     "pass", "«a big city» is a second row, not a degree — `degree` is for «VERY big», an intensifier "
             "on a property, and the self-audit caught the conflation")

# ---- operator-flattening (10 leads) ---------------------------------------------------------------

case("t-of-1", "I am happy because I am thinking and I love thinking.", "traffic:operator-flattening",
     Zip(rows=[c("th", "think.v", agent=n("me.n")),
               c("lo", "love.v", experiencer=n("me.n"), topic=generic("thinking.n")),
               c("ha", experiencer=n("me.n"), complement=n("happy.a")),
               j("j1", Operator.AND, "th", "lo"),
               j("jn", Operator.IMPLY, "j1", "ha")]),
     "pass", "the conjunction is the REASON, so it must be one operand of the IMPLY — exactly the "
             "nesting v1 flattened")

case("t-of-2", "A mind thinks, and a calculator does not think, so a calculator is not a mind.",
     "traffic:operator-flattening",
     Zip(rows=[all_of("bM", "M", generic("mind.n"), scopes="mt"),
               all_of("bC", "C", generic("calculator.n"), scopes="j2"),
               c("mt", "think.v", agent=V("M")),
               c("ct", "think.v", truth=0.0, agent=V("C")),
               c("cm", truth=0.0, patient=V("C"), complement=generic("mind.n")),
               j("j1", Operator.AND, "mt", "ct"),
               j("j2", Operator.AND, "j1", "cm"),
               j("jn", Operator.IMPLY, "j1", "cm")]),
     "pass", "a syllogism as one zip: two premises conjoined, the conclusion implied, and every "
             "negation carried by truth=0.0")

case("t-of-3", "Action implies ability but ability doesn't imply action.",
     "traffic:operator-flattening",
     Zip(rows=[all_of("bP", "P", generic("person.n"), scopes="jn"),
               c("ac", "act.v", truth=None, agent=V("P")),
               c("ab", truth=None, patient=V("P"), complement=generic("able.a")),
               j("f", Operator.IMPLY, "ac", "ab"),
               j("b", Operator.IMPLY, "ab", "ac", truth=0.0),
               j("jn", Operator.AND, "f", "b")]),
     "pass", "a zip ABOUT two implications, one of them claimed false — which works only because a "
             "join is itself claimable")

case("t-of-4", "You have friends because I'm your friend and playbot-hellen is your friend.",
     "traffic:operator-flattening",
     Zip(rows=[c("mf", patient=n("me.n"), complement=Box(head="friend.n", relation="you.n",
                                                         determination=Determination.DEFINITE)),
               c("hf", patient=n("hellen.n"), complement=Box(head="friend.n", relation="you.n",
                                                             determination=Determination.DEFINITE)),
               some_of("bF", "F", generic("friend.n"), scopes="ha"),
               c("ha", "have.v", agent=n("you.n"), patient=V("F")),
               j("j1", Operator.AND, "mf", "hf"),
               j("jn", Operator.IMPLY, "j1", "ha")]),
     "pass", "two named individuals and a possessive relation in the complement")

# ---- missed-mood (12 leads) -----------------------------------------------------------------------

case("t-mo-1", "Do you exist?", "traffic:missed-mood",
     Zip(rows=[c("e", "exist.v", truth=Open(), patient=n("you.n"))]),
     "pass", "polar question — the TRUTH is the open slot, and there is no mood field to get wrong")

case("t-mo-2", "Tokeniko, who am I?", "traffic:missed-mood",
     Zip(rows=[c("i", patient=n("me.n"), complement=Open())]),
     "pass", "a wh-question on the complement; the vocative is addressing, not content")

case("t-mo-3", "What are you?", "traffic:missed-mood",
     Zip(rows=[c("i", patient=n("you.n"), complement=Open())]),
     "pass", "the same shape as t-mo-2 with a different entity — which is correct: they ARE the "
             "same question asked about two people")

case("t-mo-4", "I would like to know what you think about yourself.", "traffic:missed-mood",
     Zip(rows=[thinks("want", n("me.n"), scopes="kn", verb="want.v", strength=0.6),
               thinks("att", n("you.n"), scopes="op", verb="think.v"),
               c("op", patient=n("you.n"), complement=Open()),
               c("kn", "know.v", experiencer=n("me.n"), topic=Open())]),
     "pass", "a wish over a knowing over an open question inside someone else's attitude — three "
             "levels, and `strength` carries «would like» rather than «want»")

# ---- missed-negation (8 leads) --------------------------------------------------------------------

case("t-ng-1", "Some software is mind, tokeniko is a mind, a calculator isn't.",
     "traffic:missed-negation",
     Zip(rows=[some_of("bS", "S", generic("software.n"), scopes="sm"),
               c("sm", patient=V("S"), complement=generic("mind.n")),
               c("tm", patient=n("tokeniko.n"), complement=generic("mind.n")),
               c("cm", truth=0.0, patient=generic("calculator.n"), complement=generic("mind.n")),
               j("j1", Operator.AND, "sm", "tm"), j("jn", Operator.AND, "j1", "cm")]),
     "pass", "«isn't» is ellipsis — the complement comes from context, which the station takes as an "
             "ARGUMENT (parser-compiler req 7). Resolved here, as the station would.")

case("t-ng-2", "No software is an animal.", "traffic:missed-negation",
     Zip(rows=[no_("bS", "S", generic("software.n"), scopes="an"),
               c("an", patient=V("S"), complement=generic("animal.n"))]),
     "pass", "NEGATIVE quantity, not a negation row — «no X is Y» is about the quantifier")

case("t-ng-3", "I am not.", "traffic:missed-negation",
     Zip(rows=[c("i", truth=0.0, patient=n("me.n"), complement=generic("software.n"))],
         parse_confidence=0.55),
     "pass", "everything but the subject is elided. Resolved against the previous turn («are you a "
             "software?»), with confidence saying the zip leaned on context.")

case("t-ng-4", "No, some software is a mind and some is not.", "traffic:missed-negation",
     Zip(rows=[some_of("bA", "A", generic("software.n"), scopes="am"),
               some_of("bB", "B", generic("software.n"), scopes="bm"),
               c("am", patient=V("A"), complement=generic("mind.n")),
               c("bm", truth=0.0, patient=V("B"), complement=generic("mind.n")),
               j("jn", Operator.AND, "am", "bm")]),
     "pass", "TWO existentials over the same restriction — «some…and some not» needs two variables, "
             "and one clause-level quantifier (v1) cannot say it")

# ---- missed-modality (2 leads) ----------------------------------------------------------------------

case("t-md-1", "Software can be minds and humans must be minds.", "traffic:missed-modality",
     Zip(rows=[all_of("bS", "S", generic("software.n"), scopes="sm"),
               all_of("bH", "H", generic("human.n"), scopes="hm"),
               can("m1", "sm"), must("m2", "hm"),
               c("sm", patient=V("S"), complement=generic("mind.n")),
               c("hm", patient=V("H"), complement=generic("mind.n")),
               j("jn", Operator.AND, "sm", "hm")]),
     "pass", "THE SENTENCE THAT FORCED CHANGE #2. ◇A ∧ □B — two different modalities over two "
             "conjuncts. A prefix scoping «everything after it» could not express this.")

case("t-md-2", "So a calculator does not necessarily think.", "traffic:missed-modality",
     Zip(rows=[all_of("bC", "C", generic("calculator.n"), scopes="t"),
               not_("neg", "t"), must("mod", "t"),
               c("t", "think.v", agent=V("C"))]),
     "pass", "¬□ — negation ORDERED BEFORE the modality, both scoping the same matrix. The order is "
             "the whole meaning: ∀¬□ is not ∀□¬.")

# ---- missed-quantifier (1 lead) ---------------------------------------------------------------------

case("t-qu-1", "Tokeniko, the cat is dead and alive.", "traffic:missed-quantifier",
     Zip(rows=[c("d", patient=the("cat.n"), complement=n("dead.a")),
               c("a", patient=the("cat.n"), complement=n("alive.a")),
               j("jn", Operator.AND, "d", "a")]),
     "pass", "the format holds a contradiction without flinching — judging it is the evaluator's "
             "job, and a format that could not STATE it could not have it refuted either")


# ================================================================================================
# AWKWARD BY DESIGN — README §6's list, plus the Captain's own first-draft rows drilled against the
# schema they generated.
# ================================================================================================

case("aw-1", "The mail was written by John.", "awkward:passive",
     Zip(rows=[c("w", "write.v", agent=n("john.n"), patient=the("mail.n"))],
         topicality=Role.PATIENT),
     "pass", "roles NORMALIZE — John is the agent however the sentence was ordered — and the one "
             "topicality marker keeps what normalization would otherwise destroy: that the speaker "
             "chose to talk about the mail. The Captain's draft kept both; so does this.")

case("aw-2", "John wrote the mail.", "awkward:passive",
     Zip(rows=[c("w", "write.v", agent=n("john.n"), patient=the("mail.n"))]),
     "pass", "the same thought, and NOT the same zip — topicality is the only difference, and it "
             "enters no arithmetic",
     distinct_from=("aw-1",))

case("aw-3", "She painted the door red.", "awkward:resultative",
     Zip(rows=[c("p", "paint.v", agent=n("she.n"), patient=the("door.n")),
               c("r", patient=the("door.n"), complement=n("red.a")),
               j("jn", Operator.IMPLY, "p", "r")]),
     "pass", "OQ5: a second row, joined by IMPLY with the theatre giving the order. The explicit "
             "RESULT operator dissolved with CAUSE, and the condition it existed for — that bare "
             "succession must not derive causation — is met better, because IMPLY is the link.")

case("aw-4", "He ate the fish raw.", "awkward:depictive",
     Zip(rows=[c("e", "eat.v", agent=n("he.n"), patient=the("fish.n")),
               c("r", patient=the("fish.n"), complement=n("raw.a")),
               j("jn", Operator.AND, "e", "r")]),
     "pass", "depictive is CO-ASSERTED, not implied — the fish was already raw. One operator apart "
             "from aw-3, and that operator is the entire distinction.",
     distinct_from=("aw-3",))

case("aw-5", "I gave my sister a book.", "awkward:draft",
     Zip(rows=[c("g", "give.v", agent=n("me.n"), patient=a("book.n"),
                 recipient=Box(head="sister.n", relation="me.n",
                               determination=Determination.DEFINITE))]),
     "pass", "the Captain's own draft row — where `(me)sister` sat in `destination`. Split now: a "
             "recipient RECEIVES, a destination is a place, and «I baked a cake for Anna» does not "
             "entail Anna got a cake.")

case("aw-6", "I went from Rome to Genoa to see the Ligurian sea.", "awkward:draft",
     Zip(rows=[thinks("want", n("me.n"), scopes="se", verb="want.v"),
               c("se", "see.v", experiencer=n("me.n"),
                 topic=Box(head="sea.n", relation="liguria.n", determination=Determination.DEFINITE)),
               c("go", "go.v", agent=n("me.n"), source=n("rome.n", marker="from"),
                 destination=n("genoa.n", marker="to")),
               j("jn", Operator.IMPLY, "se", "go")]),
     "pass", "the draft's own row, which encoded purpose TWICE (a `goal` box and an IMPLY). One "
             "encoding now: the wanting implies the going, and nothing derives that I saw the sea, "
             "because «see» is true only UNDER the want. Rome and Genoa stay fillers — «Genoa is a "
             "city you can reason about».")

case("aw-7", "I build my contraption with my hammer.", "awkward:draft",
     Zip(rows=[c("b", "build.v", agent=n("me.n"),
                 patient=Box(head="contraption.n", relation="me.n",
                             determination=Determination.DEFINITE),
                 instrument=Box(head="hammer.n", relation="me.n", marker="with",
                                determination=Determination.DEFINITE))]),
     "pass", "the draft left the hammer unfilled; it lands in `instrument`")

case("aw-8", "The hammer is made of titanium.", "awkward:draft",
     Zip(rows=[c("m", "make.v", patient=the("hammer.n"),
                 source=n("titanium.n", marker="of"), agent=Open())]),
     "pass", "the draft's `material` column folds into `source`, as ruled at task 1")

case("aw-9", "She works for her family.", "awkward:draft",
     Zip(rows=[c("w", "work.v", agent=n("she.n"),
                 beneficiary=Box(head="family.n", relation="she.n", marker="for",
                                 determination=Determination.DEFINITE))]),
     "pass", "the draft's `advantage` column, renamed — and kept apart from `recipient`")

case("aw-10", "My cat is cute.", "awkward:draft",
     Zip(rows=[c("k", patient=Box(head="cat.n", relation="me.n",
                                  determination=Determination.DEFINITE),
                 complement=n("cute.a"), pov=Pov(holder=n("me.n"), verb="think.v"))]),
     "pass", "the draft's first row, verbatim: POV me/think, no verb, cat + cute")

case("aw-11", "Anna thinks that Bob believes the cat is hungry.", "awkward:nested-attitudes",
     Zip(rows=[thinks("a1", n("anna.n"), scopes="h"),
               thinks("a2", n("bob.n"), scopes="h", verb="believe.v"),
               c("h", experiencer=the("cat.n"), complement=n("hungry.a"))]),
     "pass", "attitudes at depth two — the case POV-as-a-field could not reach, and the reason the "
             "ledger said «POV beyond depth 1». Order is the nesting.")

case("aw-12", "Every teacher gave some student a book.", "awkward:three-quantifiers",
     Zip(rows=[all_of("bT", "T", generic("teacher.n"), scopes="g"),
               some_of("bS", "S", generic("student.n"), scopes="g"),
               some_of("bB", "B", generic("book.n"), scopes="g"),
               c("g", "give.v", agent=V("T"), recipient=V("S"), patient=V("B"))]),
     "pass", "three binders, one matrix, and their ORDER is the reading")

case("aw-13", "All that glitters is not gold.  [¬∀ — not all of it is]", "awkward:scope",
     Zip(rows=[not_("neg", "g"), all_of("bX", "X", generic("glitterer.n"), scopes="g"),
               c("g", patient=V("X"), complement=generic("gold.n"))]),
     "pass", "negation ordered BEFORE the universal", distinct_from=("aw-14",))

case("aw-14", "All that glitters is not gold.  [∀¬ — none of it is]", "awkward:scope",
     Zip(rows=[all_of("bX", "X", generic("glitterer.n"), scopes="g"), not_("neg", "g"),
               c("g", patient=V("X"), complement=generic("gold.n"))]),
     "pass", "the universal ordered before the negation. v1 had to patch this one combination into "
             "its quantifier enum (`NEGATED_UNIVERSAL`); a prefix handles the class.")

case("aw-15", "In Italy, you may drive in France with a foreign licence.", "awkward:domain",
     Zip(rows=[some_of("bL", "L", n("licence.n"), scopes="jn"),
               c("fo", patient=V("L"), complement=generic("foreign.a")),
               within("dom", n("italy.n", marker="in"), "d"), can("mod", "d"),
               c("d", "drive.v", agent=n("you.n"), location=n("france.n", marker="in"),
                 instrument=Box(head=V("L"), marker="with")),
               j("jn", Operator.AND, "fo", "d")]),
     "pass", "THE SENTENCE THAT PROVED `domain` IS NOT `location`: both appear, doing different "
             "jobs — Italy is the jurisdiction, France is where the driving happens.")

case("aw-16", "As a doctor I disagree; as a father I understand.", "awkward:domain",
     Zip(rows=[within("d1", a("doctor.n", marker="as"), "di"),
               within("d2", a("father.n", marker="as"), "un"),
               c("di", "disagree.v", experiencer=n("me.n")),
               c("un", "understand.v", experiencer=n("me.n")),
               j("jn", Operator.AND, "di", "un")]),
     "pass", "two contradictory positions, both held, NOT a KB contradiction — because each is "
             "indexed to its domain. Rules reqs 6-7: defeat in context, never deletion.")

case("aw-17", "Legally, in Italy, he is still married.", "awkward:domain",
     Zip(rows=[within("d1", generic("law.n"), "m"), within("d2", n("italy.n", marker="in"), "m"),
               c("m", patient=n("he.n"), complement=n("married.a"))]),
     "pass", "domains nest by order, like every other prefix element")

case("aw-18", "I ate with a fork.", "awkward:comitative",
     Zip(rows=[c("e", "eat.v", agent=n("me.n"), instrument=a("fork.n", marker="with"))]),
     "pass", "the marker is the same word; the BOX is what separates them")

case("aw-19", "I ate with Anna.", "awkward:comitative",
     Zip(rows=[c("e", "eat.v", agent=n("me.n"), comitative=n("anna.n", marker="with"))]),
     "pass", "COMITATIVE — the box neither VerbNet nor PropBank carries, and which the Captain's "
             "first draft had as `with` on day one. Without it Anna is a utensil.",
     distinct_from=("aw-18",))

case("aw-20", "Suppose the cat is hungry.", "awkward:supposition",
     Zip(rows=[thinks("sup", n("me.n"), scopes="h", verb="suppose.v"),
               c("h", experiencer=the("cat.n"), complement=n("hungry.a"))]),
     "pass", "supposition is an ATTITUDE, and it is what heart 16 reads to fire the feeling at the "
             "imagination gain rather than at full strength")

case("aw-21", "Close the door!", "awkward:imperative",
     Zip(rows=[thinks("want", n("me.n"), scopes="cl", verb="want.v", strength=0.9),
               c("cl", "close.v", truth=None, agent=n("you.n"), patient=the("door.n"))]),
     "pass", "imperative is POV(want) over an UNASSERTED row — tkzip req 7: no act type; the zip is "
             "consumed by a hardwired category and only the dispatcher is semantic. `strength` is "
             "where «please» and «would you mind» live.")

case("aw-22", "It will rain tomorrow.", "awkward:forecast",
     Zip(rows=[c("r", "rain.v", truth=0.7)],
         theatre=Theatre(interval=[1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], epoch=1)),
     "pass", "heart 17 verbatim — same zip shape, spacetime in the future, CONFIDENCE where truth "
             "will later sit. When tomorrow comes a NEW belief is minted; this one is never rewritten.")
