import asyncio
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

class MakikiBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.guilds = True
        intents.members = True
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Load modular cogs
        await self.load_extension("cogs.shop_sync")
        await self.load_extension("cogs.twitch_alerts")
        print("[ANTISTATIC LAB] Cogs loaded successfully: shop_sync, twitch_alerts")

    async def on_ready(self):
        print(f"[GATEWAY NEXUS] Logged in as {self.user} (ID: {self.user.id})")
        print("Antistatic Lab x Ejected Media pipeline active.")

bot = MakikiBot()

if __name__ == "__main__":
    bot.run(TOKEN)
