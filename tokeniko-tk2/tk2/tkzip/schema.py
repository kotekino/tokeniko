"""THE ZIP — one thought, as a flat list of fixed-shape rows.

This module is **frame** under the standing law of 2026-08-25: it is the shape in which anything can
be stated, it moves only by migration, and a change here is never a cast. Everything it *refers* to —
which words mark which role, which attitude verbs exist, which senses a word has — is knowledge and
lives in rows.

--------------------------------------------------------------------------------------------------
THE FIVE THINGS THIS SHAPE IS FOR
--------------------------------------------------------------------------------------------------
1. **Fixed arity, so two thoughts compare by arithmetic** (req 1). Every row has every box; a box
   that is not used is ABSENT FROM STORAGE and present in the shape. Fixed arity is a property of
   the schema, not of the storage (req 61) — measured: ~80% of every row is empty.
2. **An unbound slot is a VARIABLE, never a zero** (req 2). A missing agent, an unresolved sense and
   an unanswered question are the same thing at three depths, and the evaluator solves them with one
   search (evaluator req 5).
3. **Rows point at rows by NAME, never by nesting** (req 33). Nesting has no non-arbitrary depth
   limit; naming has none to choose. This is the Tseitin transformation.
4. **Row order is SCOPE order** (req 35), and the prefix carries five scope-bearing elements —
   quantifier, negation, modality, attitude, domain. Row order is therefore NEVER free for anything
   else, which is why `CONV` is its own operator and not `IMPLY` with the rows swapped (req 42).
5. **Content is defined, structure is compiled** (the second standing law). Function words become
   rows, operators, quantifiers and markers here; they never ask the dictionary a question.

--------------------------------------------------------------------------------------------------
WHAT IS DELIBERATELY NOT HERE
--------------------------------------------------------------------------------------------------
- **No mood field.** A question is «something is OPEN»; an imperative is POV(want) over an unasserted
  row; a supposition is POV(suppose); a forecast is a future theatre. Nothing was found that mood
  would have to store (req 48).
- **No cause, purpose or result relation.** All three are `IMPLY` read with the theatre's arrow of
  time (reqs 37, 40) — premise, stated rather than assumed: *in a deterministic world, a cause is
  what implies its effect*.
- **No catch-all slot, ever** (req 21). A typed `other` is the database option by the back door.
  Material that fits no box is a DIAGNOSTIC, outside the geometry, never compared.
- **No provenance, no `derived_by`, no `original`** (req 59). Those describe the BELIEF and live on
  the document; this describes the THOUGHT.
"""

from __future__ import annotations

from enum import Enum
from typing import Annotated, Literal, Union

from pydantic import BaseModel, ConfigDict, Field, model_validator


# The frozen shape. A change to anything in this module changes this number, and a zip carries the
# number it was compiled against (req 22) — E9's translation night has to know what it is translating.
#
# **v6, 2026-09-20 — A NOUN HAS A NUMBER, AND THE SPEAKER STATED IT.** «Software can be MINDS» and
# «software can be A MIND» compiled to the same box — `{head: mind.n}` and nothing else — so the
# decompiler had two renderings and both were wrong: «be mind» is not English, and «be a mind»
# measured the round trip DOWN from 65 to 61 of 87, because an article the zip does not hold comes
# back as a determination it did not have. **The third thing in two days found to be in the sentence
# and not in the zip**, after the sort of an unknown (v4) and the tense of a clause (v5).
#
# It is not `count`, which is a NUMERAL and orthogonal by req 26 — «the three cats» is definite AND
# counted AND plural, and v1's single field could say one of those at a time. It is not
# `determination` either: a bare plural has none. It is the grammatical number, which English marks
# on the noun and which the reader needs to say the noun at all.
#
# **v5, 2026-09-20 — THE THEATRE IS PER ROW.** It was one field on the ZIP, which made «I went to
# Rome and I will go to Genoa» unrecordable: two clauses, two times, one slot. The docstring had
# always called it *«the CLAUSE's spacetime»* and the field had always sat somewhere else. Ruled by
# the Captain the hour it was named — *«theatre must obviously be a field per row»* — and it goes
# exactly where the thing it describes lives, which is v3's own lesson about the addressee.
#
# **ON A CONTENT ROW AND ON AN ATTITUDE, AND NOWHERE ELSE.** A predication happens in spacetime and
# so does a saying — «John SAID that the sky IS green» is a past saying about a present sky, and
# since an attitude's own clause dissolves into the prefix row, that row is the only place its time
# can go. A JOIN has no time of its own: it is a logical relation between things that do, and req 37
# reads its arrow by comparing THEIR theatres. A quantifier, a negation, a modality and a domain
# have none either, and a slot that can only ever be empty is a slot this schema does not add.
#
# **v4, 2026-09-20 — WHAT IS KNOWN ABOUT WHAT IS NOT KNOWN.** `Open` said «this slot is unbound»
# and nothing else, so three different sentences compiled to one zip: «WHO ate the fish» and «WHAT
# ate the fish», «HE thinks» and «SHE thinks», «ITS cubs» and «HIS cubs». That is not a rendering
# problem — the restriction «a person» is CONTENT, and an evaluator that lost it would accept a rock
# as an answer to «who ate the fish?». Four optional fields on one class, and no stored zip to
# translate. **The Captain, ruling the field and the rule above it:** *«English says several
# different things with an unknown, the zip should record several types of unknown … not sure why
# you talk about "frozen" schemas: we are building from scratch … there are no frozen schemas.»*
#
# **v3, 2026-09-16 — THE ADDRESSEE. The first migration of a frozen schema, under the Captain's hand
# (req 73), and it is one field on two classes.** An attitude had a HOLDER and no addressee, so
# «John said TO MARIE: you are a clever girl» had nowhere to record who «you» is. The alternative
# was to leave the format alone and let the resolver read the `recipient` box of a `say` row — which
# adds nothing to the schema and asks the resolver to KNOW THAT SAYING-VERBS ARE SPECIAL, i.e. a
# closed set of verbs in code, which is what two days of this epic have been moving into rows.
# Ruled by the Captain: the field. Record: `docs/E3-parser-compiler/202609161349_the-person-axis.md`.
# **v7, 2026-09-21 — A NUMBER IS `sg` OR `pl`, AND THE FORMAT NOW REFUSES ANYTHING ELSE.** The
# column was `str | None`, and `both` · `neither` · `either` · `each other` carry `number: dual` in
# the closed-class rows — meaning *this word is about exactly TWO*, which is a fact about the SET
# and not the grammatical number of anything. `Compiler._unknown()` copies a row's `number` into the
# OPEN a described unknown carries (v4), so «I saw both» and «They praised each other» were
# compiling to `Open(number='dual')`: a value the field's own docstring does not admit, sitting in a
# zip, with nothing able to say it back.
#
# **The fourth time in two days that one column carried two facts** — after the fused quantifier
# (`db/0028`), the determiner's number (`db/0029`, where it was `takes_number` that had to be told
# apart from `number`), and the described unknown itself. Every one of them was a value written by a
# writer who meant something else, and every one was invisible until something downstream choked.
#
# A `Literal` is the cheap half of the answer: the format refuses what it cannot mean, so the next
# such value raises where it is WRITTEN instead of travelling. `db/0030` is the other half, moving
# the cardinality onto `count`, which is the column the table already uses for HOW MANY (`once` 1,
# `twice` 2) and which nothing on the unknown's path reads.
# **v8, 2026-09-21 — A BINDER MAY INTRODUCE A VARIABLE WITHOUT QUANTIFYING IT.** `quantity` was
# required, and a relative clause on a REFERRING phrase has no quantifier to take it from: «the cat
# that sleeps is happy» is one cat described twice, and req 36 says the variable is how a zip says
# «the same one». With no binder available the compiler minted a variable and bound it with nothing
# — so the clause referred to `y2`, the main clause referred to `y2`, **and `cat.n` was thrown away
# entirely**, because the restriction is the only place a binder's noun can live.
#
# The alternative was to keep `quantity` required and give the phrase `EXISTENTIAL` beside its
# `determination`. That fields exist for it is true (req 26 splits the two precisely so «the three
# cats» can be definite AND counted), but it would make the COMPILER invent a logical force from a
# determination — definite becomes existential, generic becomes universal? — for phrases whose
# sentence stated none. Saying more than the zip does is the sin req 8 names, and it is no better
# for being committed on the way in. **Ruled by the Captain.**
#
# So: a binder with no `quantity` introduces and restricts a variable and claims no force. The
# `determination` the speaker DID state rides on the restriction, as it always has.
#
# **v9, 2026-09-25 — AN UNDERSTOOD MARKER IS STORED, AND SO IS THE FACT THAT NOBODY SAID IT.** «I
# gave ANNA a book» and «I gave a book TO ANNA» are one thought — Anna receives — and the Captain
# ruled that the zip says so: a bare indirect object carries the marker English leaves out, the one
# the table gives the recipient (G7; tk1 did it before tk2 existed, `lib/llc/parser.py:891`, its
# marker's origin defaulting to «implicit», `lib/core/tk.py:77`). *The meaning is «to Anna»; the
# bareness is the surface.* And the surface is kept, because the decompiler must say it as it was
# said: «I asked TO Anna where…» dissolves the attitude it came from.
#
# ONE FIELD, `Box.marker_implicit`, and nowhere else: the marker lives on the box, so what is known
# about how it was said lives beside it. The alternative — leave `marker` empty and let a reader
# infer «to» from the role — would make every reader know that a recipient's marker is understood,
# which is a fact about English in code, and would leave «Anna» and «to Anna» two different zips.
SCHEMA_VERSION = 9


# --------------------------------------------------------------------------------------------------
# keys — what a slot points at when it is bound to a word
# --------------------------------------------------------------------------------------------------

# A base key is a word plus a part of speech: `eat.v`, `small.a`. It names a DIMENSION of the base
# (E1: 4,555 of them). A sense key is finer — `eat.v.01` — and names a row of the sense layer (E1c).
# Both are strings because the dictionary owns their grammar; this module only carries them.
BaseKey = Annotated[str, Field(min_length=1)]
SenseKey = Annotated[str, Field(min_length=1)]

# The name of a row, and the name of a variable a binder introduces. Short and zip-local: Tseitin
# names never cross thoughts (req 64), so a cross-thought reference is a document id, not a name.
RowName = Annotated[str, Field(min_length=1)]
VarName = Annotated[str, Field(min_length=1)]

# v7. Grammatical number: what the SPEAKER marked on a word. Never how many things are in a set —
# that is `count`, and it is what `dual` meant on the rows that used to put it here.
#
# **`either` IS THE THIRD ANSWER AND IT IS A REAL ONE.** English's «you» does not distinguish, and
# the table has said so since v1 with the same word its `case` column uses for the same idea; the
# decompiler's `_agrees()` has always read it as *matches whatever is asked*. So a zip may record
# that the speaker used a word that does not tell us — which is a different fact from the sentence
# saying nothing at all, and the round trip needs to keep them apart.
Number = Literal["sg", "pl", "either"]


# --------------------------------------------------------------------------------------------------
# binding — the three states, expressed so that EMPTY costs nothing to store
# --------------------------------------------------------------------------------------------------


class Open(BaseModel):
    """OPEN — a variable nobody binds: the thing to solve for.

    «Who ate the fish?» has an OPEN agent. «Is the cat hungry?» has an OPEN truth. An unresolved
    sense is an OPEN sense. They are one problem (evaluator req 5), and the brain may bind any of
    them by asking, by remembering, or by inference — which source is a choice made later, never a
    shape (req 49).

    `prior` is the one genuinely new scalar the drill bench found (req 50): «It's cold, isn't it?» is
    OPEN with a high expectation of *yes*; «Is it cold?» is OPEN with none. Not parse confidence —
    real semantic content.

    **AND WHAT IS KNOWN ABOUT IT IS NOT NOTHING** *(v4, 2026-09-20)*. An unbound slot is one shape at
    three depths (req 2), and the brain may bind it by asking, remembering or inferring (req 49) —
    but the SENTENCE usually said something about the thing it did not name, and until v4 every word
    of that was thrown away:

        «WHO ate the fish?»      the answer must be a PERSON — a restriction, and restrictions are
                                 content: without it a rock is an admissible answer
        «SHE thinks X»           third person, feminine, singular. The speaker stated all three
        «ITS cubs»               the same, in the possessor

    Three pairs of different sentences that compiled to one zip each. The fields carry exactly what
    the closed-class rows already record about the word that was used — same names, same values — so
    the compiler copies what it matched and the decompiler matches back, which is the symmetry the
    whole station is built on.

    **They are strings and integers, not enums**, for `BaseKey`'s reason: the table owns this
    vocabulary and this module only carries it. A new gender or a new sort is a migration, never a
    schema change.

    **EMPTY IS ALSO AN ANSWER.** A bare `Open` is an unknown nobody described — the unexpressed agent
    of «the hammer is made of titanium» — and that is why the decompiler can tell it from an asked
    slot without guessing from position.
    """

    model_config = ConfigDict(extra="forbid")

    prior: float | None = Field(default=None, ge=0.0, le=1.0)

    #: v4. What the sentence said about the thing it did not name.
    #: `sort` is the interrogative's own restriction — «who» asks for a person, «what» for a thing.
    sort: str | None = None
    person: int | None = None
    number: Number | None = None
    gender: str | None = None

    @property
    def described(self) -> bool:
        """Did the sentence say anything about it at all? A bare OPEN is an unknown nobody named."""
        return any(v is not None for v in (self.sort, self.person, self.number, self.gender))


class Var(BaseModel):
    """BOUND — to a variable introduced by a binder row, not to a word.

    «Someone ate the fish» binds an existential and puts it in the agent box: the agent is KNOWN TO
    EXIST and unidentified, which is not the same as being asked about. That distinction is why
    `EMPTY`, `Var` and `Open` are three different things and v1's single `*` was not enough.
    """

    model_config = ConfigDict(extra="forbid")

    name: VarName


class Ref(BaseModel):
    """BOUND — to another ROW of this zip, by name.

    Requirement 34 says a box may hold a row name, valued by that row's derived point; the first cut
    of this module had no type for it, and the drill found the hole:

        «Cognition is the psychological result OF PERCEPTION AND LEARNING AND REASONING»

    The `relation` of *result* is a three-way coordination — a join row — not a word. Without `Ref`
    the row name would validate as a bare string and the evaluator would go looking for «j2» in the
    dictionary. FORCED BY THE DRILL, 2026-09-14.

    Distinct from `Var`: a variable is bound by a prefix row and ranges; a reference names a
    proposition already written down.
    """

    model_config = ConfigDict(extra="forbid")

    row: RowName


# EMPTY is the absence of the field. There is no `Empty` marker and there must not be: a stored
# marker for «nothing here» would cost a field on every unused slot, and ~80% of every row is unused.


# --------------------------------------------------------------------------------------------------
# the closed alphabets — frame, because mathematics or shape, never because English happens to mark it
# --------------------------------------------------------------------------------------------------


class Role(str, Enum):
    """The seventeen boxes. FRAME: fixed, exhaustive, and a miss is a bug to be fixed by redesigning
    the frame — never a migration (req 18, the Captain's ruling of 2026-09-11).

    Cut from VerbNet (29 thematic roles over 429 classes), PropBank (112,917 annotated sentences) and
    FrameNet (1,221 frames), then cross-checked against the Captain's own first draft — which already
    had `comitative`, a box neither computational inventory carries.

    Named and VERB-INDEPENDENT (req 19): box N means the same thing in every zip. PropBank's numbered
    convention (`ARG2` = recipient for *give*, substance for *fill*) would make «I gave the book to
    Anna» and «I filled the glass with water» compare Anna against water.
    """

    # participants
    AGENT = "agent"
    PATIENT = "patient"
    EXPERIENCER = "experiencer"
    RECIPIENT = "recipient"
    BENEFICIARY = "beneficiary"
    INSTRUMENT = "instrument"
    SOURCE = "source"
    DESTINATION = "destination"
    COMPLEMENT = "complement"
    TOPIC = "topic"
    MEASURE = "measure"
    # circumstances
    LOCATION = "location"
    # FORCED BY THE DRILL, 2026-09-14 — «He looked UP» · «She turned LEFT». A direction with no
    # endpoint: not a destination (he does not arrive at *up*), not a path (it is not a route), not a
    # manner. The marker cannot rescue it because there is no box to mark. PropBank keeps ARGM-DIR
    # separate (1,419 uses) and FrameNet has Direction beside Path and Goal; the first cut of this
    # inventory had source, path and destination and simply missed the fourth.
    DIRECTION = "direction"
    TIME = "time"
    MANNER = "manner"
    DURATION = "duration"
    PATH = "path"
    COMITATIVE = "comitative"


class Operator(str, Enum):
    """The ten non-degenerate binary truth functions. FRAME, closed by MATHEMATICS (req 41).

    Not trimmed to the six English marks. Trimming would restrict what tokeniko can THINK to what
    English can SAY, and he computes operators nobody uttered — self-talk, derived thought, a chained
    theorem. Which of these English marks is knowledge and lives in `language_closed_classes`.

    Six of the sixteen binary functions are excluded because they are degenerate — `TRUE`, `FALSE`,
    `A`, `¬A`, `B`, `¬B` ignore an input and are not joins at all. Negation of a single row is a
    property of that row, not an operator.

    `CONV` is NOT `IMPLY` with the operands swapped: row order carries scope (req 35, 42).
    """

    AND = "and"
    NAND = "nand"
    OR = "or"
    NOR = "nor"
    XOR = "xor"
    EQ = "eq"
    IMPLY = "imply"
    NIMPLY = "nimply"
    CONV = "conv"
    NCONV = "nconv"


class Quantity(str, Enum):
    """Logical force. Split from determination because the two are ORTHOGONAL (req 26, OQ7): «the
    three cats» is definite AND counted, «not all the cats» is negated-universal AND definite, and
    v1's single seven-valued field could say only one of the two at a time."""

    UNIVERSAL = "universal"
    NEGATED_UNIVERSAL = "negated_universal"
    EXISTENTIAL = "existential"
    NEGATIVE = "negative"


class Determination(str, Enum):
    """Which ones — orthogonal to how many. Definiteness is also part of the scoping mechanism."""

    DEFINITE = "definite"
    INDEFINITE = "indefinite"
    GENERIC = "generic"


class Modality(str, Enum):
    """□ and ◇. A modal claim is not a crisp assertion — `◇P ∧ ◇¬P` is consistent — so the kernel
    never treats it as P and the extractor never mints a rule from it."""

    NECESSITY = "necessity"
    POSSIBILITY = "possibility"


# --------------------------------------------------------------------------------------------------
# the box — seven fields, because a noun phrase is not one cell
# --------------------------------------------------------------------------------------------------


class Box(BaseModel):
    """One filled role: the Captain's own noun-phrase record, from the first draft (`part` · `rel` ·
    the noun), grown to seven fields as later tasks found what it was missing.

    The record is PER NOUN PHRASE, not one per clause read off the subject — v1's limit, which cannot
    say «all cats eat some fish».

    Every field is independently bindable (req 47): `head` may be BOUND while `sense` is OPEN (the
    parser emits the lemma with the sense slot open — brain req 7), `count` may be OPEN («how many
    cats?»), `relation` may be OPEN («whose cat?»). A field that is absent is EMPTY.

    `head` is req 26's `noun`, renamed for what it actually holds: a `manner` box holds an adverb and
    a `complement` box holds an adjective, so `noun` would be a name doing the wrong job for two of
    the seventeen. Same field, clearer name.
    """

    model_config = ConfigDict(extra="forbid")

    quantity: Quantity | Open | None = None
    count: int | Var | Open | None = None
    determination: Determination | Open | None = None

    # The possessor: «my cat» → `relation` = the key for *me*. A relation, not a role: it holds
    # BETWEEN this phrase and something else, which is why it lives inside the record.
    relation: BaseKey | Var | Ref | Open | None = None

    head: BaseKey | Var | Ref | Open | None = None
    sense: SenseKey | Open | None = None

    #: v6. The grammatical number the speaker used — `sg` or `pl`. EMPTY where nothing said it: a
    #: mass noun has none, and neither does a box the brain built for itself. Orthogonal to `count`
    #: (a numeral) and to `determination` (which ones), exactly as req 26 keeps those two apart.
    #: **v7 made it a `Literal`**, after `dual` reached a zip through it.
    number: Number | None = None

    # The preposition actually used, as a lemma (req 65). The marker words are already
    # `language_closed_classes` rows, so this records WHICH ROW WAS MATCHED, not new knowledge.
    # Without it «I walk TO the station» and «I walk TOWARD the station» are the same zip, and they
    # do not mean the same thing. v1 carries markers for exactly this reason and says so.
    marker: str | None = None

    #: v9. True when `marker` was UNDERSTOOD rather than said — «I gave ANNA a book» carries `to`,
    #: the recipient's marker from the table, because the meaning is «to Anna». EMPTY when the
    #: marker was written, or there is none: only the unusual case costs a stored field. Surface,
    #: like `topicality`: it enters no arithmetic, and the decompiler reads it to say the box bare.
    marker_implicit: bool | None = None

    # Degree rides what it modifies rather than earning a box (req 23): «very tall» attaches to the
    # complement, «very slowly» to the manner. It is an intensifier on another part, not a part.
    degree: float | None = Field(default=None, ge=0.0, le=1.0)


class Pov(BaseModel):
    """The point of view — the Captain's own column, from the first draft: «my cat is cute» carries
    POV `me / think`.

    This is SHORTHAND for an attitude at one fixed prefix position (req 45), not a second mechanism.
    When a quantifier has to scope in or out of the attitude — de re versus de dicto — the attitude
    takes an explicit `AttitudeRow` instead, and the two readings become row order like everything
    else. A flat-only POV does not abstain on that distinction: it silently forces DE RE, and would
    put a unicorn in the KB as existing.

    `strength` is where the gradation of «close the door» → «would you mind closing the door» lives:
    the strength of the wanting, not a mood scalar (req 51).

    **`addressee` IS v3'S ONE ADDITION** — the person the attitude is DIRECTED AT, which an attitude
    with only a holder cannot say. It is what a first- and second-person pronoun inside the attitude
    rotates against: «John said TO MARIE: **you** are a clever girl» means Marie, and it means her
    because the saying was addressed to her. **EMPTY unless the verb has one** — thinking addresses
    nobody, and a `None` here is the difference between «no addressee» and «addressed to someone
    unknown», which is `Open()`.
    """

    model_config = ConfigDict(extra="forbid")

    holder: Box
    verb: BaseKey
    #: v3. Empty for an attitude that addresses nobody — most of them.
    addressee: Box | None = None
    strength: float | None = Field(default=None, ge=0.0, le=1.0)

    #: v5. WHEN the attitude is held — «John SAID» is past whatever tense its content is in. It moves
    #: with `AttitudeRow`'s for req 45's reason: the two are one mechanism in two spellings, and a
    #: field on one and not the other would make the shorthand say less than the explicit form.
    theatre: "Theatre | None" = None


# --------------------------------------------------------------------------------------------------
# the rows
# --------------------------------------------------------------------------------------------------


class _Row(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: RowName


class _Claimable(_Row):
    """A row that can carry a truth claim.

    THE TRUTH SLOT IS THE ASSERTION STATUS, and the two turned out to be one field with three
    readings — which is why nothing else in this schema records «is this asserted?»:

      BOUND (a float)  the row is CLAIMED, fuzzily. When the theatre is future this same slot holds
                       forecast CONFIDENCE — «confidence where truth will later sit» (heart 17). A
                       resolved forecast mints a NEW belief; this value is never rewritten (req 60).
      OPEN             the row is ASKED. «Is the cat hungry?» has every box bound and its truth open.
      EMPTY (absent)   the row is STATED BUT NOT CLAIMED — the antecedent of «if it rains, I stay
                       home». The join is what is asserted there, not the halves.

    That last line is what separates «because» from «if» (req 38): same `IMPLY`, rows claimed or not.
    And it is read by the HEART as well as the evaluator — suppositions fire at the imagination gain
    (heart 16) — so it must be first-class and visible, never an internal detail of a search (req 56).
    """

    truth: float | Open | None = None


class ContentRow(_Claimable):
    """An atom: a predicate and its boxes.

    `predicate` is absent for plain copular `be`, which compiles to structure and earns no dimension
    (req 31) — so «the cat is cute» comes out as *cat + cute, no verb*, exactly as the first draft had
    it, while `become`, `seem` and `remain` keep a home. Existential `be` («there is a cat») is
    content, not glue, and does fill it.

    `boxes` is SPARSE by construction: only filled roles appear. Measured on PropBank's 112,917
    predicate instances, the mean is 2.59 roles of eighteen slots.
    """

    kind: Literal["content"] = "content"

    #: v5. WHEN this predication is set, relative to the utterance. EMPTY when nothing said — a
    #: tenseless zip is one the brain built for itself, and 1.0 would claim a present nobody stated.
    theatre: "Theatre | None" = None

    predicate: BaseKey | Var | Open | None = None
    predicate_sense: SenseKey | Open | None = None

    boxes: dict[Role, Box] = Field(default_factory=dict)

    pov: Pov | None = None


class JoinRow(_Claimable):
    """`Y = A AND B` — the Tseitin combination, and the only way rows are joined.

    Every join is explicit and names its operands, so nothing depends on an implicit «previous row».
    Row order is already carrying scope (req 35) and cannot be asked to carry adjacency as well.

    The join is itself claimable, and that is load-bearing:

        «if it rains, I stay home»          join CLAIMED, both halves EMPTY
        «I stayed home because it rained»   join CLAIMED, both halves CLAIMED
        «it rained and I stayed home»       AND, both halves CLAIMED

    All three are distinguishable, with one operator set and no relation field.
    """

    kind: Literal["join"] = "join"

    operator: Operator
    operands: Annotated[list[RowName], Field(min_length=2, max_length=2)]


class _PrefixRow(_Row):
    """A scope-bearing element: quantifier · negation · modality · attitude · domain (req 35).

    `scopes` NAMES THE ROW THIS APPLIES TO — forced by the drill, 2026-09-14, from the Captain's own
    traffic:

        «software CAN be minds and humans MUST be minds»

    `◇A ∧ □B`: two different modalities over two conjuncts. An element that scoped over «everything
    after it» could not express that — put ◇ first and it swallows B as well. The same shape breaks
    for attitudes («Anna thinks X and Bob thinks Y») and for domains («legally P but actually Q»).

    Because a named row may itself be a JOIN covering a whole subtree, naming the target gives
    arbitrary nesting for free — the Tseitin machinery paying for itself a second time.

    **Row order = scope order survives, refined**: it orders prefix elements relative to each other
    WHEN THEY SCOPE THE SAME TARGET. «Every man loves a woman» is still two binders over one content
    row, and their order is still the difference between ∀>∃ and ∃>∀.

    `scopes` NAMES A MATRIX — a content row or a join row — and NEVER another prefix row. That is the
    constraint that keeps «row order = scope order» true: nesting among prefix elements is their
    ORDER, and `scopes` only says which matrix they are nesting over. Without it, `¬∀` could be
    spelled two ways — by chaining pointers, or by sibling order — and two spellings of one reading is
    the thing this schema keeps refusing.

        ¬∀X P    neg, then ∀X, both scoping P
        ∀X ¬P    ∀X, then neg, both scoping P
        ◇A ∧ □B  ◇ scoping A, □ scoping B — different matrices, so order between them says nothing

    Required, never defaulted: a default of «everything after» would be a third spelling.
    """

    scopes: RowName


class QuantifierRow(_PrefixRow):
    """A binder: introduces a variable and restricts it.

    «All cats are mammals» becomes a binder for X restricted to cats, then a content row saying X is a
    mammal. That costs an indirection on every quantified comparison — the variable dereferences to
    its binder's derived point — and buys ONE binding mechanism for quantification, questions,
    equations and naming (req 36). Under the alternative, a quantified noun phrase is not a variable
    at all and the evaluator has to synthesise one the schema never wrote down.
    """

    kind: Literal["quantifier"] = "quantifier"

    binds: VarName

    #: v8. EMPTY where the phrase quantified nothing — «the cat that sleeps» needs a variable so the
    #: relative clause and the main clause can be about one cat, and it states no logical force. A
    #: reader that wants to know «how many» asks this and gets the honest answer, including None.
    quantity: Quantity | None = None
    count: int | Open | None = None
    determination: Determination | None = None

    # «all CATS» — the restriction on the variable's range.
    restriction: Box


class NegationRow(_PrefixRow):
    """¬ in the prefix, so «not all that glitters is gold» and «nothing that glitters is gold» are two
    zips rather than one.

    **NOT for negating a single row.** «I'm not a software but I am a mind» negates one half of a
    conjunction, and that is `truth = 0.0` — claimed false. This row is for negation that must scope
    OVER another prefix element, which is the only case where the order matters. The drill settled
    the division and it costs no new field.

    v1 had no prefix and patched a single ¬/∀ combination into its quantifier enum
    (`NEGATED_UNIVERSAL`). A prefix handles the whole class, and the enum value survives here only for
    the reading where the negation genuinely belongs to the quantifier.
    """

    kind: Literal["negation"] = "negation"


class ModalityRow(_PrefixRow):
    """□ / ◇ in the prefix — because modality SCOPES.

    «Every student must pass» has two readings (∀>□, each is required; □>∀, it is required that all
    do). That is scope-bench case C, and it is why modality could not remain a flat clause field as
    v1 has it — a constraint task 3 inherited rather than chose.
    """

    kind: Literal["modality"] = "modality"

    modality: Modality


class AttitudeRow(_PrefixRow):
    """An attitude in the prefix — the explicit form of `Pov`, used when a quantifier must scope in or
    out of it.

        de dicto:  [he thinks] [∃X cat] | X in garden      ← no cat asserted
        de re:     [∃X cat] [he thinks] | X in garden      ← cat asserted

    `verb` is a key, not a member of an enum. v1's four-valued `klass` (factive · doxastic ·
    desiderative · reportative) is a category-3 set wearing a list's clothes: attitude verbs are open
    — think, believe, suppose, want, fear, pretend, hope, doubt — so the classification is nearest-
    anchor geometry over a small anchor set, and never misses the verb nobody thought of (req 55).
    """

    kind: Literal["attitude"] = "attitude"

    #: v5, and it moves with `Pov`'s. «John SAID that the sky IS green» is a past saying about a
    #: present sky, and the saying's own clause is this row.
    theatre: "Theatre | None" = None

    holder: Box
    verb: BaseKey
    #: v3, and it moves with `Pov`'s — the two are one mechanism in two spellings (req 45), so a
    #: field on one and not the other would make the explicit form say LESS than the shorthand.
    addressee: Box | None = None
    strength: float | None = Field(default=None, ge=0.0, le=1.0)


class DomainRow(_PrefixRow):
    """The context a claim holds in — «legally» · «in chess» · «as a doctor» · «in Italy».

    This is requirement 6 («scope rides inside, so a contextual defeat is never relearned») satisfied
    with NO NEW MACHINERY: a domain is simply the fifth prefix element. It is what lets «as a doctor I
    disagree; as a father I understand» be two positions honestly held rather than a KB contradiction
    (rules reqs 6-7).

    There is no `type` column — jurisdiction, game, capacity, framework. Nothing reasons differently
    across them; the evaluator treats every one as «P holds indexed to D», and a type column would be
    a category-3 set enumerated in code.

    Provably not the `location` box: «In Italy, you may drive IN FRANCE with a foreign licence» needs
    both at once.
    """

    kind: Literal["domain"] = "domain"

    domain: Box


Row = Annotated[
    Union[
        ContentRow,
        JoinRow,
        QuantifierRow,
        NegationRow,
        ModalityRow,
        AttitudeRow,
        DomainRow,
    ],
    Field(discriminator="kind"),
]


# --------------------------------------------------------------------------------------------------
# the caches — derived, epoch-stamped, and never the truth
# --------------------------------------------------------------------------------------------------


#: **THE VERSION OF THE STATION'S TIME-RESOLUTION LOGIC**, stamped on every theatre it derives.
#: Requirement 63 is why it exists: recomputing «yesterday» years later needs the utterance timestamp
#: AND the logic that read it, so a theatre that could not say which logic wrote it would be a cache
#: nobody can invalidate. It starts at 1, which is what the drill hand-wrote for its one forecast,
#: and it moves when the reading moves — never when the vocabulary does.
THEATRE_EPOCH = 1


class Theatre(BaseModel):
    """The clause's spacetime, as four axis pairs — `[t_from,t_to][x][y][z]` — the Captain's own
    column from the first draft, and the same width as v1's denormalization map.

    DERIVED, not a replacement for the boxes (req 25). «I went from Rome to Genoa» keeps Rome and
    Genoa as fillers, because *«Genoa is a thing you can reason about: it's a city, somebody is born
    there»* — the evaluator must answer «where does he work?» with *the kitchen*, not with
    coordinates.

    Stored as a CACHE (req 63): recomputing «yesterday» years later needs the utterance timestamp AND
    the station's version-dependent resolution logic. Truth is the filler plus the timestamp.
    """

    model_config = ConfigDict(extra="forbid")

    #: `[t_from, t_to][x][y][z]`. **The time axis is relative to the utterance** — -1 before it, 0
    #: at it, +1 after it — which is the convention the drill's own forecast used (`aw-22`) and the
    #: one the station writes from the tense it hears. Space stays empty until a filler puts
    #: something there: nothing in a tense says WHERE.
    interval: Annotated[list[float], Field(min_length=8, max_length=8)]
    epoch: int


class GeometryCache(BaseModel):
    """The role vectors, sparse, keyed by `<row name>.<role>`.

    THE KEY IS THE TRUTH; THE VECTOR IS A CACHE (dictionary req 13 — «derived vectors are a cache in
    the zip, recomputable, so cosine runs in the DB»). The consequence is the one that matters: a
    dictionary rebuild invalidates only this object, never the meaning, so E9's translation night is
    for a SCHEMA change and never for a new base. Re-derivation is ~9 lookups per sentence.

    Affordable because E1c's sense vectors average 6.78 cells of 4,555 — the cache costs less than a
    doubling of the zip.

    ONE epoch for the whole cache, not one per vector: every vector here was derived at the same time
    against the same base, and a per-vector stamp would restate that on every entry. Redundancy that
    can disagree with itself is worse than no stamp, because the reader cannot tell which half lies —
    the same argument that kept `sphere` off the heart's level rows and `epoch_layer` off the derived
    points.
    """

    model_config = ConfigDict(extra="forbid")

    epoch: int
    vectors: dict[str, list[tuple[int, float]]] = Field(default_factory=dict)


# --------------------------------------------------------------------------------------------------
# the zip
# --------------------------------------------------------------------------------------------------


class Zip(BaseModel):
    """One thought.

    A flat list of rows, ordered by scope, joined by name. Self-contained: Tseitin names never cross
    thoughts, so a cross-thought reference is a document id and this object can be embedded whole
    (req 64).
    """

    model_config = ConfigDict(extra="forbid")

    schema_version: int = SCHEMA_VERSION

    rows: Annotated[list[Row], Field(min_length=1)]

    # Which role the speaker foregrounded (req 27). Roles NORMALIZE — «the fish was eaten by the cat»
    # compiles with cat as agent, so it compares as one thought with «the cat ate the fish» — and this
    # one marker keeps what normalization would otherwise destroy: that the speaker chose to talk
    # about the fish. It enters no arithmetic; the renderer reads it to speak the sentence back in the
    # voice it was heard in (req 9).
    topicality: Role | None = None

    # «This zip IS what I received» — coverage, repairs taken, self-round-trip, aggregated and
    # calibrated (parser-compiler req 4). ONE number for the whole zip, because its calibration signal
    # — «did the speaker correct me?» — arrives per utterance: a per-row scalar would have no training
    # signal and could never come to MEAN anything. Per-part doubt is carried by binding state and
    # prior instead: a half-heard word is OPEN, never BOUND to a guess with a low number.
    #
    # EMPTY when no parse happened — self-talk invokes no parser, and 1.0 would claim perfect
    # understanding of an utterance that never existed (req 58).
    parse_confidence: float | None = Field(default=None, ge=0.0, le=1.0)

    # **THE THEATRE LEFT THIS CLASS AT v5** and went to the rows, where the clause it describes
    # lives. One slot for a whole thought could not say «I went to Rome and I WILL GO to Genoa».
    geometry_cache: GeometryCache | None = None

    # Material no box fits: recorded, never compared, never given a position (req 21). NOT a slot and
    # not a typed `other` — the moment two leftovers need to know whether they are the same kind of
    # leftover, a role registry has been built by accident, un-curated and unsealed. The compiler is
    # the thing that knows it failed to place these words; throwing that away means re-deriving it
    # later, expensively and imperfectly.
    unplaced: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _check_names_and_scopes(self) -> "Zip":
        """Three invariants that cost nothing here and would cost a great deal downstream."""
        names = [r.name for r in self.rows]
        if len(names) != len(set(names)):
            raise ValueError("row names must be unique within a zip")

        claimable = {r.name for r in self.rows if isinstance(r, (ContentRow, JoinRow))}
        for r in self.rows:
            if isinstance(r, _PrefixRow) and r.scopes not in claimable:
                raise ValueError(
                    f"row {r.name!r} scopes {r.scopes!r}, which is not a content or join row — a "
                    "prefix element nests over a MATRIX; nesting among prefix elements is row order"
                )
            if isinstance(r, ContentRow):
                for role, box in r.boxes.items():
                    for slot in (box.head, box.relation):
                        if isinstance(slot, Ref) and slot.row not in names:
                            raise ValueError(
                                f"row {r.name!r} box {role.value!r} references unknown row "
                                f"{slot.row!r}"
                            )
            if isinstance(r, JoinRow):
                for operand in r.operands:
                    if operand not in names:
                        raise ValueError(f"join {r.name!r} names unknown operand {operand!r}")
        return self

    def row(self, name: str) -> Row | None:
        """The row with this name, or None. Names are zip-local, so this never leaves the thought."""
        for r in self.rows:
            if r.name == name:
                return r
        return None
