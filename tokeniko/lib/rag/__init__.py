# lib/rag — the Claude API machinery, concentrated (the author's 2026-07-16 consolidation ruling):
# one lazy client + one call helper (client.py) over the per-instrument model/prompt/schema
# registry (registry.py). Call sites: lib/llc/normalizer.py (rag1), lib/llc/decompiler.py (rag2
# decompile), senses/microscope.py (rag3 judge), senses/blog.py (polish), lib/llc/language.py +
# senses/outbound.py (rag4 multilingual, 2026-07-26 — the two independent inbound readers + the
# outbound translator).
from lib.rag.client import get_client, json_envelope, rag_call, rag_enabled
from lib.rag.registry import (
    BLOG_POLISH,
    RAG1_NORMALIZER,
    RAG2_DECOMPILE,
    RAG2_OUT,
    RAG3_JUDGE,
    RAG4_RENDER_IN,
    RAG4_TRANSLATE_IN,
    RAG4_TRANSLATE_OUT,
    RagSpec,
)

__all__ = [
    "get_client", "json_envelope", "rag_call", "rag_enabled",
    "RagSpec", "RAG1_NORMALIZER", "RAG2_DECOMPILE", "RAG2_OUT", "RAG3_JUDGE", "BLOG_POLISH",
    "RAG4_TRANSLATE_IN", "RAG4_RENDER_IN", "RAG4_TRANSLATE_OUT",
]
