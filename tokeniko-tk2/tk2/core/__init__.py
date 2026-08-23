"""tk2.core — the shape of things.

Pydantic models are the single source of shape (data-modeling req. 6); a dimension change is a
migration, never a cast. What lands here, in order:

  - `constants.py`  — the names the body cannot look up, because it needs them to look anything up.
  - the base document conventions: every model declares its WRITE-CLASS — kb (rw) · param (r) ·
    logic (r) — plus the provenance and epoch-stamp mixins every later model reuses  [T2].
  - the collection models themselves (heart, forecasts, derived points, micro-nn, registers)  [T4].

Nothing in here talks to Mongo. The tier that moves the rows is `tk2.datatier`.
"""
