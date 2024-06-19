import discord
from discord import app_commands
from discord.ext import commands
import aiosqlite
import os
import sys
import subprocess


class ModCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="addnote", description="Add a note to a user")
    async def add_note(self, interaction: discord.Interaction,
                       user: discord.User, note: str):
        async with aiosqlite.connect("ariella.db") as db:
            cursor = await db.execute(
                "SELECT notes FROM user_notes WHERE user_id = ?",
                (user.id,)
            )
            row = await cursor.fetchone()
            if row:
                notes = row[0] + "\n" + note
                await db.execute(
                    "UPDATE user_notes SET notes = ? WHERE user_id = ?",
                    (notes, user.id)
                )
            else:
                await db.execute(
                    "INSERT INTO user_notes (user_id, notes, strikes) "
                    "VALUES (?, ?, ?)",
                    (user.id, note, 0)
                )
            await db.commit()
        await interaction.response.send_message(
            f"Note added for {user.name}: {note}"
        )

    @app_commands.command(name="warn", description="Warn a user")
    async def warn_user(self, interaction: discord.Interaction,
                        user: discord.User, reason: str):
        async with aiosqlite.connect("ariella.db") as db:
            cursor = await db.execute(
                "SELECT strikes FROM user_notes WHERE user_id = ?",
                (user.id,)
            )
            row = await cursor.fetchone()
            if row:
                strikes = row[0] + 1
                await db.execute(
                    "UPDATE user_notes SET strikes = ? WHERE user_id = ?",
                    (strikes, user.id)
                )
            else:
                strikes = 1
                await db.execute(
                    "INSERT INTO user_notes (user_id, notes, strikes) "
                    "VALUES (?, ?, ?)",
                    (user.id, "", strikes)
                )
            await db.commit()
        await interaction.response.send_message(
            f"User {user.name} warned for: {reason}."
            f"They now have {strikes} strikes."
        )
        await user.send(
            f"You have been warned for: {reason}."
            f"You now have {strikes} strikes."
        )

    @app_commands.command(name="checknotes",
                          description="Check notes and strikes of a user")
    async def check_notes(self, interaction: discord.Interaction,
                          user: discord.User):
        async with aiosqlite.connect("ariella.db") as db:
            cursor = await db.execute(
                "SELECT notes, strikes FROM user_notes WHERE user_id = ?",
                (user.id,)
            )
            row = await cursor.fetchone()
            if row:
                notes, strikes = row
                await interaction.response.send_message(
                    f"Notes for {user.name}: {notes}\nStrikes: {strikes}"
                )
            else:
                await interaction.response.send_message(
                    f"No notes found for {user.name}."
                )

    @app_commands.command(name="update",
                          description="Update Ariellia to the latest version")
    @commands.is_owner()
    async def update(self, interaction: discord.Interaction):
        await interaction.response.send_message("Updating the bot...")
        # Pull latest changes from the repository
        subprocess.run(["git", "pull"])
        # Restart the bot
        await interaction.followup.send("Restarting the bot...")
        os.execv(sys.executable, ['python'] + sys.argv)

    @app_commands.command(name="help", description="List all commands")
    async def help_command(self, interaction: discord.Interaction):
        commands = self.bot.tree.walk_commands()
        help_text = "Here are the available commands:\n"
        for command in commands:
            help_text += f"/{command.name} - {command.description}\n"
        await interaction.response.send_message(help_text)


async def setup(bot):
    await bot.add_cog(ModCommands(bot))
