# datatier — REQUIREMENTS

*How the rows MOVE. Distillation session 2026-08-23 (author's ruling: keep bunnet/pydantic and the
tk1 stack). One line each.*

1. **Bunnet + pydantic over local MongoDB, inherited** — the tk1 stack is the stack; no ORM adventure.
2. **The tk1 traps become law** — `.get()`/`.find_one()` return queries: `.run()`/`.to_list()` or it silently no-ops; timeseries deletes go through raw pymongo; the tier wraps these so callers cannot fall in.
3. **r-class collections load at boot and refresh on a slow tick** — a db edit becomes visible without restart (growth through someone else, live).
4. **One guard pattern for every non-body tool** — instruments and sandboxes name their db and refuse the body's (the tk2 guard, made standard).
5. **The public window is one-way** — publish-only to the separate public Atlas; the body's db is never bound to or exposed by any public surface.
6. **The tier is thin** — readers, writers, caches, guards; no business logic below the model layer.
