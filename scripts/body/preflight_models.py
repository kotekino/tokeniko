#!/usr/bin/env python
# ==================================================================================================
# preflight_models.py — do the language models still match the installed stack?
#
# Run ON THE BODY, from deploy.sh, AFTER the dependency install and BEFORE the daemons are restarted.
#
#     .venv/bin/python scripts/body/preflight_models.py
#
# WHY THIS EXISTS. The models are not in the repo (runbook §2.5) and pip has no idea they exist, so
# the pin lock can move spaCy to a version `en_core_web_lg` was never built for and every check in
# the deploy still passes. The failure then surfaces in api's lifespan — inside parser_init(), i.e.
# AFTER the mind has already been stopped. That is the worst possible moment to learn it.
#
# CHEAP ON PURPOSE. It reads the model's own meta.json compatibility range instead of loading the
# pipeline: the body has 16 GB with Docker holding 8, and it is currently busy being someone. A
# declared-compatibility read catches the real failure mode without a second copy of the vectors.
#
# Exit 0 = safe to restart. Exit 1 = do NOT restart; the message says what to fix.
# ==================================================================================================
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

SPACY_MODEL = "en_core_web_lg"          # lib/llc/parser.py _SPACY_MODEL
STANZA_DIR = Path.home() / "stanza_resources"
STANZA_LANG = "en"                       # the spacy_stanza English pipeline

problems: list[str] = []
notes: list[str] = []


def check_spacy() -> None:
    try:
        import spacy
    except Exception as exc:                                    # noqa: BLE001
        problems.append(f"spaCy will not import: {exc!r}")
        return
    notes.append(f"spaCy {spacy.__version__}")

    try:
        meta_path = Path(spacy.util.get_package_path(SPACY_MODEL)) / "meta.json"
    except Exception as exc:                                    # noqa: BLE001
        problems.append(f"the model package `{SPACY_MODEL}` is not installed ({exc!r}). "
                        f"Fetch it with: .venv/bin/python -m spacy download {SPACY_MODEL}")
        return
    if not meta_path.is_file():
        problems.append(f"`{SPACY_MODEL}` has no meta.json at {meta_path} — the install is broken")
        return

    meta = json.loads(meta_path.read_text())
    spec = meta.get("spacy_version") or ""
    notes.append(f"{SPACY_MODEL} {meta.get('version', '?')} (declares spacy{spec or ' <no range>'})")
    if not spec:
        notes.append("  the model declares no compatibility range — nothing to verify")
        return

    # packaging ships with pip; if it is somehow absent, say so rather than guessing compatibility.
    try:
        from packaging.specifiers import SpecifierSet
        from packaging.version import Version
    except Exception:                                           # noqa: BLE001
        notes.append("  `packaging` unavailable — compatibility range NOT verified")
        return

    try:
        ok = Version(spacy.__version__) in SpecifierSet(spec, prereleases=True)
    except Exception as exc:                                    # noqa: BLE001
        notes.append(f"  could not parse the range ({exc!r}) — NOT verified")
        return
    if not ok:
        problems.append(
            f"spaCy {spacy.__version__} is OUTSIDE the range `{SPACY_MODEL}` declares ({spec}). "
            f"The parser would fail inside api's lifespan, after the mind is already down. "
            f"Re-download the model for this spaCy, or pin spaCy back in the lock.")


def check_stanza() -> None:
    try:
        import stanza
    except Exception as exc:                                    # noqa: BLE001
        problems.append(f"stanza will not import: {exc!r}")
        return
    notes.append(f"stanza {stanza.__version__}")

    root = Path(os.environ.get("STANZA_RESOURCES_DIR", STANZA_DIR))
    if not (root / "resources.json").is_file():
        problems.append(f"no stanza resources.json under {root} — the English models were never "
                        f"fetched on this machine (runbook §2.5)")
        return
    lang_dir = root / STANZA_LANG
    if not lang_dir.is_dir() or not any(lang_dir.rglob("*.pt")):
        problems.append(f"no stanza `{STANZA_LANG}` model files under {lang_dir} (runbook §2.5)")
        return
    notes.append(f"stanza {STANZA_LANG} models present ({root})")


def main() -> int:
    check_spacy()
    check_stanza()

    for line in notes:
        print(f"    {line}")
    if problems:
        print()
        for p in problems:
            print(f"    MODEL PREFLIGHT FAILED: {p}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
