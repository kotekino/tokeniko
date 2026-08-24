# senses: this is the I/O of tokeniko
# - discord connector, to process messages and send messages
# - atproto connector, to process trusted sources and be aware of the events happening in the world

import asyncio
import logging
import os
import signal
import sys
from dotenv import load_dotenv
from lib.core.consent import install_consent_reader
from lib.core.io import init_io
from senses.inbound import handle_discord_message
from senses.outbound import outbound_executor_task
from senses.blog_outbound import blog_outbound_task
from senses.microscope import microscope_task

load_dotenv()

# logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("tokeniko-brain")

# atproto listenere
async def atproto_listener_task():

    logger.info("🦋 ATProto Listener (Jetstream) started")
    try:
        while True:

            await asyncio.sleep(5)  # Simulazione attesa dati
    except asyncio.CancelledError:
        logger.info("🦋 LATProto Listener interrupted...")

# discord bot — the live inbound listener (P1: DMs → /input → memory; channels dropped until step 2).
# The adapter owns the gateway; senses owns the translation (senses/inbound.py). The client is built
# in main() and SHARED with the outbound executor (one gateway connection carries both directions).
async def discord_bot_task(client):
    client.on_message(handle_discord_message)
    logger.info("💬 Discord interface started (inbound: DMs → memory)")
    try:
        await client.start()
    except asyncio.CancelledError:
        logger.info("💬 Discord interface interrupted...")
        raise
    finally:
        await client.close()


# build the outbound Sender closure over the shared client (P3): the executor hands it a resolved
# Destination + prepared content; the adapter ships it. None when Discord is not connected.
def make_discord_sender(client):
    async def sender(destination, content: str) -> str:
        return await client.send(destination, content)
    return sender

# main / init
async def main():
    logger.info("🚀 Init tokeniko: senses")
    
    # 1. Init — senses needs Mongo (the action queue) + Ollama (the decompiler, raw -> fluent English).
    #    No spaCy/Stanza pipeline: the brain compiled the input; senses only DECOMPILES the reply.
    db, db_memory, ai_client = init_io()

    # THE CONSENT GATE (privacy §1 step 3): the outbound voice, the localizer and the microscope all
    # send someone's words, so senses arms the gate exactly like the api does. Before this call the
    # default reader denies everything — deliberately: an unwired process must be silent, not leaky.
    install_consent_reader()

    # 2. Graceful Shutdown
    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()
    
    def shutdown_handler():
        logger.warning("⚠️ SIGTERM. Time to go to deep sleep...")
        stop_event.set()

    # Listen for termination signals
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, shutdown_handler)

    # 3. The shared Discord client (P3): ONE gateway connection carries both directions — the inbound
    #    listener and the outbound sender. Without a token, inbound idles and outbound stays dry-run.
    discord_client = None
    sender = None
    token = os.getenv("DISCORD_TOKEN")
    if token:
        from lib.discord.client import DiscordClient  # import here: discord.py only when actually used
        from senses.privacy import consent_setup_hook, register_consent_events
        discord_client = DiscordClient(token)
        # the setup_hook re-registers the PERSISTENT #privacy view (privacy §1 step 3) and launches
        # the roster sweep. It must be installed BEFORE start(): discord.py awaits it at the end of
        # login(), before the gateway connects. Registering the view in on_ready instead fails
        # SILENTLY — the buttons of the already-posted notice stop answering after every restart.
        discord_client.set_setup_hook(consent_setup_hook(discord_client))
        register_consent_events(discord_client)
        sender = make_discord_sender(discord_client)
    else:
        logger.warning("💬 Discord interface idle — no DISCORD_TOKEN in env")

    # 4. Tasks launcher
    try:
        async with asyncio.TaskGroup() as tg:
            # Creiamo i processi paralleli che gireranno contemporaneamente
            atproto_task = tg.create_task(atproto_listener_task())
            discord_task = tg.create_task(discord_bot_task(discord_client)) if discord_client else None
            # D3b: the outbound actions executor — carries the brain's decisions to Discord (dry-run
            # unless SENSES_DELIVER_DRYRUN=0 AND a live sender is connected).
            outbound_task = tg.create_task(outbound_executor_task(sender))
            # blog P3: the PUBLIC-channel executor — publishes transmissions + mind snapshots to the
            # public website API (dry-run unless SENSES_DELIVER_DRYRUN=0 AND INGEST_API_KEY is set).
            blog_task = tg.create_task(blog_outbound_task())
            # rag3 P1: the microscope — the post-hoc QA oracle over every heard sentence
            # (observer-only; RAG3_DISABLED=1 or a missing ANTHROPIC_API_KEY disarms it).
            microscope = tg.create_task(microscope_task())

            # Waiting for sigterms
            await stop_event.wait()

            # Gently shutdown
            logger.info("Shutting down sub threads...")
            atproto_task.cancel()
            if discord_task is not None:
                discord_task.cancel()
            outbound_task.cancel()
            blog_task.cancel()
            microscope.cancel()
            
    except* Exception as eg:
        logger.error(f"❌ Critical error: {eg}")
    finally:
        logger.info("🛑 tokeniko: senses are deep sleeping")

if __name__ == "__main__":
    # main start
    asyncio.run(main())