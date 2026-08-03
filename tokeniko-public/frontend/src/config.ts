// Build-time configuration read from the environment.
//
// Vite INLINES `import.meta.env.VITE_*` at build time — it is not read at runtime, so changing the
// value means rebuilding and redeploying, never just restarting. Only the `VITE_` prefix is
// exposed to the client; a bare `DISCORD_INVITE_CODE` would silently be `undefined`.

// tokeniko's playground — the Discord invite, kept in config so the code can be ROTATED without a
// code change (2026-08-03). DELIBERATELY NO STALE FALLBACK: an invite that has been refreshed makes
// the old code dead, and a dead link is worse than an absent one — so an unset var yields an empty
// URL and the callers hide their CTA rather than inviting people through a door that no longer opens.
export const DISCORD_INVITE_CODE: string =
  (import.meta.env.VITE_DISCORD_INVITE_CODE || '').trim();

export const DISCORD_URL: string =
  DISCORD_INVITE_CODE ? `https://discord.gg/${DISCORD_INVITE_CODE}` : '';

if (!DISCORD_URL && typeof console !== 'undefined') {
  // loud in dev, harmless in prod: a missing invite is a misconfigured BUILD, not a runtime state.
  console.warn(
    '[config] VITE_DISCORD_INVITE_CODE is not set — the Discord CTAs are hidden. ' +
    'Set it in the frontend env BEFORE `npm run build` (Vite inlines it).'
  );
}
