"""The skeleton: tokens, universal POS, dependencies — and nothing else.

**WHAT A SKELETON IS.** The station's contract is surface → tkzip. The skeleton is the one thing it
asks a third-party model for: *which words are here, what part of speech is each, and what hangs off
what.* Senses belong to the evaluator, semantics to the anchors, figures to the derived layer — tk2
stripped the parser of everything stanza was bad at, and what remains is where it is best in class.

**ONE PROVIDER, AND IT IS STANZA, BECAUSE IT TARGETS A STANDARD** (the Captain, 2026-09-15). The
conception notes proposed a second reader as a shield — disagreement between skeletons — and called
it weak because *«spaCy and stanza are not consistently comparable»*. The reason is sharper than
«different vocabularies»: **stanza aims at UD2 and spaCy is more creative**, and two readers where
only one is trying to be correct is one reader plus noise. So there is no second parser here. **The
second reader is UD2 itself** — the published relation inventory and its examples — and checking
against it is a measurement E3 owes, relation by relation.

**THE DEPENDENCY BOUNDARY IS THIS FILE.** Everything above it sees `Skeleton` and `Word`, which are
plain dataclasses holding UD strings. Nothing else in tk2 imports spacy, stanza or torch. That is
requirement 2's «swappable without touching any format», made structural: a provider that emitted
CoNLL-U from a file, or a future model nobody has written, replaces `StanzaSkeletons` and the
station does not notice.

**FOUR THINGS INHERITED FROM tk1's parser, each paid for once already:**

1. **The `torch.load` patch.** Newer torch defaults `weights_only=True` and stanza's models do not
   load under it. Patched at import time, narrowly, and restored — a global left mutated would reach
   every other torch user in the process.
2. **`device="mps"`** — the Captain's machine is Apple silicon and this is the difference between
   seconds and tens of seconds.
3. **`download_method="reuse_resources"`** — never re-download a model that is already on disk.
4. **THE 43-MINUTE GREMLIN, and it is a correctness bug rather than a speed one:** spaCy mints a
   FRESH `Token` wrapper on every `.head` access, so `token.head is token` is never true and a walk
   to the root never terminates. **Compare INDICES.** `Skeleton` stores `head` as an index for
   exactly this reason, and the root is the word whose head is its own index.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from typing import Iterator, Sequence

#: UD's seventeen universal POS tags — the closed vocabulary the station reads. Frame: UD publishes
#: it, and a tag outside this set means the provider is not speaking UD.
UD_POS = (
    "ADJ", "ADP", "ADV", "AUX", "CCONJ", "DET", "INTJ", "NOUN", "NUM", "PART", "PRON", "PROPN",
    "PUNCT", "SCONJ", "SYM", "VERB", "X",
)

#: UD's 37 main dependency relations. Subtypes arrive as `rel:sub` and are normalised by `bare()`.
UD_DEPS = (
    "acl", "advcl", "advmod", "amod", "appos", "aux", "case", "cc", "ccomp", "clf", "compound",
    "conj", "cop", "csubj", "dep", "det", "discourse", "dislocated", "expl", "fixed", "flat",
    "goeswith", "iobj", "list", "mark", "nmod", "nsubj", "nummod", "obj", "obl", "orphan",
    "parataxis", "punct", "reparandum", "root", "vocative", "xcomp",
)

#: The relations that open an EMBEDDED clause. tk1 earned this set on live specimens (R5, the
#: wh-position bug): a wh-word makes an utterance interrogative only if it attaches to the ROOT
#: clause — «WHEN do you sleep» is a question, «I am happy WHEN I talk» is subordination.
EMBEDDING_DEPS = frozenset({"advcl", "ccomp", "xcomp", "acl", "csubj", "parataxis"})


def bare(dep: str) -> str:
    """`acl:relcl` → `acl`. UD's subtypes are language-specific refinements OF a main relation, and
    a consumer that matched on the full string would silently stop handling a relation the moment a
    model got more specific about it."""
    return dep.split(":", 1)[0] if dep else dep


@dataclass(frozen=True, slots=True)
class Word:
    """One token, as UD describes it.

    `head` is an INDEX into the skeleton's own words, never an object — see the gremlin above. The
    root is the word whose `head` is its own `index`.
    """

    index: int
    text: str
    lemma: str
    upos: str
    dep: str
    head: int
    feats: dict[str, str] = field(default_factory=dict)

    @property
    def bare_dep(self) -> str:
        return bare(self.dep)

    @property
    def is_root(self) -> bool:
        return self.head == self.index


@dataclass(frozen=True, slots=True)
class Skeleton:
    """One sentence, as UD describes it — and the ONLY thing a provider may return.

    Deliberately not a tree object: the station walks it, and a walk over indices is something any
    provider can produce and any test can write by hand. `tests` build these literally, which is
    what keeps the compiler testable without loading a 400 MB model.
    """

    text: str
    words: tuple[Word, ...]

    def __iter__(self) -> Iterator[Word]:
        return iter(self.words)

    def __len__(self) -> int:
        return len(self.words)

    def __getitem__(self, i: int) -> Word:
        return self.words[i]

    @property
    def tokens(self) -> tuple[str, ...]:
        return tuple(w.text for w in self.words)

    @property
    def tags(self) -> tuple[tuple[str, str], ...]:
        """`(upos, dep)` per token — exactly what `ClosedClasses.walk` takes."""
        return tuple((w.upos, w.dep) for w in self.words)

    @property
    def root(self) -> Word | None:
        return next((w for w in self.words if w.is_root), None)

    def children(self, index: int) -> tuple[Word, ...]:
        return tuple(w for w in self.words if w.head == index and w.index != index)

    def attaches_to_root(self, index: int) -> bool:
        """Does this word hang off the ROOT clause, or off an embedded one?

        tk1's R5 walk, brought over with its bound intact. The bound is not defensive programming:
        a malformed skeleton with a head cycle would otherwise hang the station forever, and the
        walk costs nothing.
        """
        node = self.words[index]
        for _ in range(len(self.words)):
            if node.bare_dep in EMBEDDING_DEPS:
                return False
            if node.is_root:
                return True
            node = self.words[node.head]
        return True

    def non_ud(self) -> tuple[str, ...]:
        """Tags and relations this skeleton carries that UD does not define.

        The gate's own instrument: a provider claiming to speak UD and emitting something else is
        exactly what «take stanza as close enough and CHECK» was ruled to catch.
        """
        bad = {w.upos for w in self.words if w.upos not in UD_POS}
        bad |= {w.bare_dep for w in self.words if w.bare_dep not in UD_DEPS}
        return tuple(sorted(bad))


class SkeletonProvider:
    """The seam. A provider turns text into `Skeleton`s and knows nothing about tkzip."""

    name = "abstract"

    def __call__(self, text: str) -> tuple[Skeleton, ...]:
        raise NotImplementedError


class StanzaSkeletons(SkeletonProvider):
    """stanza, through `spacy-stanza`, behind the boundary.

    Through spacy-stanza rather than stanza directly because that is what tk1 runs and what the
    Captain's models are downloaded for — but **the pipeline is stanza's**, and the spaCy layer is
    an API surface, not a second opinion. What comes out is UD: stanza's own `upos` and `dep`.

    The model is loaded ONCE per process and lazily: importing this module must stay free, or every
    test that touches `tk2.language` pays 400 MB and twenty seconds for a table lookup.
    """

    name = "stanza"

    def __init__(self, device: str = "mps") -> None:
        self.device = device
        self._pipeline = None

    def pipeline(self):
        if self._pipeline is None:
            self._pipeline = _load_pipeline(self.device)
        return self._pipeline

    def __call__(self, text: str) -> tuple[Skeleton, ...]:
        doc = self.pipeline()(text)
        return tuple(_skeleton_of(sent) for sent in doc.sents)


@lru_cache(maxsize=2)
def _load_pipeline(device: str):
    """The model, loaded once per process and per device.

    The torch patch lives HERE rather than at module import: it is needed only while stanza reads a
    checkpoint, and a process-wide `torch.load` that silently trusts every file is not something to
    leave switched on for anyone else's sake.
    """
    import spacy_stanza
    import torch

    original = torch.load

    def trusting(*args, **kwargs):
        # stanza's own checkpoints, which torch >= 2.6 refuses by default under `weights_only=True`.
        kwargs["weights_only"] = False
        return original(*args, **kwargs)

    torch.load = trusting
    try:
        return spacy_stanza.load_pipeline(
            "en",
            device=device,
            download_method="reuse_resources",  # never re-download what is already on disk
        )
    finally:
        torch.load = original


def _skeleton_of(sent) -> Skeleton:
    """A spaCy span → our own dataclasses, with heads as LOCAL indices.

    The re-basing matters: spaCy's `token.i` is an offset into the whole DOCUMENT, so a second
    sentence would carry heads pointing past its own end. Everything above this line indexes within
    one sentence, because a skeleton IS one sentence.
    """
    start = sent[0].i
    words = []
    for token in sent:
        head = token.head.i - start
        index = token.i - start
        words.append(Word(
            index=index,
            text=token.text,
            lemma=(token.lemma_ or token.text).lower(),
            upos=token.pos_ or "X",
            # spaCy stores UD's `root` as an empty dep or as `ROOT`; normalise to UD's spelling so
            # nothing above has to know which library produced the skeleton.
            dep=("root" if (token.dep_ or "").lower() in ("root", "") else token.dep_.lower()),
            head=index if head == index else head,
            feats=dict(token.morph.to_dict()) if token.has_morph() else {},
        ))
    return Skeleton(text=sent.text, words=tuple(words))


def skeleton_from_conllu(text: str, rows: Sequence[Sequence[str]]) -> Skeleton:
    """A skeleton built from CoNLL-U columns — `(id, form, lemma, upos, head, deprel)`.

    This is how UD's own examples enter the gate without a model in the loop, and how a test states
    a parse it wants to reason about. CoNLL-U is 1-indexed with 0 for the root; we are 0-indexed with
    the root pointing at itself, and the conversion is here so it is written once.
    """
    words = []
    for position, row in enumerate(rows):
        _id, form, lemma, upos, head, deprel = row
        head_index = int(head) - 1
        words.append(Word(
            index=position,
            text=form,
            lemma=(lemma or form).lower(),
            upos=upos.upper(),
            dep=(deprel or "dep").lower(),
            head=position if head_index < 0 else head_index,
        ))
    return Skeleton(text=text, words=tuple(words))
