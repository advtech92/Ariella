import discord
from discord import app_commands
from discord.ext import commands
import aiosqlite
from gdpr import check_consent, give_consent, revoke_consent


class GDPRCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="consent",
                          description="Give consent to store data")
    async def consent(self, interaction: discord.Interaction):
        await give_consent(interaction.user.id)
        await interaction.response.send_message(
            "Consent given to store your data."
        )

    @app_commands.command(name="revoke_consent",
                          description="Revoke consent to store data")
    async def revoke_consent(self, interaction: discord.Interaction):
        await revoke_consent(interaction.user.id)
        await interaction.response.send_message(
            "Consent revoked and your data has been deleted."
        )

    @app_commands.command(name="privacy_policy",
                          description="View the privacy policy")
    async def privacy_policy(self, interaction: discord.Interaction):
        privacy_text = (
            "Privacy Policy:\n"
            "We collect and store data to provide better services. The data "
            "includes:\n"
            "- User ID\n"
            "- Notes and Strikes added by moderators\n"
            "Data is stored securely and only accessible by authorized "
            "personnel.\n"
            "You can revoke consent at any time by using the /revoke_consent "
            "command.\n"
            "For more details, visit our [website](https://example.com/privacy)."  # noqa: E501
        )
        await interaction.response.send_message(privacy_text)

    @app_commands.command(name="get_my_data",
                          description="Get a copy of your data")
    async def get_my_data(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        async with aiosqlite.connect("ariella.db") as db:
            cursor = await db.execute(
                "SELECT notes, strikes FROM user_notes WHERE user_id = ?",
                (user_id,)
            )
            row = await cursor.fetchone()
            if row:
                notes, strikes = row
                data_text = f"Your data:\nNotes: {notes}\nStrikes: {strikes}"
                await interaction.user.send(data_text)
                await interaction.response.send_message(
                    "Your data has been sent to you privately."
                )
            else:
                await interaction.response.send_message("No data found for you.")  # noqa: E501


async def setup(bot):
    await bot.add_cog(GDPRCommands(bot))
