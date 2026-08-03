/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string
  readonly VITE_SITE_NAME: string
  readonly VITE_COMING_SOON: string
  readonly VITE_DISCORD_INVITE_CODE: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
