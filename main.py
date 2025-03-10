import discord
from discord.ext import commands
import aiosqlite
import os
import sys
import subprocess
import asyncio
from dotenv import load_dotenv

load_dotenv()

GUILD_ID = os.getenv('GUILD_ID')
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True


class Ariella(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents)

    async def setup_hook(self):
        await self.load_extension('commands')
        await self.load_extension('gdpr_commands')
        self.tree.copy_global_to(guild=discord.Object(id=GUILD_ID))
        await self.tree.sync()


bot = Ariella()


# Database setup
async def init_db():
    async with aiosqlite.connect("ariella.db") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS user_notes (
                user_id INTEGER PRIMARY KEY,
                notes TEXT,
                strikes INTEGER
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS user_consent (
                user_id INTEGER PRIMARY KEY,
                consent INTEGER
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
