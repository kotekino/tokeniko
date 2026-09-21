"""Rebuild the data behind `tools/journey_ledger.html` — the Captain's v1 journeys, grouped.

READ-ONLY over tk1's `tokeniko_mem.tkzipdebug`, which is his biography and is never written here.
The grouping is done with our OWN `language_closed_classes` rows, so the page and the station agree
about what a subordinator is — and so a gap in that table shows up as a bad grouping rather than
hiding.

These journeys are **E9's no-regression ratchet material** (the Captain, 2026-09-15), not E3's gate.
Run from `tokeniko-tk2/`:  PYTHONPATH=. ../.venv/bin/python tools/journey_ledger_build.py
"""
import sys, re, json, pathlib
sys.path.insert(0,'.')
from collections import defaultdict
from pymongo import MongoClient
from tk2.core import config as settings
tk1 = MongoClient("mongodb://tokeniko.local:27018/?directConnection=true", serverSelectionTimeoutMS=8000)
body = MongoClient(settings.MONGO_URI, serverSelectionTimeoutMS=8000)['tokeniko_tk2']
byrole = defaultdict(set)
for r in body["language_closed_classes"].find({}, {"_id":0,"form":1,"role":1}):
    byrole[r["role"]].add(r["form"])
ARTICLES = {"a","an","the"}
SUB, COORD = byrole["subordinator"], byrole["coordinator"]
# `db/0028` split the fused quantifiers («nobody» · «everywhere») out of the determiner role;
# this bucket means «a quantifying word», which is both of them.
QUANT = (byrole["quantificational"] | byrole["fused_quantifier"]) - ARTICLES
MODAL, NEG, AUX = byrole["modality"], byrole["negation"], byrole["tense_aspect"]
WH = byrole["interrogative"] | byrole["free_relative"]
MARK = byrole["role_marker"] - {"as"}
norm = lambda s: re.sub(r"\s+"," ",(s or "").strip().lower()).rstrip(".!?").strip()
rows = list(tk1["tokeniko_mem"]["tkzipdebug"].find({}, {"_id":0}))
distinct = {}
for r in rows:
    k = norm(r.get("original"))
    if k and k not in distinct: distinct[k] = r
from tests.fixtures import drill
spent = set()
for name in dir(drill):
    v = getattr(drill, name)
    if isinstance(v,(list,tuple)):
        for it in v:
            s = getattr(it,"sentence",None) or (it.get("sentence") if isinstance(it,dict) else None)
            if isinstance(s,str): spent.add(norm(s))
def classify(s):
    w = s.split(); first = w[0] if w else ""; tags = []
    if set(w) & WH and (first in WH or "?" in s): tags.append("wh-question")
    elif first in AUX | MODAL | {"do","does","did","is","are","am","was","were","can","will","would","have","has"}:
        tags.append("polar question")
    if set(w) & SUB: tags.append("subordinate")
    if set(w) & COORD: tags.append("coordination")
    if set(w) & QUANT: tags.append("quantified")
    elif set(w) & ARTICLES: tags.append("article only")
    if set(w) & MODAL: tags.append("modal")
    if set(w) & NEG or "n't" in s: tags.append("negation")
    if {"than"} & set(w) or re.search(r"\bas .+ as\b", s): tags.append("comparison")
    if set(w) & MARK: tags.append("role marker")
    if len(w) <= 3 and not (set(w) & AUX): tags.append("fragment")
    if not tags: tags.append("plain statement")
    return tags
items, gcount = [], defaultdict(lambda: [0,0])
for s, r in distinct.items():
    tags = classify(s)
    v = r.get("verdict") or "ok"
    it = {"s": r.get("original","").strip(), "k": s, "v": v, "sev": r.get("severity"),
          "g": tags, "spent": s in spent}
    if v == "mismatch": it["note"] = (r.get("note") or "")[:280]
    items.append(it)
    if not it["spent"]:
        for t in tags:
            gcount[t][0] += 1
            if v == "mismatch": gcount[t][1] += 1
groups = sorted(gcount.items(), key=lambda kv: -kv[1][0])
data = {"items": items,
        "groups": [{"name": g, "n": c[0], "bad": c[1]} for g, c in groups],
        "totals": {"journeys": len(rows), "distinct": len(distinct),
                   "spent": sum(1 for i in items if i["spent"]),
                   "clean": sum(1 for i in items if not i["spent"]),
                   "mismatch": sum(1 for i in items if not i["spent"] and i["v"]=="mismatch")}}
# Spliced straight into the page between its markers: ONE self-contained file the Captain can
# double-click, with no sibling asset a browser might refuse to load over file://.
page = pathlib.Path("tools/journey_ledger.html")
html = page.read_text()
payload = "window.JOURNEYS=" + json.dumps(data, ensure_ascii=False) + ";"
html, n = re.subn(r"/\*DATA-START\*/.*?/\*DATA-END\*/",
                  lambda _: "/*DATA-START*/" + payload.replace("\\", "\\\\") + "/*DATA-END*/",
                  html, count=1, flags=re.S)
if n != 1:
    raise SystemExit("journey_ledger.html has lost its /*DATA-START*/ … /*DATA-END*/ markers")
page.write_text(html)
out = str(page)
print("wrote", out, f"{len(json.dumps(data))/1024:.0f} KB")
print(data["totals"])
