from aiohttp import web
from plugins import web_server

import pyromod.listen
from pyrogram import Client
from pyrogram.enums import ParseMode
import asyncio
import sys
from datetime import datetime

from config import (
    API_HASH,
    APP_ID,
    LOGGER,
    TG_BOT_TOKEN,
    TG_BOT_WORKERS,
    FORCE_SUB_CHANNEL,
    FORCE_SUB_CHANNEL2,
    CHANNEL_ID,
    PORT
)


class Bot(Client):
    def __init__(self):
        super().__init__(
            name="Bot",
            api_hash=API_HASH,
            api_id=APP_ID,
            plugins={"root": "plugins"},
            workers=TG_BOT_WORKERS,
            bot_token=TG_BOT_TOKEN,
        )
        self.LOGGER = LOGGER

    async def start(self):
        await super().start()
        usr_bot_me = await self.get_me()
        self.uptime = datetime.now()
        self.username = usr_bot_me.username

        # Handle Force Sub Channels
        if FORCE_SUB_CHANNEL:
            try:
                link = (await self.get_chat(FORCE_SUB_CHANNEL)).invite_link
                if not link:
                    await self.export_chat_invite_link(FORCE_SUB_CHANNEL)
                    link = (await self.get_chat(FORCE_SUB_CHANNEL)).invite_link
                self.invitelink = link
            except Exception as a:
                self.LOGGER(__name__).warning(a)
                self.LOGGER(__name__).warning("Bot can't Export Invite link from Force Sub Channel!")
                self.LOGGER(__name__).warning(
                    f"Please Double check the FORCE_SUB_CHANNEL_1 value and make sure the bot is an admin in the channel with Invite Users via Link Permission. "
                    f"Current Force Sub Channel Value: {FORCE_SUB_CHANNEL}"
                )
                self.LOGGER(__name__).info("\nBot Stopped. Join https://t.me/weebs_support for support")
                sys.exit()
        if FORCE_SUB_CHANNEL2:
            try:
                link = (await self.get_chat(FORCE_SUB_CHANNEL2)).invite_link
                if not link:
                    await self.export_chat_invite_link(FORCE_SUB_CHANNEL2)
                    link = (await self.get_chat(FORCE_SUB_CHANNEL2)).invite_link
                self.invitelink2 = link
            except Exception as a:
                self.LOGGER(__name__).warning(a)
                self.LOGGER(__name__).warning("Bot can't Export Invite link from Force Sub Channel!")
                self.LOGGER(__name__).warning(
                    f"Please Double check the FORCE_SUB_CHANNEL_2 value and make sure the bot is an admin in the channel with Invite Users via Link Permission. "
                    f"Current Force Sub Channel Value: {FORCE_SUB_CHANNEL2}"
                )
                self.LOGGER(__name__).info("\nBot Stopped. Join https://t.me/weebs_support for support")
                sys.exit()

        # Validate DB Channel
        try:
            db_channel = await self.get_chat(CHANNEL_ID)
            self.db_channel = db_channel
            test = await self.send_message(chat_id=db_channel.id, text="Test Message")
            await test.delete()
        except Exception as e:
            self.LOGGER(__name__).warning(e)
            self.LOGGER(__name__).warning(
                f"Ensure the bot is an admin in the DB Channel and check the CHANNEL_ID value. Current value: {CHANNEL_ID}"
            )
            sys.exit()

        self.set_parse_mode(ParseMode.HTML)
        self.LOGGER(__name__).info("Bot started successfully!")
        self.LOGGER(__name__).info("Created by https://t.me/codeflix_bots")

        # Start Web Server
        app = web.AppRunner(await web_server())
        await app.setup()
        await web.TCPSite(app, "0.0.0.0", PORT).start()

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__).info("Bot stopped.")

    def run(self):
        """Run the bot."""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.start())
        self.LOGGER(__name__).info("Bot is now running. Thanks to @rohit_1888")
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            self.LOGGER(__name__).info("Shutting down...")
        finally:
            loop.run_until_complete(self.stop())
