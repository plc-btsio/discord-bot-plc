import asyncio
import os

import discord
from discord import app_commands
from discord.ext import commands
from huggingface_hub.utils import HfHubHTTPError

from cogs.ia.ai_chat import MODEL_ID, hf_client, truncate_response


try:
    IDEA_CHANNEL_ID = int(os.getenv("IDEA_CHANNEL_ID", ""))
except ValueError:
    IDEA_CHANNEL_ID = None


class IdeaDeveloper(commands.Cog):
    """Recueille les idées à étudier par le conseil des élèves."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="propose-idee",
        description="Propose une idée au conseil des élèves de BTS SIO",
    )
    @app_commands.describe(idee="L'idée que tu souhaites proposer")
    async def propose_idee(self, interaction: discord.Interaction, idee: str):
        """Publie une idée afin qu'elle soit étudiée par le conseil des élèves."""
        if IDEA_CHANNEL_ID is None:
            await interaction.response.send_message(
                "❌ Le salon des idées n'est pas configuré.", ephemeral=True
            )
            return

        if interaction.channel_id != IDEA_CHANNEL_ID:
            await interaction.response.send_message(
                f"❌ Cette commande est disponible uniquement dans <#{IDEA_CHANNEL_ID}>.",
                ephemeral=True,
            )
            return

        idee = idee.strip()
        if not idee:
            await interaction.response.send_message(
                "❌ Décris une idée avant de l'envoyer au conseil des élèves.",
                ephemeral=True,
            )
            return
        if len(idee) > 2000:
            await interaction.response.send_message(
                "❌ L'idée est trop longue (maximum 2000 caractères).",
                ephemeral=True,
            )
            return

        await interaction.response.defer()

        messages = [
            {
                "role": "system",
                "content": (
                    "Tu aides le conseil des élèves de BTS SIO à étudier des idées. "
                    "À partir de l'idée fournie, rédige un post clair, détaillé et "
                    "réaliste en français. Structure-le avec un titre, l'objectif, "
                    "les bénéficiaires, une description concrète, les avantages, "
                    "les besoins ou étapes de réalisation et les points à discuter. "
                    "Ne présente pas l'idée comme déjà validée et n'invente pas "
                    "d'informations absentes : indique les éléments à préciser."
                ),
            },
            {"role": "user", "content": idee},
        ]

        try:
            response = await asyncio.wait_for(
                hf_client.chat_completion(
                    model=MODEL_ID,
                    messages=messages,
                    max_tokens=800,
                    temperature=0.7,
                    stream=False,
                ),
                timeout=30.0,
            )
            detail = response.choices[0].message.content.strip()

            embed = discord.Embed(
                title="💡 Nouvelle idée proposée",
                description=truncate_response(detail),
                color=discord.Color.blue(),
                timestamp=discord.utils.utcnow(),
            )
            idee_affichee = idee if len(idee) <= 1024 else f"{idee[:1021]}..."
            embed.add_field(name="Idée d'origine", value=idee_affichee, inline=False)
            embed.add_field(
                name="Statut", value="À étudier par le conseil des élèves", inline=False
            )
            embed.set_footer(text=f"Proposée par {interaction.user.display_name}")

            await interaction.followup.send(embed=embed)

        except asyncio.TimeoutError:
            await interaction.followup.send(
                "⏱️ L'IA met trop de temps à détailler l'idée. Veuillez réessayer.",
                ephemeral=True,
            )
        except HfHubHTTPError:
            await interaction.followup.send(
                "⚠️ Le service IA est momentanément indisponible.", ephemeral=True
            )
        except Exception as error:
            print(f"❌ Erreur lors du détail d'une idée : {error}")
            await interaction.followup.send(
                "❌ Une erreur inattendue est survenue.", ephemeral=True
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(IdeaDeveloper(bot))