# --------------------------------------------------------------
# brain/api_client.py — the brain's FIRST OUTBOUND SEAM (#4 D3a). The brain process is PARSER-FREE
# (it never loads spaCy/Stanza/the compiler); when it needs the full pipeline — to compile a derived
# conclusion into a first-class zip theorem — it reaches the `api` process over HTTP rather than
# importing the parser. This module is that thin client.
#
# Stdlib-only (urllib) on purpose: a tiny, dependency-free, SYNCHRONOUS POST that fits the coordinator
# loop's one-bounded-unit-per-tick rhythm. GRACEFUL BY CONTRACT — if the API is down or errors, it
# LOGS and returns None; the brain never crashes on an unreachable seam (it simply retries next tick).
#
# D3a uses it for ONE call (materialize_theorem); D3b extends it (the senses target: speakup/answer/…).
# --------------------------------------------------------------
import json
import logging
import os
import urllib.error
import urllib.parse
import urllib.request

logger = logging.getLogger("tokeniko-brain")

# base URL of the local `api` process (one body, one machine — see CLAUDE.md embodiment note).
_API_BASE = os.getenv("BRAIN_API_BASE", "http://localhost:8000")
_TIMEOUT = float(os.getenv("BRAIN_API_TIMEOUT", "30"))  # materialize compiles (~seconds); be patient


# POST a JSON body to `path` on the local API. Returns the parsed response dict, or None on ANY
# failure (connection refused, timeout, non-2xx, malformed JSON) — logged, never raised.
def _post_json(path: str, body: dict) -> dict | None:
    url = _API_BASE.rstrip("/") + path
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, method="POST", headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body_text = e.read().decode("utf-8", "replace") if e.fp else ""
        logger.warning("[api_client] POST %s -> HTTP %s: %s", path, e.code, body_text[:200])
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        logger.warning("[api_client] POST %s unreachable (%s) — will retry next tick", path, e)
    except (ValueError, json.JSONDecodeError) as e:
        logger.warning("[api_client] POST %s — malformed response (%s)", path, e)
    return None


# GET a JSON body from `path` on the local API with query `params`. Same graceful contract as
# _post_json (returns None on ANY failure, logged never raised). `/api/v1/input` is a GET.
def _get_json(path: str, params: dict) -> dict | None:
    url = _API_BASE.rstrip("/") + path + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body_text = e.read().decode("utf-8", "replace") if e.fp else ""
        logger.warning("[api_client] GET %s -> HTTP %s: %s", path, e.code, body_text[:200])
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        logger.warning("[api_client] GET %s unreachable (%s) — will retry next tick", path, e)
    except (ValueError, json.JSONDecodeError) as e:
        logger.warning("[api_client] GET %s — malformed response (%s)", path, e)
    return None


# RE-INGEST a text through the NORMAL ingestion path (`/api/v1/input`) as if the speaker had said it
# cleanly — the "did you mean?" confirmation seam (1b). The brain is parser-free; a CONFIRMED reading
# must be COMPILED (its meaning differs from the stumbling item's stored zip) and then flow through
# the very same pipeline any clean human turn does (teaching / hypothesis / corroboration / cross-
# item), gated by the SPEAKER's own trust — so it re-enters as a fresh input attributed to that
# speaker, not minted directly as a theorem. `talker` is the channel-scoped uid (get_stakeholder
# fetch-or-creates it), `directedness`/`metadata` inherited from the original turn. Graceful: API
# down -> None (the answer was still understood; the reading is simply not re-ingested this time).
def ingest_input(tokens: str, talker: str, channel: str, directedness: float,
                 talker_name: str | None = None, metadata: str | None = None) -> dict | None:
    params: dict = {"tokens": tokens, "talker": talker, "channel": channel,
                    "directedness": directedness}
    if talker_name:
        params["talker_name"] = talker_name
    if metadata:
        params["metadata"] = metadata
    return _get_json("/api/v1/input", params)


# MATERIALIZE a derived conclusion as a first-class theorem via the API pipeline. `tokens` is the
# rendered first-person NL ("I exist"); premises/chain/derived_by are its provenance (the proof). The
# API compiles it (talker=tokeniko ⇒ "I" → its own uid), semantic-dedups, and stores it ACTIVE +
# trusted. Returns the {status, data} dict (data = the theorem, existing or new), or None on failure.
def materialize_theorem(tokens: str, premises: list[str], chain: str, derived_by: str = "wondering",
                        trusted: float = 0.9, senses: dict | None = None,
                        postable: bool = True, structure: dict | None = None) -> dict | None:
    # `postable` (blog P1): the provenance gate computed brain-side (the premise-AND over the
    # conclusion's premise theorems — "DM never public"); persisted on the stored theorem doc.
    # `structure` (instrument arc #2): the conclusion's {subject, predicate, object?, negated?,
    # subject_kind?} — the ZIP-NATIVE entrance: the API assembles the zip directly from it, the
    # parser never runs, and `tokens` is only the human-readable label.
    body = {"tokens": tokens, "premises": premises, "chain": chain, "derived_by": derived_by,
            "trusted": trusted, "postable": postable}
    if structure:
        body["structure"] = structure
    if senses:
        body["senses"] = senses  # parser-fallback path only: pinned server-side into the compiled zip
    return _post_json("/api/v1/theorems/materialize", body)


# CREATE an axiom via the API pipeline — the brain's ONE runtime KB-write seam besides materialize
# (the WRITE-PATH INVARIANT, Brain v1.1 step 1): runtime learning writes AXIOMS, never definitions
# (design-time vocabulary) and never theorems directly (derived-only, via materialize). Any future
# learn-loop (eval:true novel truth taught by a trusted stakeholder, D-phase) MUST come through here.
# The API compiles, runs the contradiction guard (logic-is-sacred), and stores. Returns the
# {status, data} dict, or None on failure.
def create_axiom(tokens: str) -> dict | None:
    return _post_json("/api/v1/axioms", {"tokens": tokens})
