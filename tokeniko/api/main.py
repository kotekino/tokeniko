import copy
import logging
import os
import time
from typing import Optional
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
from lib.llc.parser import parser, parser_diagram, parser_init
from lib.core.io import exchange_channel_key, find_exchange, get_exchange, get_stakeholder, get_tokeniko, init_io, upsert_individual
from lib.core.models import TKMemoryItemDoc
from lib.core.evaluation_harness import zip_senses
from lib.core.trust import resolve_canonical
from lib.llc.language import ENGLISH, consensus_language, is_english, language_read, translate_in, translator_enabled
from lib.llc.normalizer import detector_stumbles, detector_unrepairable, normalizer_enabled, normalizer_polish, translation_verdict, verifier_preserves, verifier_verdict, verifier_voice
from lib.llc.social import social_detect

logger_api = logging.getLogger("tokeniko-api")
from lib.llc.utils import utils_searchDissimilarTokens, utils_searchSimilarTokens
from lib.llc.decompiler import decompiler_decompile, decompiler_raw
from lib.core.tk import TKStatements
from lib.core.tkllc import TKLLC
from lib.core.memory import MEMChannels, MEMProvenance
from lib.llc.compiler import compiler_compile, compiler_zipGetBaseMarker
from lib.core.tkzip import TKZip
from api.services import AxiomService, DefinitionService, TheoremService, StakeholderService, MemoryService, EvaluationService
from api.schemas import (
    AxiomIn, AxiomPatch, AxiomReplace, AxiomSummary, axiom_or_http,
    DefinitionIn, DefinitionPatch, DefinitionReplace, DefinitionSummary, definition_or_http,
    TheoremIn, TheoremPatch, TheoremReplace, TheoremMaterializeIn, TheoremSummary, theorem_or_http,
    EvaluateIn,
    VoiceVerifyIn,
    StakeholderSummary, stakeholder_or_http,
    MemoryIn, MemorySummary, memory_or_http,
    create_or_http,
)

# env load (MONGO_URI, ecc.)
load_dotenv()


# THE ADDRESSED BAR (B, 2026-07-24): «you»→tokeniko binds when directedness clears this bar. The bar
# is deliberately BELOW momentum (0.85) and ABOVE ambient (0.6): an open-exchange follow-up («so,
# what are you?» mid-dialogue) binds, a cold ambient line does not. Momentum (0.85) and explicit
# addressing (0.9 / 1.0) clear it; ambient (0.6) and someone-else's-thread (0.15) do not.
def _is_addressed(directedness: float) -> bool:
    return directedness >= float(os.getenv("ADDRESSED_BAR", "0.75"))


# THE WALL'S CATCHES ARE VISIBLE LEADS (the Captain's ruling, 2026-07-24): «ears should NEVER
# hallucinate — it's the whole point». Every rag1 polish the zip-verifier TRASHES writes ONE
# microscope row (TKZipDebugDoc) into the standing triage corpus — a deterministic finding, no
# cloud judge (the rejection IS the finding, confidence 1.0). RED (high) when the polish CHANGED
# MEANING (a mood flip or a semantic drift — «what are you?» -> «I am a normalizer…»); medium for a
# structural miss (dropped leaf / balloon / still-stumbles). Best-effort: a write failure must never
# block the ears — the raw parse already stands, hearing is unaffected. Nothing in the mind reads
# these back (the collection's diagnostic charter). Accepted polishes are NOT logged.
def _log_ears_rejection(item_id: str, original: str, note: str, polished: str,
                        original_zip, polished_zip) -> None:
    try:
        from lib.core.models import TKZipDebugDoc
        from lib.llc.normalizer import verifier_semantic_similarity
        from lib.rag import RAG1_NORMALIZER
        from senses.microscope import digest_zip

        meaning_changed = (note.startswith("polish changes mood")
                           or note.startswith("polish drifts semantically"))
        sim = verifier_semantic_similarity(original_zip, polished_zip)
        sim_txt = f"{sim:.2f}" if sim is not None else "n/a (no shared semantic anchor)"
        TKZipDebugDoc(
            item_id=item_id,
            original=original,
            digest=digest_zip(original_zip),
            verdict="mismatch",
            category="ears-hallucination",
            severity="high" if meaning_changed else "medium",
            note=f"rag1 polish REJECTED — {note} | polished: «{polished}» | semantic similarity: {sim_txt}",
            model=RAG1_NORMALIZER.model,
            confidence=1.0,
        ).save()
    except Exception as error:
        logger_api.info("[rag1] ears-rejection lead write failed (%s) — hearing unaffected", repr(error))


# THE TRANSLATION'S CATCHES ARE LEADS TOO (multilingual §1 step 2): when the two independent
# readings of a foreign message do NOT hold together, the message is discarded and admitted to —
# and the failure joins the standing triage corpus so the ears' foreign-language blind spots are
# visible, not silent. Deliberately its OWN category and severity: an untranslatable message is a
# DIAGNOSTIC lead, not a hallucination (nothing was heard, so no meaning was corrupted) — MEDIUM,
# where a rag1 meaning-change is RED. The digest is of the RAW (foreign) zip: what the English-only
# compiler made of the original is exactly what an engineer needs to see. Best-effort, as above.
def _log_translation_rejection(item_id: str, original: str, lang: Optional[str], note: str,
                               readings: tuple, original_zip) -> None:
    try:
        from lib.core.models import TKZipDebugDoc
        from lib.rag import RAG4_TRANSLATE_IN
        from senses.microscope import digest_zip

        rendered = " | ".join(f"«{r.english}»" for r in readings if r is not None) or "«»"
        TKZipDebugDoc(
            item_id=item_id,
            original=original,
            digest=digest_zip(original_zip),
            verdict="mismatch",
            category="ears-translation",
            severity="medium",
            note=f"rag4 readings DISAGREE ({lang or 'unknown language'}) — {note} | readings: {rendered}",
            model=RAG4_TRANSLATE_IN.model,
            confidence=1.0,
        ).save()
    except Exception as error:
        logger_api.info("[rag4] translation lead write failed (%s) — hearing unaffected", repr(error))


# ---- THE ROOM, from the api side (multilingual §1 step 2) -------------------------------------------
# The conversational-context room (brick 1) gains a LANGUAGE, and the language is discovered where
# the message is heard — here. The api only ever READS the room on the perceiving path (never mints
# one: a room is born from a processed TURN, in the brain) and writes the language back once the
# item that decided it has an id (the REFERENCE discipline: `lang_set_by` is that item's id).
def _room_read(talker_entity, metadata, channel_enum) -> tuple:
    try:
        soul = resolve_canonical(str(talker_entity.id))
        if soul is None or soul.isMe or not soul.uid:
            return None, None, None
        key = exchange_channel_key(metadata, channel_enum)
        return find_exchange(soul.uid, key), soul.uid, key
    except Exception as error:
        logger_api.info("[rag4] room read failed (%s) — the message is heard without room context",
                        repr(error))
        return None, None, None


def _room_language_write(soul_uid: Optional[str], channel_key: Optional[str],
                         lang: Optional[str], item_id: str) -> None:
    if not soul_uid or not channel_key or not lang:
        return
    try:
        room = get_exchange(soul_uid, channel_key)   # the WRITE path may mint the room
        if room.lang == lang and room.lang_set_by:
            return                                   # unchanged — no write, no churn
        room.lang, room.lang_set_by = lang, item_id
        room.updated_at = int(time.time())
        room.save()
        logger_api.info("[rag4] room %s now speaks %s (set by %s)", channel_key, lang, item_id)
    except Exception as error:
        logger_api.info("[rag4] room language write failed (%s) — hearing unaffected", repr(error))


# THE CONSENSUS OF TWO INDEPENDENT TRANSLATIONS (the Captain's ruling). Ask twice, compile BOTH
# English candidates, and let THE COMPILER judge whether they agree — the one authority in this
# engine that is not the cloud. Returns (verdict, lang, english, note, readings); verdict is
# ACCEPT | ASK | DISCARD, or None when a reader simply did not answer (API down / kill-switch —
# graceful by contract: the raw parse then stands exactly as today, nothing is recorded).
async def _translation_consensus(tokens: str, talker_entity, addressed: bool) -> tuple:
    primary, second = await translate_in(tokens)
    if primary is None or second is None:
        return None, None, None, "a reader did not answer", (primary, second)
    lang = consensus_language(primary, second)
    zips = []
    for reading in (primary, second):
        recursive = parser(reading.english, talker_entity, app.state.tokeniko,
                           app.state.ai_client, addressed=addressed)
        zips.append(compiler_compile(copy.deepcopy(recursive))[1])
    verdict, note = translation_verdict(zips[0], zips[1])
    return verdict, lang, primary.english, note, (primary, second)


# define lifespan for startup and shutdown logic
async def lifespan(app: FastAPI):

    # IO init
    uri = os.getenv("MONGO_URI")
    db_name = os.getenv("MONGO_DB_NAME")
    db_name_memory = os.getenv("MONGO_DB_NAME_MEMORY")
    ollama_host = os.getenv("OLLAMA_HOST")

    db_client, db_memory_client, ai_client = init_io(uri, db_name, db_name_memory, ollama_host)
    tokeniko = get_tokeniko()

    # Salviamo nello stato
    app.state.db_client = db_client
    app.state.ai_client = ai_client
    app.state.db_memory_client = db_memory_client
    app.state.tokeniko = tokeniko

    # service layer (business logic + mongo ops)
    app.state.axiom_service = AxiomService(tokeniko, ai_client)
    app.state.definition_service = DefinitionService(tokeniko, ai_client)
    app.state.theorem_service = TheoremService(tokeniko, ai_client)
    app.state.stakeholder_service = StakeholderService()
    app.state.memory_service = MemoryService()
    app.state.evaluation_service = EvaluationService(tokeniko, ai_client)

    # init the pipeline (LOCAL-RETIRED 2026-07-16, the author's ruling: the Ollama preparser and
    # decompiler inits are gone — no model pulls, no loading. The machinery stays in lib/llc as
    # unreferenced code; the ears are rag1 (Claude) and the decompile surface is Claude too.)
    parser_init()

    yield  #where fastapi runs

    # shutdown logic
    db_client.close()
    db_memory_client.close()

# init fastapi app
app = FastAPI(lifespan=lifespan)

# ------------------------
# AXIOMS resource (/api/v1/axioms)
# ------------------------
# list axioms (summary view, no zip); optional filter by archived
@app.get("/api/v1/axioms")
async def list_axioms(archived: Optional[bool] = None):
    axioms = app.state.axiom_service.list(archived=archived, projection=AxiomSummary)
    return {"status": "complete", "data": axioms}

# get a single axiom (full document, including zip)
@app.get("/api/v1/axioms/{object_id}")
async def get_axiom(object_id: str):
    axiom = axiom_or_http(lambda: app.state.axiom_service.get(object_id))
    return {"status": "complete", "data": axiom}

# insert a new axiom, given a sentence
@app.post("/api/v1/axioms")
async def create_axiom(payload: AxiomIn):
    try:
        axiom = create_or_http(lambda: app.state.axiom_service.create(payload.tokens))
        return {"status": "complete", "data": axiom}
    except HTTPException:
        raise
    except Exception as error:
        return {"status": "failed", "data": repr(error)}

# partial update: only the provided fields change (recompiles if 'tokens' given)
@app.patch("/api/v1/axioms/{object_id}")
async def patch_axiom(object_id: str, payload: AxiomPatch):
    updates = payload.model_dump(exclude_unset=True)
    try:
        axiom = create_or_http(lambda: axiom_or_http(lambda: app.state.axiom_service.patch(object_id, updates)))
        return {"status": "complete", "data": axiom}
    except HTTPException:
        raise
    except Exception as error:
        return {"status": "failed", "data": repr(error)}

# replacement update: recompiles the sentence and resets flags to the body
@app.put("/api/v1/axioms/{object_id}")
async def put_axiom(object_id: str, payload: AxiomReplace):
    try:
        axiom = create_or_http(lambda: axiom_or_http(lambda: app.state.axiom_service.replace(object_id, **payload.model_dump())))
        return {"status": "complete", "data": axiom}
    except HTTPException:
        raise
    except Exception as error:
        return {"status": "failed", "data": repr(error)}

# delete an axiom
@app.delete("/api/v1/axioms/{object_id}")
async def delete_axiom(object_id: str):
    axiom_or_http(lambda: app.state.axiom_service.delete(object_id))
    return {"status": "complete", "data": {"deleted": object_id}}

# ------------------------
# DEFINITIONS resource (/api/v1/definitions) — semantic statements (single OR multi clause; TKZip)
# ------------------------
# list definitions (summary view, no zip); optional filter by archived
# WRITE-PATH INVARIANT (Brain v1.1 step 1): definitions are the DESIGN-TIME vocabulary — no runtime
# path may write them (runtime learning writes AXIOMS; theorems are derived-only via /materialize).
# TOKENIKO_DESIGN_TIME=0 locks every mutating /definitions route (403) so an embodied, live tokeniko
# physically cannot have its vocabulary edited through the API; unset/1 (the default) keeps the
# design bench open. Reads are always allowed.
def _require_design_time():
    if os.getenv("TOKENIKO_DESIGN_TIME", "1").lower() in ("0", "false", "no"):
        raise HTTPException(
            status_code=403,
            detail="definitions are design-time only (write-path invariant); "
                   "runtime learning writes axioms — set TOKENIKO_DESIGN_TIME=1 to edit the vocabulary",
        )


@app.get("/api/v1/definitions")
async def list_definitions(archived: Optional[bool] = None):
    definitions = app.state.definition_service.list(archived=archived, projection=DefinitionSummary)
    return {"status": "complete", "data": definitions}

# get a single definition (full document, including zip)
@app.get("/api/v1/definitions/{object_id}")
async def get_definition(object_id: str):
    definition = definition_or_http(lambda: app.state.definition_service.get(object_id))
    return {"status": "complete", "data": definition}

# insert a new definition, given a sentence (single OR multi clause)
@app.post("/api/v1/definitions")
async def create_definition(payload: DefinitionIn):
    _require_design_time()
    try:
        definition = create_or_http(lambda: app.state.definition_service.create(payload.tokens))
        return {"status": "complete", "data": definition}
    except HTTPException:
        raise
    except Exception as error:
        return {"status": "failed", "data": repr(error)}

# partial update: only the provided fields change (recompiles if 'tokens' given)
@app.patch("/api/v1/definitions/{object_id}")
async def patch_definition(object_id: str, payload: DefinitionPatch):
    _require_design_time()
    updates = payload.model_dump(exclude_unset=True)
    try:
        definition = create_or_http(lambda: definition_or_http(lambda: app.state.definition_service.patch(object_id, updates)))
        return {"status": "complete", "data": definition}
    except HTTPException:
        raise
    except Exception as error:
        return {"status": "failed", "data": repr(error)}

# replacement update: recompiles the sentence and resets flags to the body
@app.put("/api/v1/definitions/{object_id}")
async def put_definition(object_id: str, payload: DefinitionReplace):
    _require_design_time()
    try:
        definition = create_or_http(lambda: definition_or_http(lambda: app.state.definition_service.replace(object_id, **payload.model_dump())))
        return {"status": "complete", "data": definition}
    except HTTPException:
        raise
    except Exception as error:
        return {"status": "failed", "data": repr(error)}

# delete a definition
@app.delete("/api/v1/definitions/{object_id}")
async def delete_definition(object_id: str):
    _require_design_time()
    definition_or_http(lambda: app.state.definition_service.delete(object_id))
    return {"status": "complete", "data": {"deleted": object_id}}

# ------------------------
# THEOREMS resource (/api/v1/theorems) — derived knowledge (full TKZip). No `readonly` flag.
# ------------------------
# list theorems (summary view, no zip); optional filter by archived
@app.get("/api/v1/theorems")
async def list_theorems(archived: Optional[bool] = None):
    theorems = app.state.theorem_service.list(archived=archived, projection=TheoremSummary)
    return {"status": "complete", "data": theorems}

# get a single theorem (full document, including zip)
@app.get("/api/v1/theorems/{object_id}")
async def get_theorem(object_id: str):
    theorem = theorem_or_http(lambda: app.state.theorem_service.get(object_id))
    return {"status": "complete", "data": theorem}

# insert a new theorem, given a sentence
@app.post("/api/v1/theorems")
async def create_theorem(payload: TheoremIn):
    try:
        theorem = create_or_http(lambda: app.state.theorem_service.create(payload.tokens))
        return {"status": "complete", "data": theorem}
    except HTTPException:
        raise
    except Exception as error:
        return {"status": "failed", "data": repr(error)}

# MATERIALIZE a DERIVED conclusion as a first-class theorem (wondering-v2 / brain→API seam): ACTIVE +
# trusted, carrying its provenance (premises + chain), deduped on the SEMANTIC conclusion. The brain
# (parser-free) renders a derived conclusion to NL and POSTs it here; the service compiles it through
# the real pipeline. Returns the existing theorem (no write) when the conclusion is already held.
@app.post("/api/v1/theorems/materialize")
async def materialize_theorem(payload: TheoremMaterializeIn):
    provenance = MEMProvenance(premises=payload.premises, chain=payload.chain, derived_by=payload.derived_by)
    try:
        theorem = create_or_http(lambda: app.state.theorem_service.materialize(payload.tokens, provenance, trusted=payload.trusted, senses=payload.senses, postable=payload.postable, structure=payload.structure))
        return {"status": "complete", "data": theorem}
    except HTTPException:
        raise
    except Exception as error:
        return {"status": "failed", "data": repr(error)}

# partial update: only the provided fields change (recompiles if 'tokens' given)
@app.patch("/api/v1/theorems/{object_id}")
async def patch_theorem(object_id: str, payload: TheoremPatch):
    updates = payload.model_dump(exclude_unset=True)
    try:
        theorem = create_or_http(lambda: theorem_or_http(lambda: app.state.theorem_service.patch(object_id, updates)))
        return {"status": "complete", "data": theorem}
    except HTTPException:
        raise
    except Exception as error:
        return {"status": "failed", "data": repr(error)}

# replacement update: recompiles the sentence and resets flags to the body
@app.put("/api/v1/theorems/{object_id}")
async def put_theorem(object_id: str, payload: TheoremReplace):
    try:
        theorem = create_or_http(lambda: theorem_or_http(lambda: app.state.theorem_service.replace(object_id, **payload.model_dump())))
        return {"status": "complete", "data": theorem}
    except HTTPException:
        raise
    except Exception as error:
        return {"status": "failed", "data": repr(error)}

# delete a theorem
@app.delete("/api/v1/theorems/{object_id}")
async def delete_theorem(object_id: str):
    theorem_or_http(lambda: app.state.theorem_service.delete(object_id))
    return {"status": "complete", "data": {"deleted": object_id}}

# ---------------------------------
# STAKEHOLDERS resource (/api/v1/stakeholders) (LIST, GET) — read-only
# ---------------------------------
# list stakeholders (summary view)
@app.get("/api/v1/stakeholders")
async def list_stakeholders():
    stakeholders = app.state.stakeholder_service.list(projection=StakeholderSummary)
    return {"status": "complete", "data": stakeholders}

# get a single stakeholder (full document)
@app.get("/api/v1/stakeholders/{object_id}")
async def get_stakeholder_resource(object_id: str):
    stakeholder = stakeholder_or_http(lambda: app.state.stakeholder_service.get(object_id))
    return {"status": "complete", "data": stakeholder}

# ---------------------------------
# MEMORY resource (/api/v1/memory) (CREATE, LIST, GET, SEARCH) — timeseries log, no update
# ---------------------------------
# list recent memory items (summary view, no zip); optional limit
@app.get("/api/v1/memory")
async def list_memory(limit: int = 100):
    items = app.state.memory_service.list(projection=MemorySummary, limit=limit)
    return {"status": "complete", "data": items}

# search the memory log by timeframe / source / target / channel.
# NOTE: declared BEFORE /memory/{object_id} so "search" isn't captured as an id.
# `from`/`to` are epoch SECONDS (int); `from` is aliased since it is a Python keyword.
@app.get("/api/v1/memory/search")
async def search_memory(
    frm: Optional[int] = Query(None, alias="from"),
    to: Optional[int] = None,
    source: Optional[str] = None,
    target: Optional[str] = None,
    channel: Optional[str] = None,
    limit: int = 100,
):
    items = app.state.memory_service.search(
        frm=frm, to=to, source=source, target=target, channel=channel, limit=limit
    )
    return {"status": "complete", "data": items}

# get a single memory item (full document)
@app.get("/api/v1/memory/{object_id}")
async def get_memory(object_id: str):
    item = memory_or_http(lambda: app.state.memory_service.get(object_id))
    return {"status": "complete", "data": item}

# append a new memory item (plain log entry; no compilation)
@app.post("/api/v1/memory")
async def create_memory(payload: MemoryIn):
    try:
        item = app.state.memory_service.create(
            original=payload.original,
            sourceId=payload.sourceId,
            targetId=payload.targetId,
            channel=payload.channel,
            metadata=payload.metadata,
        )
        return {"status": "complete", "data": item}
    except Exception as error:
        return {"status": "failed", "data": repr(error)}

# ---------------------------------
# EVALUATE action (/api/v1/evaluate) — compile a sentence and evaluate its truth against tokeniko's
# knowledge (definitions + axioms + theorems). Pure: stores nothing.
# ---------------------------------
@app.post("/api/v1/evaluate")
async def evaluate(payload: EvaluateIn):
    try:
        result = app.state.evaluation_service.evaluate(payload.tokens)
        return {"status": "complete", "data": result}
    except Exception as error:
        return {"status": "failed", "data": repr(error)}

# the OUTBOUND voice gate (rag2-out, compose 2.0 slice 3): does the polished reply still compile
# to the meaning of the raw one? The API owns the pipeline (the one-compile-seam doctrine — same
# as /input), so the consensus runs here; `senses` makes the cloud call and asks. PURE — stores
# nothing; the polishability gate (a raw with unsound leaves is unverifiable) lives inside
# verifier_voice. Compiles with talker=tokeniko: the raw is HIS OWN speech.
@app.post("/api/v1/voice/verify")
async def voice_verify(payload: VoiceVerifyIn):
    try:
        me = app.state.tokeniko
        raw_zip = compiler_compile(copy.deepcopy(
            parser(payload.raw, me, me, app.state.ai_client)))[1]
        polished_zip = compiler_compile(copy.deepcopy(
            parser(payload.polished, me, me, app.state.ai_client)))[1]
        ok, note = verifier_voice(raw_zip, polished_zip)
        return {"status": "complete", "data": {"ok": ok, "note": note}}
    except Exception as error:
        return {"status": "failed", "data": repr(error)}

# ------------------------
# UTILS endpoints (debugging; may be removed later)
# ------------------------
@app.get("/api/v1/utils/dict")
async def search(token: str, opposite: int = 0):
    preparsedTokens = token
    if opposite == 0:
        doc = utils_searchSimilarTokens(preparsedTokens) 
    else:
        doc = utils_searchDissimilarTokens(preparsedTokens) 

    return doc

@app.get("/api/v1/utils/markers")
async def search(token: str):
    result = compiler_zipGetBaseMarker(token)
    return result

@app.get("/api/v1/utils/render", response_class=HTMLResponse)
async def render(tokens: str = Query(..., min_length=3, description="Sentence to submit")):
    preparsedTokens = tokens
    res = parser_diagram(preparsedTokens)
    return res

# ------------------------
# COMPILER endpoints
# ------------------------
# walk the recursive parse for entity-linked named individuals (TKName with a uid) — recurses into
# nested statements. exposes the full name payload (uid + ner + 2925 type centroid) so the storing
# path can home each individual in the stakeholders collection.
def _collect_individuals(statements) -> list:
    found = []
    for stat in statements:
        for ent in getattr(stat, "entities", []):
            payload = ent.payload
            if getattr(payload, "entity_type", None) == "statement":
                found.extend(_collect_individuals([payload]))
            elif getattr(payload, "entity_type", None) == "name" and getattr(payload, "uid", None):
                found.append(payload)
    return found

@app.get("/api/v1/input")
async def process(tokens: str = Query(..., min_length=3, description="Sentence to submit"), output: int = 0, talker: str = "unknown",
                  talker_name: Optional[str] = None, channel: str = MEMChannels.API.value,
                  metadata: Optional[str] = None, directedness: float = 1.0):
    try:
        # the perceiving channel (senses passes "discord"; a bad value falls back to API). metadata is
        # the channel's reply coordinates (a JSON string, e.g. {"channel_id","message_id"}) that ride
        # the memory item so a directed answer can thread back; directedness is the fuzzy addressing
        # carrier (see MEMItem). talker is a channel-scoped uid ("renzo@discord:12345"), talker_name
        # the human display name.
        try:
            channel_enum = MEMChannels(channel)
        except ValueError:
            channel_enum = MEMChannels.API

        # get talker entity from memory, or create it if not exists
        talkerEntity = get_stakeholder(talker, channel=channel_enum, display_name=talker_name)

        # the COREFERENCE GATE (the mammal incident, 2026-07-18; the bar softened by momentum, B
        # 2026-07-24): «you»→tokeniko only when the utterance is actually ADDRESSED to him — now the
        # ADDRESSED_BAR (default 0.75, below momentum's 0.85, above ambient's 0.6); in cold-ambient or
        # someone-else's-thread talk the addressee is unknowable and «you» stays unresolved. (Read
        # here rather than at the parse: the translation's own compiles need it too.)
        addressed = _is_addressed(directedness)

        # pipeline: recursive, flat, raw, output (if output). The old prepare= Ollama pre-pass is
        # RETIRED (2026-07-16) — rag1 below is the only pre-input tidying, and only on a stumble.
        preparsedTokens = tokens

        # --------------------------------------------------------------
        # MULTILINGUAL AT THE EARS (§1 step 2 — the room's second tenant). FIRST of everything: the
        # Captain speaks Italian, and every stage below (the social detector, the parser, rag1) is
        # English-only — so the English must exist before any of them looks at the message.
        #   1. DETECT, locally (never a cloud call: the privacy frame must be able to gate the cloud
        #      per stakeholder, and a cloud language-detect would itself be such a call). Sticky:
        #      a short or ambiguous turn INHERITS the room's language instead of being guessed at.
        #   2. If foreign: TWO INDEPENDENT READINGS, and the COMPILER judges whether they agree
        #      (asking twice restores the authority a translation otherwise escapes).
        #   3. ACCEPT -> the English becomes the pipeline's input (and rides in `normalized`);
        #      ASK -> the primary reading rides in `suggested_reading` and the brain asks «did you
        #      mean: …?» (brick 1's room, pending and answer-binding, for free);
        #      DISCARD -> nothing usable came back: the item is stored from its raw parse and the
        #      derivable not-understood state earns an honest admission (the Captain's ruling).
        # `original` ALWAYS keeps his own words, in his own language (true history be it).
        # --------------------------------------------------------------
        source_lang: Optional[str] = None
        normalized_text: Optional[str] = None
        suggested_reading: Optional[str] = None  # the "did you mean?" candidate (ASK tier) — the brain reacts
        translation_lead: Optional[tuple] = None  # (lang, note, readings) — logged post-store
        room, soul_uid, room_key = _room_read(talkerEntity, metadata, channel_enum)
        heard = language_read(tokens, getattr(room, "lang", None))
        # only a MEASURED verdict may move the room's language (an ambiguous turn leaves it alone).
        room_lang: Optional[str] = ENGLISH if (heard.measured and not heard.foreign) else None
        if heard.foreign and translator_enabled():
            verdict, lang, english, note, readings = await _translation_consensus(
                tokens, talkerEntity, addressed)
            if verdict is None:
                logger_api.info("[rag4] «%s» reads foreign (stop=%s odd=%s) but the readers are "
                                "unreachable — the raw parse stands", tokens[:60], heard.stop, heard.odd)
            elif is_english(lang):
                # the local detector over-fired: BOTH independent readers name it English. Take the
                # correction — the room is English and the original words stand (never rewritten on
                # a false alarm; rag1 below is the tidy path for English, as always).
                room_lang = ENGLISH
                logger_api.info("[rag4] «%s» read foreign locally but both readers say english — "
                                "correction taken", tokens[:60])
            else:
                # a reading with no LABEL is still a reading (the label is metadata, the English is
                # the substance): `source_lang` records the ATTEMPT — which is what the derivable
                # not-understood state reads — while only a real name is worth teaching the room,
                # since the outbound carrier has to speak it.
                source_lang = lang or "unknown"
                room_lang = lang or None
                if verdict == "ACCEPT":
                    preparsedTokens = normalized_text = english
                    logger_api.info("[rag4] %s heard: «%s» -> «%s» (%s)",
                                    source_lang, tokens[:60], english[:60], note)
                elif verdict == "ASK":
                    suggested_reading = english
                    logger_api.info("[rag4] %s readings DIVERGE coherently for «%s» -> «%s» (%s) — "
                                    "«did you mean?»", source_lang, tokens[:60], english[:60], note)
                else:
                    translation_lead = (source_lang, note, readings)
                    logger_api.info("[rag4] %s NOT understood: «%s» (%s) — the honest admission stands",
                                    source_lang, tokens[:60], note)

        # THE SOCIAL-ACT DETECTOR (survey slice 4, hunch 8): a social act is RECOGNIZED, never
        # evaluated. PURE act -> stored as memory WITHOUT a zip (a greeting is not a claim —
        # nothing to compile; thinking branches on `social` and reacts, or stays quiet for an
        # act naming another). MIXED (fork A, author's ruling: content wins) -> the social
        # prefix is stripped like a vocative and the content compiles clean; no reflex fires.
        social = social_detect(preparsedTokens, app.state.tokeniko.name)
        if social is not None and not social.remainder:
            memory_doc = TKMemoryItemDoc(
                original=tokens,             # ALWAYS the speaker's raw words (true history be it)
                zip=None,
                sourceId=str(talkerEntity.id),
                targetId=str(app.state.tokeniko.id),
                channel=channel_enum,
                metadata=metadata,
                directedness=directedness,
                social=social.kind,
                social_at=social.at,
                normalized=normalized_text,   # a «ciao» is greeted BECAUSE it was heard as «hello»
                source_lang=source_lang,
            )
            memory_doc.insert()
            _room_language_write(soul_uid, room_key, room_lang, str(memory_doc.id))
            return {"status": "complete",
                    "data": {"original": tokens, "social": social.kind, "social_at": social.at}}
        if social is not None:
            preparsedTokens = social.remainder
        recursiveResult = parser(preparsedTokens, talkerEntity, app.state.tokeniko, app.state.ai_client, addressed=addressed)
        recursiveResultCopy: TKStatements = copy.deepcopy(recursiveResult)
        flatResult: tuple[TKLLC, TKZip] = compiler_compile(recursiveResultCopy)

        # THE TRANSLATOR AT THE EARS (rag1-in + rag2-in, instrument arc #3): escalation-only — a
        # message whose parse STUMBLES (unknown/wart leaves) gets one surface-tidying pass
        # (Claude Haiku, normalization never interpretation) and the polish is accepted ONLY if
        # its recompiled zip preserves every soundly-parsed leaf (the zip-verifier: the compiler
        # disposes, whoever proposes). Unverifiable/unreachable -> the raw parse stands exactly
        # as before (unknown leaves never become beliefs; eval:unknown already asks).
        # The chains COMPOSE: an ACCEPTED translation hands English down here and may still be
        # tidied. What rag1 must never touch is a message the translation could NOT resolve (ASK /
        # DISCARD): the words below are still Italian, and an English surface-tidy of Italian is a
        # burned call at best and a fabricated re-hearing at worst.
        rag1_rejection: Optional[tuple] = None  # (note, polished, polished_zip) — logged post-store
        foreign_unresolved = source_lang is not None and normalized_text is None
        if normalizer_enabled() and not foreign_unresolved and flatResult and detector_stumbles(flatResult[1]):
            # unrepairable-by-tidying (pronoun-subject leaves = a COREFERENCE gap, not a surface
            # one): the polish would recompile to the same leaf and be rejected — skip the call.
            if detector_unrepairable(flatResult[0], flatResult[1]):
                logger_api.info("[rag1] stumble UNREPAIRABLE for «%s» (pronoun-subject leaf) — "
                                "escalation skipped", tokens[:60])
                polished = None
            else:
                # the ENGLISH is what gets tidied when a translation was accepted (rag1 has no
                # business reading Italian); otherwise the raw words, exactly as before.
                polished = await normalizer_polish(normalized_text or tokens)
            if polished:
                rec2 = parser(polished, talkerEntity, app.state.tokeniko, app.state.ai_client, addressed=addressed)
                flat2: tuple[TKLLC, TKZip] = compiler_compile(copy.deepcopy(rec2))
                # the two-tier floor at the ears (1a): ACCEPT | ASK | DISCARD (verifier_verdict).
                verdict, note = verifier_verdict(flatResult[1], flat2[1]) if flat2 else ("DISCARD", "no compile")
                if verdict == "ACCEPT":
                    recursiveResult, flatResult, normalized_text = rec2, flat2, polished
                    logger_api.info("[rag1] normalized «%s» -> «%s» (verified)", tokens[:60], polished[:60])
                elif verdict == "ASK":
                    # a COHERENT offerable reading — the raw parse still stands (asking ≠ believing);
                    # the candidate rides on the item and the BRAIN reacts (open a pending + ask).
                    # NOT a caught drift, so it writes NO ears-hallucination lead.
                    suggested_reading = polished
                    logger_api.info("[rag1] polish OFFERED for «%s» -> «%s» (%s) — «did you mean?»",
                                    tokens[:60], polished[:60], note)
                else:
                    logger_api.info("[rag1] polish REJECTED for «%s» (%s) — raw parse stands", tokens[:60], note)
                    rag1_rejection = (note, polished, flat2[1] if flat2 else None)

        rawResult = decompiler_raw(flatResult[0]) if flatResult[0] else ''
        outputResult = await decompiler_decompile(rawResult) if output == 1 else ''

        res = {
            "original": tokens,
            "raw output": rawResult,
            "polished output": outputResult,
            "llc flat": flatResult[0],
            "llc recursive": recursiveResult,
        }
        status = "complete"

        # store in memory
        if flatResult:
            memory_doc: TKMemoryItemDoc = TKMemoryItemDoc(
                original=tokens,            # ALWAYS the speaker's raw words (true history be it)
                zip=flatResult[1],          # compiled from the normalized text when rag1 verified
                senses=zip_senses(flatResult[1]),
                raw=rawResult,
                sourceId=str(talkerEntity.id),
                targetId=str(app.state.tokeniko.id),
                channel=channel_enum,
                metadata=metadata,
                directedness=directedness,
                normalized=normalized_text,
                suggested_reading=suggested_reading,  # the ASK candidate (1a) — the brain asks «did you mean?»
                source_lang=source_lang,              # the language heard (§1 step 2) — None when English
            )
            memory_doc.insert()

            # the room's LANGUAGE, referenced to the item that decided it (§1 step 2)
            _room_language_write(soul_uid, room_key, room_lang, str(memory_doc.id))

            # the ears' wall left a catch: log it as a microscope lead now that item_id is real
            if rag1_rejection is not None:
                r_note, r_polished, r_polzip = rag1_rejection
                _log_ears_rejection(str(memory_doc.id), tokens, r_note, r_polished,
                                    flatResult[1], r_polzip)

            # …and so did the translation consensus, when the two readings did not hold together
            if translation_lead is not None:
                t_lang, t_note, t_readings = translation_lead
                _log_translation_rejection(str(memory_doc.id), tokens, t_lang, t_note,
                                           t_readings, flatResult[1])

            # home any entity-linked named individuals in the stakeholders collection (storing path
            # only — NOT /evaluate). contextKey = the scope after "@" in the parser-minted uid.
            for individual in _collect_individuals(recursiveResult):
                context_key = individual.uid.split("@", 1)[1] if "@" in individual.uid else None
                upsert_individual(
                    name=individual.name,
                    uid=individual.uid,
                    ner_type=individual.ner,
                    vector=individual.vector,
                    context_key=context_key,
                    channel=talkerEntity.channel,
                )

    except Exception as error:
        res = repr(error)
        status = "failed"
    return {"status": status, "data": res}

@app.get("/api/v1/output")
async def out(tokens: str):
    res = await decompiler_decompile(tokens)
    return res
