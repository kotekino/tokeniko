"""0004 — English's closed classes become typed rows.

The standing law of 2026-08-25, both halves of it. Test 2 of the FRAME test: a closed grammatical
class is «a contingent fact about one language, dialect-varying and revisable», therefore knowledge,
therefore rows. And the second law of the same day says what the rows are for — **content is
defined, structure is compiled**: what is written down here is the vocabulary that never earns a
dimension, because it becomes structure in the zip instead.

ONE TABLE, TWO CONSUMERS (`plan.md` E3 task 0, born early because E1 needed it): the seed proposal
excludes these forms from the definition digraph's in-degree ranking, and E3 compiles with them,
retiring tk1's `_ANAPHORIC_PRONOUNS`, `_QUANTIFIER_*`, `_WH_*` and `_RELATIVE_PRONOUNS`.

**NOT APPLIED BY THE OFFICER.** This file is written and reported; the apply is the Captain's hand.

HOW COMPLETENESS WAS ESTABLISHED — because «be exhaustive» is a claim, and a claim needs a method:

  1. THE FRAME is the Penn Treebank's closed tag inventory, which is the standard enumeration of
     exactly this question: DT/PDT (determiners), IN (prepositions and subordinators), CC
     (coordinators), PRP/PRP$ (personal and possessive pronouns), WDT/WP/WP$/WRB (the wh-words), MD
     (modals), EX (existential *there*), RP (verb particles), TO, POS (the genitive clitic). Every
     tag is walked and its members written out; a tag with no rows would be a hole with a name.
  2. THE CROSS-CHECKS are three, and they are TESTS (`tests/test_closed_classes.py`), not a memory:
     every one of tk1's four hand lists is covered (the table must be able to replace them);
     nltk's 198 English stop words are covered but for a residue declared word by word in the test
     — the de-apostrophised fragments (`aren`, `didn`, `ma`, and the bare letters `d ll m o re s t
     ve y`, whose structural halves `n't` `'s` `'re` `'ve` `'ll` `'d` `'m` ARE rows) and eight
     content and degree words (`again`, `further`, `just`, `only`, `own`, `same`, `too`, `very`)
     that sit on the declared edge of the table rather than inside it; and no form in the
     dictionary's declared seeds is silently also a row (the overlaps that DO exist are listed
     below and are the Captain's to rule on).
  3. WHAT IS OUT, and why, is written at the head of `tk2/core/models/language.py`: numerals
     (productive), interjections (open), `-ly` adverbs derived from open adjectives (a rule, not a
     roster), proper names (a different refusal, already built).

THE OVERLAPS WITH E1's SEEDS, surfaced rather than resolved — the officer does not rule on them:

  - `must` and `need` are declared seeds of the volitional family AND modal auxiliaries. Their
    modal reading compiles (`must go`); their content reading is a real word (`need.v` = «require
    as useful»). Same form, two readings, and the table says so — see «a form is not a reading» in
    the model's docstring.
  - `being` is the identity family's new seed («the state or fact of existing») AND the progressive
    form of `be`. That is the same shape and is the Captain's stated exception: the noun earns a
    dimension, the auxiliary form compiles.

Version 1 of the table. A change is version 2 written WHOLE, never an edit of these rows.
"""

from tk2.core.models import ALL_MODELS, LEDGER_MODELS, ClosedClassDoc
from tk2.migrations import ensure_collections

VERSION = 1

#: Where the inventory was walked from. Recorded per row, so «is this complete?» is answered by
#: re-walking a named source rather than by re-remembering what was thought of.
PTB = "Penn Treebank closed tag inventory (DT PDT IN CC PRP PRP$ WDT WP WP$ WRB MD EX RP TO POS)"
CGEL = "standard reference grammar of English (closed-class inventories)"
TK1 = "tk1 lib/llc/constants.py — the hand list this table retires"

# ------------------------------------------------------------------------------------------------
# 1 — REFERENTIAL: the forms that resolve to an ENTITY from context
# ------------------------------------------------------------------------------------------------
#
# The second standing law's first consequence. A pronoun is indexical — `me` means whoever is
# speaking — so it is resolved to an entity at parse time and the dictionary is never asked; the
# self-model is carried by `kotekino` and `tokeniko` as named individuals (uid + type-centroid),
# never by a pronoun's dimension. `features` carries what the resolver needs and the spelling does
# not give it: person, number, gender, case.
#
# `you` and `it` hold one row each with case "either": English stopped distinguishing their
# nominative and accusative, and inventing two identical rows would invent a distinction the
# language does not make.

PERSONAL = (
    ("i", {"person": 1, "number": "sg", "case": "nominative"}, ""),
    ("me", {"person": 1, "number": "sg", "case": "accusative"}, ""),
    ("we", {"person": 1, "number": "pl", "case": "nominative"}, ""),
    ("us", {"person": 1, "number": "pl", "case": "accusative"}, ""),
    ("you", {"person": 2, "number": "either", "case": "either"}, "number and case both syncretic"),
    ("he", {"person": 3, "number": "sg", "gender": "m", "case": "nominative"}, ""),
    ("him", {"person": 3, "number": "sg", "gender": "m", "case": "accusative"}, ""),
    ("she", {"person": 3, "number": "sg", "gender": "f", "case": "nominative"}, ""),
    ("her", {"person": 3, "number": "sg", "gender": "f", "case": "accusative"},
     "also the possessive determiner — two rows, two jobs"),
    ("it", {"person": 3, "number": "sg", "gender": "n", "case": "either"}, ""),
    ("they", {"person": 3, "number": "pl", "case": "nominative"},
     "singular `they` is legal and unresolved is legal: an unbound variable at low confidence, and "
     "the brain may ask"),
    ("them", {"person": 3, "number": "pl", "case": "accusative"}, ""),
    ("one", {"person": 3, "number": "sg", "gender": "n", "case": "either"},
     "the impersonal pronoun («one does not simply»); also a numeral, which is NOT this row"),
    ("thou", {"person": 2, "number": "sg", "case": "nominative"}, "archaic: read, never produced"),
    ("thee", {"person": 2, "number": "sg", "case": "accusative"}, "archaic"),
    ("ye", {"person": 2, "number": "pl", "case": "nominative"}, "archaic"),
)

POSSESSIVE_DETERMINERS = (
    ("my", {"person": 1, "number": "sg"}, ""),
    ("our", {"person": 1, "number": "pl"}, ""),
    ("your", {"person": 2, "number": "either"}, ""),
    ("his", {"person": 3, "number": "sg", "gender": "m"}, ""),
    ("her", {"person": 3, "number": "sg", "gender": "f"}, ""),
    ("its", {"person": 3, "number": "sg", "gender": "n"}, ""),
    ("their", {"person": 3, "number": "pl"}, ""),
    ("thy", {"person": 2, "number": "sg"}, "archaic"),
    ("whose", {"wh": True}, "the interrogative/relative possessive — its wh row is separate"),
)

POSSESSIVE_PRONOUNS = (
    ("mine", {"person": 1, "number": "sg"}, ""),
    ("ours", {"person": 1, "number": "pl"}, ""),
    ("yours", {"person": 2, "number": "either"}, ""),
    ("his", {"person": 3, "number": "sg", "gender": "m"}, "syncretic with the determiner"),
    ("hers", {"person": 3, "number": "sg", "gender": "f"}, ""),
    ("its", {"person": 3, "number": "sg", "gender": "n"}, "vanishingly rare, and legal"),
    ("theirs", {"person": 3, "number": "pl"}, ""),
    ("thine", {"person": 2, "number": "sg"}, "archaic"),
)

REFLEXIVES = (
    ("myself", {"person": 1, "number": "sg"}, ""),
    ("ourselves", {"person": 1, "number": "pl"}, ""),
    ("yourself", {"person": 2, "number": "sg"}, ""),
    ("yourselves", {"person": 2, "number": "pl"}, ""),
    ("himself", {"person": 3, "number": "sg", "gender": "m"}, ""),
    ("herself", {"person": 3, "number": "sg", "gender": "f"}, ""),
    ("itself", {"person": 3, "number": "sg", "gender": "n"}, ""),
    ("themselves", {"person": 3, "number": "pl"}, ""),
    ("themself", {"person": 3, "number": "sg"}, "singular `they`'s reflexive"),
    ("oneself", {"person": 3, "number": "sg"}, "the impersonal `one`'s reflexive"),
)

RECIPROCALS = (
    ("each other", {"number": "dual"}, "multi-word: one operator, never two role markers"),
    ("one another", {"number": "pl"}, "multi-word"),
)

#: Deictic pro-adverbs: `here` is a PLACE resolved from context exactly as `me` is a person, and the
#: dictionary is no more use for one than for the other. `there` holds a second row below as the
#: existential — «there is a cat» posits, it does not point.
DEICTIC_ADVERBS = (
    ("here", {"deixis": "place", "distance": "proximal"}, ""),
    ("there", {"deixis": "place", "distance": "distal"}, "also the existential — two rows"),
    ("now", {"deixis": "time", "distance": "proximal"}, ""),
    ("then", {"deixis": "time", "distance": "distal"}, ""),
)

DEMONSTRATIVES = (
    ("this", {"number": "sg", "distance": "proximal"}, ""),
    ("that", {"number": "sg", "distance": "distal"},
     "also the relative pronoun and the complementizer — three jobs, three rows"),
    ("these", {"number": "pl", "distance": "proximal"}, ""),
    ("those", {"number": "pl", "distance": "distal"}, ""),
)

# ------------------------------------------------------------------------------------------------
# 2 — QUANTIFICATIONAL: a quantifier, never a referent
# ------------------------------------------------------------------------------------------------
#
# tk1 read these off the subject's determiner and called the answer a corner of the square of
# opposition; the corner is E2/E3's to fill (`compiled`), and what belongs here is the roster.
#
# ONE ROW, not two, where a form is both determiner and pronoun («all cats» / «all are here»): the
# quantifier is the same operator in both, and the syntactic difference is the parser's to see. The
# forms English DOES distinguish (`my`/`mine`) get two rows above, because there the language made
# the distinction and we would be erasing it.

QUANTIFIER_DETERMINERS = (
    ("all", {"force": "universal"}, "also a predeterminer («all the cats»)"),
    ("every", {"force": "universal"}, ""),
    ("each", {"force": "universal", "distributive": True}, ""),
    ("both", {"force": "universal", "number": "dual"}, "also the correlative «both … and»"),
    ("some", {"force": "existential"}, ""),
    ("any", {"force": "existential", "polarity": "negative-context"}, ""),
    ("several", {"force": "existential"}, ""),
    ("a", {"force": "indefinite"}, "the indefinite article; tk1 split it from EXISTENTIAL on "
     "purpose — «a X is a Y» reads generic, «some X are Y» does not"),
    ("an", {"force": "indefinite"}, "`a` before a vowel; WordNet also spells it AN (a nursing "
     "degree), which the name refusal already removes from the base"),
    ("the", {"force": "definite"}, "the definite article"),
    ("no", {"force": "negative"}, "the determiner («no money»); the negation particle is its own row"),
    ("neither", {"force": "negative", "number": "dual"}, "also the correlative «neither … nor»"),
    ("either", {"force": "disjunctive", "number": "dual"}, "also the correlative «either … or»"),
    ("many", {"force": "many"}, ""),
    ("much", {"force": "many", "mass": True}, ""),
    ("few", {"force": "few"}, ""),
    ("little", {"force": "few", "mass": True}, "the quantifier; the adjective «small» is a word"),
    ("more", {"force": "comparative", "direction": "up"}, ""),
    ("most", {"force": "superlative", "direction": "up"}, ""),
    ("less", {"force": "comparative", "direction": "down"}, ""),
    ("fewer", {"force": "comparative", "direction": "down"}, ""),
    ("least", {"force": "superlative", "direction": "down"}, ""),
    ("fewest", {"force": "superlative", "direction": "down"}, ""),
    ("enough", {"force": "sufficient"}, ""),
    ("such", {"force": "kind"}, "«such a cat» — a kind, not a count"),
    ("another", {"force": "existential", "distinct": True}, ""),
    ("other", {"force": "existential", "distinct": True}, ""),
    ("what", {"force": "exclamative"}, "the exclamative predeterminer («what a day»); the "
     "interrogative is its own row"),
)

#: The compound indefinites: a quantifier that already carries its own noun. They are pronouns by
#: class and quantifiers by job, which is exactly the split the table exists for.
QUANTIFIER_PRONOUNS = (
    ("everyone", {"force": "universal", "sort": "person"}, ""),
    ("everybody", {"force": "universal", "sort": "person"}, ""),
    ("everything", {"force": "universal", "sort": "thing"}, ""),
    ("someone", {"force": "existential", "sort": "person"}, ""),
    ("somebody", {"force": "existential", "sort": "person"}, ""),
    ("something", {"force": "existential", "sort": "thing"}, ""),
    ("anyone", {"force": "existential", "sort": "person"}, ""),
    ("anybody", {"force": "existential", "sort": "person"}, ""),
    ("anything", {"force": "existential", "sort": "thing"}, ""),
    ("no one", {"force": "negative", "sort": "person"}, "multi-word, and tk1 also met it spelled "
     "`no-one` and `noone`"),
    ("nobody", {"force": "negative", "sort": "person"}, ""),
    ("nothing", {"force": "negative", "sort": "thing"}, ""),
    ("none", {"force": "negative"}, ""),
)

#: Quantification over PLACES and TIMES. The place set is the pro-form of a quantifier phrase
#: («everywhere» = at every place) and belongs here for the same reason `everything` does.
QUANTIFIER_ADVERBS = (
    ("everywhere", {"force": "universal", "sort": "place"}, ""),
    ("somewhere", {"force": "existential", "sort": "place"}, ""),
    ("anywhere", {"force": "existential", "sort": "place"}, ""),
    ("nowhere", {"force": "negative", "sort": "place"}, ""),
    ("somehow", {"force": "existential", "sort": "manner"}, ""),
    ("always", {"force": "universal", "sort": "time"}, "tk1's _ADV_QUANTIFIER_UNIVERSAL"),
    ("never", {"force": "negative", "sort": "time"}, "tk1 held it in BOTH _NEGATION_MARKERS and "
     "_ADV_QUANTIFIER_NEGATIVE and had to reclassify at read time; one row, one job, and the "
     "reclassification becomes a compile rule instead"),
    ("ever", {"force": "existential", "sort": "time"}, ""),
    ("sometimes", {"force": "existential", "sort": "time"}, "tk1's _ADV_QUANTIFIER_EXISTENTIAL"),
    ("often", {"force": "many", "sort": "time"}, ""),
    ("seldom", {"force": "few", "sort": "time"}, ""),
    ("once", {"force": "existential", "sort": "time", "count": 1}, "also the subordinator «once he "
     "arrives» — two rows"),
    ("twice", {"force": "existential", "sort": "time", "count": 2}, "the last of the multiplicative "
     "adverbs English keeps as words; `three times` is productive and is a numeral"),
)

# ------------------------------------------------------------------------------------------------
# 3 — INTERROGATIVE and RELATIVE: an unbound variable, and (interrogative) a question mood
# ------------------------------------------------------------------------------------------------
#
# tk1 mapped each wh-word to the GAP ROLE it asks about (_WH_SUBJECT, _WH_PREDICATE, _WH_LOCATION,
# _WH_TIME, _WH_MANNER, _WH_CAUSE); that mapping is what `compiled` will carry, and `features.gap`
# records the same fact in the vocabulary of the table so nothing is lost while E2 decides the role
# names. The RELATIVE rows are the same forms doing a different job: no mood, and the variable is
# bound by the noun the clause modifies rather than left for an answer.

INTERROGATIVES = (
    ("who", {"gap": "subject", "sort": "person"}, ""),
    ("whom", {"gap": "object", "sort": "person"}, "prescriptively the accusative; heard as `who`"),
    ("whose", {"gap": "possessor", "sort": "person"}, ""),
    ("what", {"gap": "predicate", "sort": "thing"}, ""),
    ("which", {"gap": "subject", "sort": "selection"}, "selects from a given set"),
    ("where", {"gap": "location"}, ""),
    ("when", {"gap": "time"}, ""),
    ("why", {"gap": "cause"}, ""),
    ("how", {"gap": "manner"}, ""),
    ("whether", {"gap": "polarity"}, "the embedded yes/no question; also a subordinator"),
    ("whither", {"gap": "goal"}, "archaic"),
    ("whence", {"gap": "source"}, "archaic"),
)

RELATIVES = (
    ("who", {"sort": "person"}, ""),
    ("whom", {"sort": "person"}, ""),
    ("whose", {"sort": "possessor"}, ""),
    ("which", {"sort": "thing"}, ""),
    ("that", {}, "the relative pronoun — tk1's _RELATIVE_PRONOUNS holds exactly who/whom/which/"
     "that/whose"),
    ("where", {"sort": "place"}, ""),
    ("when", {"sort": "time"}, ""),
    ("why", {"sort": "cause"}, ""),
    ("as", {}, "the relative after `such`/`same` («such as it is»)"),
)

#: -ever: a free relative, which quantifies AND binds («whoever comes is welcome» = ∀x). Their job
#: is the relative one; the universal force rides in `features`.
FREE_RELATIVES = (
    ("whoever", {"sort": "person", "force": "universal"}, ""),
    ("whomever", {"sort": "person", "force": "universal"}, ""),
    ("whatever", {"sort": "thing", "force": "universal"}, ""),
    ("whichever", {"sort": "selection", "force": "universal"}, ""),
    ("whenever", {"sort": "time", "force": "universal"}, ""),
    ("wherever", {"sort": "place", "force": "universal"}, ""),
    ("however", {"sort": "manner", "force": "universal"},
     "also the discourse connective («however, he left»), which is a different job and a "
     "conjunctive adverb — E2/E3's, and NOT written here as a guess"),
)

# ------------------------------------------------------------------------------------------------
# 4 — PREPOSITIONS: role markers
# ------------------------------------------------------------------------------------------------
#
# The class E1 most needed written down: `in` heads the definition digraph's in-degree ranking with
# 14,408 in-edges and WordNet's `in` means *inch*; `at` is #19 and means the Lao kip. Frequency
# earned by grammar, meaning supplied by a homograph — and the second standing law says the fix is
# not a filter but a principle: a role marker never asks the dictionary a question.
#
# The list is the reference grammars' one-word inventory, walked whole. Several forms here also
# spell open-class words (`like`, `save`, `down`, `round`, `past`, `near`, `since`, `but`); a row
# says the FORM has a structural job, never that the spelling has no content reading. See the
# hazard note at the head of the model.

PREPOSITIONS = (
    "about", "above", "across", "after", "against", "along", "alongside", "amid", "amidst",
    "among", "amongst", "around", "as", "aside", "astride", "at", "atop", "bar", "barring",
    "before", "behind", "below", "beneath", "beside", "besides", "between", "beyond", "but",
    "by", "circa", "concerning", "considering", "despite", "down", "during", "except",
    "excepting", "excluding", "following", "for", "from", "given", "in", "including", "inside",
    "into", "less", "like", "minus", "near", "notwithstanding", "of", "off", "on", "onto",
    "opposite", "out", "outside", "over", "past", "pending", "per", "plus", "regarding",
    "respecting", "round", "save", "since", "than", "through", "throughout", "till", "times",
    "to", "toward", "towards", "under", "underneath", "unlike", "until", "unto", "up", "upon",
    "versus", "via", "with", "within", "without",
)

#: Postpositions — English has two and a half, and a parser that assumes head-initial marking will
#: mis-read all of them.
POSTPOSITIONS = ("ago", "apart", "aside", "notwithstanding", "through")

#: Complex prepositions: multi-word, ONE role marker. Split into words they mean nothing apart, so
#: they are single forms here and the tokeniser's problem is the tokeniser's.
COMPLEX_PREPOSITIONS = (
    "according to", "ahead of", "along with", "apart from", "as for", "as from", "as of",
    "as to", "aside from", "away from", "because of", "but for", "by means of", "close to",
    "contrary to", "depending on", "due to", "except for", "far from", "in addition to",
    "in case of", "in favour of", "in front of", "in lieu of", "in place of", "in spite of",
    "in terms of", "instead of", "irrespective of", "near to", "next to", "on account of",
    "on behalf of", "on top of", "other than", "out of", "outside of", "owing to", "prior to",
    "regardless of", "subsequent to", "thanks to", "together with", "up to", "with regard to",
    "with respect to", "within reach of",
)

# ------------------------------------------------------------------------------------------------
# 5 — CONJUNCTIONS: coordinators and subordinators
# ------------------------------------------------------------------------------------------------

COORDINATORS = (
    ("and", {"relation": "conjunction"}, ""),
    ("or", {"relation": "disjunction"}, "WordNet knows this spelling only as Oregon; the name "
     "refusal already removed it from the base, and this row is why it must never come back"),
    ("but", {"relation": "adversative"}, "also the preposition «everyone but him»"),
    ("nor", {"relation": "disjunction", "polarity": "negative"}, ""),
    ("for", {"relation": "causal"}, "the coordinator («he left, for it was late»); the preposition "
     "is its own row"),
    ("yet", {"relation": "adversative"}, "also the aspectual adverb «not yet»"),
    ("so", {"relation": "consequence"}, "also the degree adverb «so big», which is NOT this row"),
    ("plus", {"relation": "conjunction"}, "colloquial; also the preposition"),
)

SUBORDINATORS = (
    ("after", {"relation": "time"}, ""),
    ("although", {"relation": "concession"}, ""),
    ("as", {"relation": "time-or-cause"}, "genuinely ambiguous in English; the compiler resolves it"),
    ("because", {"relation": "cause"}, ""),
    ("before", {"relation": "time"}, ""),
    ("if", {"relation": "condition"}, ""),
    ("lest", {"relation": "purpose", "polarity": "negative"}, ""),
    ("once", {"relation": "time"}, ""),
    ("since", {"relation": "time-or-cause"}, ""),
    ("than", {"relation": "comparison"}, ""),
    ("that", {"relation": "complement"}, "the complementizer («he said that he left») — the third "
     "of `that`'s three jobs"),
    ("though", {"relation": "concession"}, ""),
    ("till", {"relation": "time"}, ""),
    ("unless", {"relation": "condition", "polarity": "negative"}, ""),
    ("until", {"relation": "time"}, ""),
    ("when", {"relation": "time"}, ""),
    ("whenever", {"relation": "time", "force": "universal"}, ""),
    ("where", {"relation": "place"}, ""),
    ("whereas", {"relation": "contrast"}, ""),
    ("wherever", {"relation": "place", "force": "universal"}, ""),
    ("whether", {"relation": "polarity"}, ""),
    ("while", {"relation": "time-or-contrast"}, ""),
    ("whilst", {"relation": "time-or-contrast"}, "British"),
    ("providing", {"relation": "condition"}, ""),
    ("provided", {"relation": "condition"}, ""),
    ("supposing", {"relation": "condition"}, ""),
)

COMPLEX_SUBORDINATORS = (
    ("as if", {"relation": "manner"}),
    ("as long as", {"relation": "condition"}),
    ("as soon as", {"relation": "time"}),
    ("as though", {"relation": "manner"}),
    ("even if", {"relation": "concession"}),
    ("even though", {"relation": "concession"}),
    ("in case", {"relation": "condition"}),
    ("in order that", {"relation": "purpose"}),
    ("in order to", {"relation": "purpose"}),
    ("no matter", {"relation": "concession"}),
    ("rather than", {"relation": "preference"}),
    ("so that", {"relation": "purpose"}),
    ("such that", {"relation": "manner"}),
)

# ------------------------------------------------------------------------------------------------
# 6 — AUXILIARIES and MODALS
# ------------------------------------------------------------------------------------------------
#
# Every inflected form is written out, not the lemma alone. This table is read by a PARSER, which
# meets `were` and `been` and not an abstraction of them — and it is the table E1 excludes with, so
# `are` (whose WordNet gloss is «a unit of surface area equal to 100 square meters») has to be a
# row for the exclusion to reach it. The lemma each form belongs to rides in `features.lemma`.

AUXILIARIES = (
    ("be", {"lemma": "be", "form": "base"}, "the copula compiles; `being` the NOUN is a dictionary "
     "word and a declared seed — same spelling, two readings"),
    ("am", {"lemma": "be", "form": "finite", "person": 1, "number": "sg", "tense": "present"}, ""),
    ("is", {"lemma": "be", "form": "finite", "person": 3, "number": "sg", "tense": "present"}, ""),
    ("are", {"lemma": "be", "form": "finite", "tense": "present"},
     "WordNet's `are` is a unit of 100 square metres, and it ranks #26 in the definition digraph's "
     "in-degree — frequency earned entirely by `be`'s conjugation"),
    ("was", {"lemma": "be", "form": "finite", "number": "sg", "tense": "past"}, ""),
    ("were", {"lemma": "be", "form": "finite", "number": "pl", "tense": "past"}, ""),
    ("been", {"lemma": "be", "form": "participle"}, ""),
    ("being", {"lemma": "be", "form": "gerund"},
     "THE EXCEPTION, argued: the auxiliary form compiles, and `being` the noun («the state or fact "
     "of existing») is the identity family's seed. The row does not refuse the dimension"),
    ("have", {"lemma": "have", "form": "base"}, "also a full lexical verb — a form, not a reading"),
    ("has", {"lemma": "have", "form": "finite", "person": 3, "number": "sg"}, ""),
    ("had", {"lemma": "have", "form": "finite", "tense": "past"}, ""),
    ("having", {"lemma": "have", "form": "gerund"}, ""),
    ("do", {"lemma": "do", "form": "base"}, "do-support; also a full lexical verb"),
    ("does", {"lemma": "do", "form": "finite", "person": 3, "number": "sg"}, ""),
    ("did", {"lemma": "do", "form": "finite", "tense": "past"}, ""),
    ("doing", {"lemma": "do", "form": "gerund"}, ""),
    ("done", {"lemma": "do", "form": "participle"}, ""),
)

MODALS = (
    ("can", {"modality": "possibility"}, "tk1's _MODAL_POSSIBILITY; also a container"),
    ("could", {"modality": "possibility", "tense": "past"}, ""),
    ("may", {"modality": "possibility"}, ""),
    ("might", {"modality": "possibility", "tense": "past"}, "also a noun meaning power"),
    ("must", {"modality": "necessity"},
     "tk1's _MODAL_NECESSITY — AND a declared seed of E1's volitional family. Two readings of one "
     "spelling; the Captain's to rule on, not the officer's"),
    ("shall", {"modality": "future"}, ""),
    ("should", {"modality": "obligation"}, ""),
    ("will", {"modality": "future"}, "also the noun — volition, which is a word he must be able to "
     "reason about"),
    ("would", {"modality": "future", "tense": "past"}, ""),
    ("ought", {"modality": "obligation"}, "takes `to`"),
    ("need", {"modality": "necessity"},
     "the semi-modal («he need not go») — AND a declared seed of the volitional family"),
    ("dare", {"modality": "possibility"}, "the semi-modal"),
    ("used", {"modality": "habitual", "tense": "past"},
     "«used to» — the past habitual. Its in-degree in the definition digraph is `use`'s, which is "
     "what the de-inflection guard is about"),
)

# ------------------------------------------------------------------------------------------------
# 7 — PARTICLES and CLITICS: what is left, and it is all structure
# ------------------------------------------------------------------------------------------------

PARTICLES = (
    ("not", "negation", {}, "PURE STRUCTURE, and the second standing law's own example: `not` "
     "compiles, `negation` — the concept he reasons about — keeps its dimension and is a seed"),
    ("no", "negation", {"use": "response"}, "the negative response and the negative marker; the "
     "determiner «no money» is its own row"),
    ("yes", "affirmation", {"use": "response"}, "the polarity answer, structure for the same reason "
     "`no` is"),
    ("to", "infinitive_marker", {}, "the PTB gives it a tag of its own (TO) because it is neither "
     "preposition nor verb here"),
    ("there", "existential", {}, "«there is a cat» posits an entity; the deictic `there` points at "
     "one. Two jobs, two rows"),
    ("it", "expletive", {}, "«it rains», «it is likely that…» — no referent to resolve, and a "
     "resolver that hunts for one will find the wrong entity"),
    ("let", "hortative", {}, "«let us go» — the imperative auxiliary"),
)

#: Verb particles: the forms that turn a verb into another verb («give up», «take off»). They are
#: spelled like prepositions and are not prepositions — they mark no role and take no object — and
#: E3 will need the difference the day it meets «he ran up a bill».
VERB_PARTICLES = ("up", "down", "in", "out", "on", "off", "over", "away", "back", "through",
                  "along", "around", "about", "apart", "aside", "forward", "together")

CLITICS = (
    ("n't", "negation", "the contracted negator; tk1 kept it in _NEGATION_MARKERS defensively, in "
     "case a contraction survived expansion"),
    ("'s", "genitive", "the possessive clitic — PTB's POS tag. It attaches to a PHRASE, not a word, "
     "which is why it is a clitic and not a suffix"),
    ("'re", "tense_aspect", "contracted `are`"),
    ("'ve", "tense_aspect", "contracted `have`"),
    ("'ll", "modality", "contracted `will`"),
    ("'d", "modality", "contracted `would` or `had` — genuinely ambiguous"),
    ("'m", "tense_aspect", "contracted `am`"),
)

# ------------------------------------------------------------------------------------------------
# the rows
# ------------------------------------------------------------------------------------------------


def _rows() -> list[dict]:
    """The inventory, flattened into rows — `position` counting within each class, in the order the
    groups are declared above, so the table reads back grouped as it was argued."""
    out: list[dict] = []
    counters: dict[str, int] = {}

    def add(form: str, word_class: str, role: str, features: dict, source: str, note: str) -> None:
        position = counters.get(word_class, 0)
        counters[word_class] = position + 1
        out.append(
            {
                "version": VERSION,
                "form": form,
                "word_class": word_class,
                "role": role,
                "features": dict(features),
                # E3's, and empty by construction: what a form compiles TO is a tkzip question and
                # tkzip is E2. A guess written here would be the hand list, relocated.
                "compiled": {},
                "source": source,
                "note": note,
                "position": position,
            }
        )

    for form, features, note in PERSONAL:
        add(form, "pronoun", "referential", features, TK1, note)
    for form, features, note in POSSESSIVE_DETERMINERS:
        add(form, "determiner", "possessive", features, CGEL, note)
    for form, features, note in POSSESSIVE_PRONOUNS:
        add(form, "pronoun", "possessive", features, CGEL, note)
    for form, features, note in REFLEXIVES:
        add(form, "pronoun", "reflexive", features, TK1, note)
    for form, features, note in RECIPROCALS:
        add(form, "pronoun", "reciprocal", features, CGEL, note)
    for form, features, note in DEICTIC_ADVERBS:
        add(form, "adverb", "referential", features, CGEL, note)
    for form, features, note in DEMONSTRATIVES:
        add(form, "determiner", "demonstrative", features, TK1, note)

    for form, features, note in QUANTIFIER_DETERMINERS:
        add(form, "determiner", "quantificational", features, TK1, note)
    for form, features, note in QUANTIFIER_PRONOUNS:
        add(form, "pronoun", "quantificational", features, TK1, note)
    for form, features, note in QUANTIFIER_ADVERBS:
        add(form, "adverb", "quantificational", features, TK1, note)

    for form, features, note in INTERROGATIVES:
        add(form, "pronoun", "interrogative", features, TK1, note)
    for form, features, note in RELATIVES:
        add(form, "pronoun", "relative", features, TK1, note)
    for form, features, note in FREE_RELATIVES:
        add(form, "pronoun", "free_relative", features, CGEL, note)

    for form in PREPOSITIONS:
        add(form, "preposition", "role_marker", {}, PTB, "")
    for form in POSTPOSITIONS:
        add(form, "postposition", "role_marker", {"position": "after"}, CGEL,
            "English's handful of postpositions")
    for form in COMPLEX_PREPOSITIONS:
        add(form, "preposition", "role_marker", {"complex": True}, CGEL, "multi-word: one marker")

    for form, features, note in COORDINATORS:
        add(form, "conjunction", "coordinator", features, PTB, note)
    for form, features, note in SUBORDINATORS:
        add(form, "conjunction", "subordinator", features, PTB, note)
    for form, features in COMPLEX_SUBORDINATORS:
        add(form, "conjunction", "subordinator", {**features, "complex": True}, CGEL,
            "multi-word: one subordinator")

    for form, features, note in AUXILIARIES:
        add(form, "auxiliary", "tense_aspect", features, PTB, note)
    for form, features, note in MODALS:
        add(form, "modal", "modality", features, PTB, note)

    for form, role, features, note in PARTICLES:
        add(form, "particle", role, features, PTB, note)
    for form in VERB_PARTICLES:
        add(form, "particle", "verb_particle", {}, PTB,
            "spelled like a preposition, marks no role, takes no object")
    for form, role, note in CLITICS:
        add(form, "clitic", role, {}, PTB, note)

    return out


ROWS = _rows()

#: The single-word forms, which is what E1's seed proposal excludes with. Multi-word forms are rows
#: for E3's sake and can never appear in the digraph's in-degree ranking, whose nodes are words.
FORMS = tuple(sorted({row["form"] for row in ROWS if " " not in row["form"]}))


def up(writer, db) -> None:
    ensure_collections(db, [*ALL_MODELS, *LEDGER_MODELS])
    writer.insert_many(ClosedClassDoc, ROWS)
