"""tk2.datatier — how the rows MOVE.

Thin by charter (datatier req. 6): readers, writers, caches, guards. No business logic below the
model layer. What lands here [T3]:

  - the Mongo client + THE GUARD as standard equipment — every entry point names its db and refuses
    anything not explicitly whitelisted, tk1's above all (datatier req. 4).
  - bunnet init with the tk1 traps wrapped away (datatier req. 2): a fetch that always `.run()`s,
    and timeseries deletion through raw pymongo, exposed as one honest function.
  - the r-cache: `param` and `logic` collections read into an in-memory snapshot at boot and
    reconciled on a slow tick, so a db edit lands live without a restart (datatier req. 3).
"""
