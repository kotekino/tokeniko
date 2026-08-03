# --------------------------------------------------------------
# lib/rag/client.py — the ONE Claude client + call helper (the 2026-07-16 consolidation).
#
# Every actual Anthropic API call in the engine goes through rag_call: one lazily-constructed
# AsyncAnthropic (the SDK import stays lazy so every module remains importable without it), the
# spec's per-call timeout, text-block extraction, optional structured-output schema, and the
# GRACEFUL-BY-CONTRACT failure mode the instruments were all built on — log and return None,
# never raise (the cloud may never block the mind, the voice, or the diagnostics).
#
# Instruments keep their logic (stumble detectors, zip-verifiers, response validation, honest
# fallbacks); this module owns only the wire. The per-instrument specs live in registry.py.
#
# THE CONSENT GATE (privacy §1 step 3, 2026-07-29) also lives here, and it lives here for one
# reason: this is the ONE function through which every Claude call in the engine passes, so the
# enforcement is leak-proof BY CONSTRUCTION rather than by discipline — per-path checks are correct
# until the day someone adds path number six. The question the gate asks is not «which instrument is
# this?» but «WHOSE WORDS am I about to send?», which is why `subject_uid` is required with no
# default: a future instrument cannot be added without its author consciously deciding whose words
# it carries. Direction of travel is NOT the honest unit — the «did you mean…?» ask is tokeniko's
# own outbound speech and yet its payload literally carries the speaker's sentence back out.
# --------------------------------------------------------------
import json
import logging
import os
from typing import Callable, Optional, Union

from lib.rag.registry import RagSpec

logger = logging.getLogger(__name__)

_client = None

# ---- the consent reader (INJECTED — lib/rag stays DB-agnostic) ---------------------------------
# The evaluator's idiom (`relations=`/`part_of=`/`antonyms=` readers): the process wires the real,
# Mongo-bound reader at init (lib.core.consent.install_consent_reader); this module only asks.
# THE DEFAULT DENIES EVERYTHING — an unwired process is a SILENT process, never a leaking one.
ConsentReader = Callable[[str], Optional[bool]]


def _deny_all(subject_uid: str) -> Optional[bool]:
    return False


_consent_reader: ConsentReader = _deny_all


def set_consent_reader(reader: Optional[ConsentReader]) -> None:
    """Wire the process's consent reader (None restores the deny-all default)."""
    global _consent_reader
    _consent_reader = reader if reader is not None else _deny_all


def consent_allows(subject_uid: str) -> bool:
    """Does this person allow their words to reach the cloud? Only an explicit True proceeds —
    unasked (None), refused (False), an unknown uid and a reader that BLEW UP all deny."""
    try:
        return _consent_reader(subject_uid) is True
    except Exception as error:  # fail CLOSED: a broken reader must never open the door
        logger.warning("[rag] consent reader failed for %s (%s: %s) — denying",
                       subject_uid, type(error).__name__, error)
        return False


def get_client():
    """The process-wide AsyncAnthropic, constructed on first use (ANTHROPIC_API_KEY from env —
    never hardcoded). The default timeout is per-call overridden by each spec (with_options)."""
    global _client
    if _client is None:
        import anthropic  # lazy: the caller stays importable without the SDK
        _client = anthropic.AsyncAnthropic(timeout=60.0)
    return _client


def rag_enabled(disable_env: Optional[str] = None) -> bool:
    """Is the cloud armed? — the key is present AND the instrument's kill-switch (if it has one,
    e.g. RAG1_DISABLED — the privacy switch) is off."""
    if disable_env and os.getenv(disable_env, "").strip() in ("1", "true", "yes"):
        return False
    return bool(os.getenv("ANTHROPIC_API_KEY"))


def json_envelope(text: Optional[str]) -> Optional[dict]:
    """Extract the {...} JSON object riding inside a free-text response (the prompt-instructed
    envelope, for instruments that predate structured outputs). None if absent/malformed."""
    if not text:
        return None
    try:
        data = json.loads(text[text.index("{"): text.rindex("}") + 1])
        return data if isinstance(data, dict) else None
    except (ValueError, TypeError):
        return None


async def rag_call(spec: RagSpec, user: str, *,
                   subject_uid: Optional[str], client=None) -> Optional[Union[str, dict]]:
    """ONE Claude call per the instrument's spec. Returns the response text (free-text specs) or
    the parsed dict (schema specs); None on ANY failure — API down / auth / timeout / malformed
    JSON — logged as [rag:<name>], never raised.

    `subject_uid` is REQUIRED and has NO DEFAULT — whose words does this payload carry?
      - None      -> the payload is tokeniko's OWN content: proceed, ungated.
      - "<uid>"   -> a person's words: proceed only on an explicit consent True, else None.
    A denial is a graceful None, exactly like an API failure — every call site already has an
    honest fallback for it.

    `client` overrides the process client (tests inject fakes; the injected client's own timeout
    stands — the spec timeout is applied only on the real client)."""
    if subject_uid is not None and not consent_allows(subject_uid):
        # INFO, not WARNING: a refusal being honored is the system working, not a fault — visible
        # without being alarming.
        logger.info("[rag:%s] denied — no consent for %s", spec.name, subject_uid)
        return None
    try:
        cl = client if client is not None else get_client().with_options(timeout=spec.timeout)
        kwargs = dict(
            model=spec.model,
            max_tokens=spec.max_tokens,
            system=spec.system,
            messages=[{"role": "user", "content": user}],
        )
        if spec.temperature is not None:
            kwargs["temperature"] = spec.temperature
        if spec.schema is not None:
            kwargs["output_config"] = {"format": {"type": "json_schema", "schema": spec.schema}}
        resp = await cl.messages.create(**kwargs)
        text = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text").strip()
        if spec.schema is not None:
            return json.loads(text)
        return text or None
    except Exception as error:  # graceful by contract — the caller falls through, never crashes
        logger.warning("[rag:%s] call failed (%s: %s)", spec.name, type(error).__name__, error)
        return None
