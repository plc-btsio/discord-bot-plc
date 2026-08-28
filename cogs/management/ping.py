import discord
from discord.ext import commands
from variables import VERSION
import time


class Ping(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Commande slash
    @discord.app_commands.command(name="ping", description="Affiche la latence du bot.")
    async def ping(self, interaction: discord.Interaction):
        # Mesurer le temps de début
        start = time.perf_counter()

        # Déférer la réponse (pour mesurer le temps réel)
        await interaction.response.defer()

        # Temps de réponse réel
        end = time.perf_counter()
        response_time_ms = round((end - start) * 1000)

        # Latence API Discord
        api_latency_ms = round(self.bot.latency * 1000)

        # Créer l'embed
        embed = discord.Embed(
            title="🏓・PING",
            color=0x212554
        )
        embed.add_field(name="Latence API", value=f"`{api_latency_ms} ms`", inline=False)
        embed.add_field(name="Traitement de la requête", value=f"`{response_time_ms} ms`", inline=False)

        embed.set_footer(text=f"{VERSION} | *💖 Développé par la promo 2025 du BTS SIO*")

        await interaction.followup.send(embed=embed)


# Enregistrement sur le Cog
async def setup(bot):
    await bot.add_cog(Ping(bot))
