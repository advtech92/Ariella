import discord
from discord.ext import commands
import aiosqlite
import os
import sys
import subprocess
import asyncio
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True


class Ariella(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents)

    async def setup_hook(self):
        await self.load_extension('commands')
        await self.tree.sync()


bot = Ariella()


# Database setup
async def init_db():
    async with aiosqlite.connect("bot.db") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS user_notes (
                user_id INTEGER PRIMARY KEY,
                notes TEXT,
                strikes INTEGER
            )
        """)
        await db.commit()


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    await init_db()


@bot.event
async def on_guild_join(guild):
    await bot.tree.sync(guild=guild)

bot.run(TOKEN)
