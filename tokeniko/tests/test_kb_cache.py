"""§4.6 — the two-tier KB cache: new knowledge must not evict the vocabulary.

Measured on 2026-08-09 against the live memory DB:

    definitions      3233 docs   1209.9 MB
    axioms+theorems  < 900 docs   ~176 MB   (1.6 MB in the gate's sandbox)

Under ONE fingerprint over all three, minting a single theorem invalidated the whole cache and
re-fetched 1.2 GB of definitions that had not moved. That is the 62% the gate's `--durations` found
in 13 theorem-materializing tests — and on the body it means he is slowest exactly when he is being
most productive.

FAST LANE by construction: no Mongo, no spaCy/Stanza. The document classes are stubbed in the
module namespace, so this asserts the CACHE POLICY itself rather than a database's behaviour.
"""
import pytest

from lib.core import evaluation_harness as eh


class _FakeQuery:
    """Mimics the Bunnet query object closely enough for the fingerprint AND the bulk fetch.

    The counter must only tick on the BULK read: `_count_and_max` also ends in `.to_list()`, and
    counting its one-document probe would make every fingerprint look like a 1.2 GB reload.
    """
    def __init__(self, docs, counter, label, probe=False):
        self._docs, self._counter, self._label, self._probe = docs, counter, label, probe

    def count(self):
        return len(self._docs)

    def sort(self, key):
        assert key == "-createdAt", key           # descending: newest first, as the real query does
        ordered = sorted(self._docs, key=lambda d: d.createdAt, reverse=True)
        return _FakeQuery(ordered, self._counter, self._label, probe=True)

    def limit(self, n):
        return _FakeQuery(self._docs[:n], self._counter, self._label, probe=True)

    def to_list(self):
        if not self._probe:
            self._counter[self._label] = self._counter.get(self._label, 0) + 1
        return list(self._docs)


class _FakeDoc:
    """A definition row whose zip is None — `_zip_leaves` is not what is under test here."""
    def __init__(self, created_at):
        self.createdAt = created_at
        self.zip = None


class _FakeModel:
    def __init__(self, docs, counter, label):
        self._docs, self._counter, self._label = docs, counter, label

    def find(self, _q):
        return _FakeQuery(self._docs, self._counter, self._label)


@pytest.fixture
def kb(monkeypatch):
    """Stub the three collections; yield a handle that can grow them and count fetches."""
    counter: dict = {}
    state = {"definitions": [_FakeDoc(10), _FakeDoc(20)],
             "axioms": [_FakeDoc(30)],
             "theorems": []}

    for label, attr in (("definitions", "TKDefinitionDoc"),
                        ("axioms", "TKAxiomDoc"),
                        ("theorems", "TKTheoremDoc")):
        monkeypatch.setattr(eh, attr, _FakeModel(state[label], counter, label))

    eh.kb_cache_clear()
    yield type("KB", (), {"state": state, "fetches": counter})()
    eh.kb_cache_clear()


def test_fingerprint_string_is_unchanged_by_the_split(kb):
    """The parts must still join into the original `nd:td:na:ta:nt:tt` — callers compare strings."""
    fp_defs, fp_rest = eh.kb_fingerprint_parts()
    assert eh.kb_fingerprint() == f"{fp_defs}:{fp_rest}"
    assert eh.kb_fingerprint() == "2:20:1:30:0:0"


def test_definitions_are_fetched_once_and_reused(kb):
    first_docs, first_leaves = eh._load_definitions(eh.kb_fingerprint_parts()[0])
    second_docs, second_leaves = eh._load_definitions(eh.kb_fingerprint_parts()[0])

    assert kb.fetches["definitions"] == 1, "the vocabulary was re-fetched under an unchanged fingerprint"
    assert second_docs is first_docs and second_leaves is first_leaves


def test_a_new_theorem_does_not_evict_the_vocabulary(kb):
    """THE REGRESSION THIS FILE EXISTS FOR: learning something must not re-read 1.2 GB."""
    fp_defs_before, fp_rest_before = eh.kb_fingerprint_parts()
    docs_before, _ = eh._load_definitions(fp_defs_before)

    kb.state["theorems"].append(_FakeDoc(40))          # he derives something

    fp_defs_after, fp_rest_after = eh.kb_fingerprint_parts()
    assert fp_rest_after != fp_rest_before, "the knowledge half must notice a new theorem"
    assert fp_defs_after == fp_defs_before, "the vocabulary half must NOT move"

    docs_after, _ = eh._load_definitions(fp_defs_after)
    assert kb.fetches["definitions"] == 1
    assert docs_after is docs_before


def test_a_new_definition_does_reload_the_vocabulary(kb):
    """The other direction — the cache must not go stale when the vocabulary really grows."""
    eh._load_definitions(eh.kb_fingerprint_parts()[0])
    kb.state["definitions"].append(_FakeDoc(50))

    docs, _ = eh._load_definitions(eh.kb_fingerprint_parts()[0])
    assert kb.fetches["definitions"] == 2
    assert len(docs) == 3


def test_archiving_a_definition_reloads_it_too(kb):
    """`archived=True` leaves the collection's newest timestamp alone — the COUNT is what moves."""
    eh._load_definitions(eh.kb_fingerprint_parts()[0])
    kb.state["definitions"].pop()                       # archived => outside {"archived": False}

    docs, _ = eh._load_definitions(eh.kb_fingerprint_parts()[0])
    assert kb.fetches["definitions"] == 2
    assert len(docs) == 1


def test_kb_cache_clear_drops_the_vocabulary_too(kb):
    eh._load_definitions(eh.kb_fingerprint_parts()[0])
    eh.kb_cache_clear()
    eh._load_definitions(eh.kb_fingerprint_parts()[0])
    assert kb.fetches["definitions"] == 2


def test_hand_resetting_only_the_kb_dict_keeps_the_vocabulary(kb):
    """The documented asymmetry: the call sites that reset `_kb_cache` by hand (untangle.py, several
    tests) rebuild the KB dict but must NOT pay for the vocabulary again."""
    eh._load_definitions(eh.kb_fingerprint_parts()[0])
    eh._kb_cache = None
    eh._kb_cache_fp = None
    eh._load_definitions(eh.kb_fingerprint_parts()[0])
    assert kb.fetches["definitions"] == 1
