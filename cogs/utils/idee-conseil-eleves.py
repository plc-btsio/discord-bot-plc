import os
import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime

FALLBACK_FORUM_ID = 1543221330348871720

class IdeaFeature(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.forum_id = int(os.getenv("IDEA_CHANNEL_ID", FALLBACK_FORUM_ID))

    @app_commands.command(name="idee-conseil-eleve", description="Soumet une idée au conseil des élèves")
    @app_commands.describe(titre="Titre du post", description="Détail de ton idée")
    async def submit_idea(self, interaction: discord.Interaction, titre: str, description: str):
        await interaction.response.defer(ephemeral=True)

        forum = self.bot.get_channel(self.forum_id)
        if not isinstance(forum, discord.ForumChannel):
            return await interaction.followup.send("Erreur : Le salon cible n'est pas un forum.", ephemeral=True)

        logo_file = discord.File("img/favicon.jpg", filename="logo-bot-plc.jpg")

        embed = discord.Embed(
            title="💡 | Proposition d'idée - Conseil des élèves",
            color=discord.Color.yellow() 
        )
        embed.add_field(name="Auteur", value=interaction.user.mention, inline=False)
        embed.add_field(name="Description", value=description, inline=False)
        
        date_jour = datetime.now().strftime("%d/%m/%Y")
        embed.set_footer(text=f"Utilitaires - idée conseil des élèves • {date_jour}", icon_url="attachment://logo-bot-plc.jpg")

        tag_cible = discord.utils.get(forum.available_tags, name="Non traité")
        tags_a_appliquer = [tag_cible] if tag_cible else []

        try:
            thread_with_message = await forum.create_thread(
                name=titre,
                embed=embed,
                file=logo_file,
                applied_tags=tags_a_appliquer
            )
            
            message_initial = thread_with_message.message
            await message_initial.add_reaction("👍")
            await message_initial.add_reaction("👎")

            await interaction.followup.send(f"Ton idée est postée : {thread_with_message.thread.mention}", ephemeral=True)

        except Exception as e:
            await interaction.followup.send(f"Erreur lors de la création : {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(IdeaFeature(bot))