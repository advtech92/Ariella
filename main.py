import discord
from discord.ext import commands
import aiosqlite
import asyncio
import os
import sys
import subprocess
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True


class Ariella(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = discord.app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()
        # Load commands
        await self.load_extension('commands')


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


# Load commands
async def load_commands():
    await bot.load_extension('commands')

asyncio.run(load_commands())

bot.run('TOKEN')
