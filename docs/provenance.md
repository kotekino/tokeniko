# The source corpora — what `data/` holds, and what was removed

`data/` is **gitignored**: git cannot restore anything here, which is why this file exists. It is the
ledger for the raw material the body was built from — the files that came from outside the project
and are not reproducible by running our own code.

*Pruned 2026-09-17 from 3.3 GB to 6.8 MB, on the Captain's ruling «inventory then prune».* Nothing was
deleted that is not either re-downloadable from a stable public source or derivable by a script in
this repo. Both are named below.

---

## KEPT — not re-downloadable, or cheap enough that losing it would be silly

| file | what it is | why it stays |
|---|---|---|
| `The_Oxford_3000.pdf` · `The_Oxford_5000.pdf` | Oxford's published word lists | **The provenance of the dictionary's 2925-base**, which is Oxford 3000 + Moby. The base is a measured artifact; this is the evidence of where half of it came from |
| `dictionary.txt` (3.9 MB) | the Moby-derived word list | the other half of the same answer. Read by `tokeniko-tk1/tools/dictionary.py` |
| `names.csv` · `names.txt` | 21,975 personal names, one per line | the source of tk1's name table — **E3b's inheritance**, and the thing the name question was measured against (28.1% collide with place names) |
| `tokeniko.markers.json` · `tokeniko.fullmarkers.json` · `tokeniko.markers.base.json` | mongo exports of tk1's marker collections, vectors included | **curated knowledge with no upstream.** These are ours; there is nowhere to fetch them from |
| `semantic_engine.polygon_registry.json` | a mongo export of the polygon registry | same: no upstream |
| `admin1CodesASCII.txt` · `countryInfo.txt` | geonames reference tables, 180 KB together | re-downloadable, but small enough that keeping the ingest runnable is worth more than the bytes |

## REMOVED — and exactly how to get each one back

| file | size | how to restore |
|---|---|---|
| `allCountries.txt` | 1.7 GB | `https://download.geonames.org/export/dump/allCountries.zip` — the full geonames gazetteer |
| `cities500.txt` · `cities500.zip` | 49 MB | `https://download.geonames.org/export/dump/cities500.zip` |
| `cities15000.zip` | 2.9 MB | `https://download.geonames.org/export/dump/cities15000.zip` |
| `natural_earth/` | 10 MB | `https://www.naturalearthdata.com/downloads/` — the public shapefile sets |
| `places.json` | 1.5 GB | **derived, not downloaded.** Built from the geonames dumps above by `tokeniko-tk1/tools/geo*.py`, and its content is **live in the body** as `tokeniko.places` — 4,674,701 rows, 21 distinct `type` values, measured 2026-09-16 for E3b |

**The ingest path is code and is kept**: `tokeniko-tk1/tools/geo2.py`, `geo3alt.py`, `geo5.py`,
`geoTest.py` read the geonames files; `tokeniko-tk1/tools/dictionary.py` reads `dictionary.txt`. So
the restoration is download-then-run, not archaeology.

---

## Why this file rather than a clean delete

The project buys honesty with **ledgers**, not with un-editable media — there is no team here to
review a deletion. A gitignored folder that quietly loses 3.3 GB leaves no trace at all; a folder
that loses it with this table beside it loses nothing that matters. The same reasoning that keeps a
retired dictionary-bar pair as `retired_at` rather than a missing row.
