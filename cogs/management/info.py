import discord
from discord.ext import commands
from datetime import datetime
import os
from utils.logger import send_log

#########################################
# VARIABLE
#########################################

VERSION = os.getenv("APP_VERSION", "N/A")
LANGAGE = "Python 🐍"
URL_RELEASE = f"https://github.com/plc-btsio/discord-bot-plc/releases/tag/{VERSION}"
URL_REPO = "https://github.com/plc-btsio/discord-bot-plc"
URL_CONTRIBUTORS = "https://github.com/plc-btsio/discord-bot-plc/graphs/contributors?all=1"

#########################################
# DISCORD COMMAND
#########################################

file = discord.File("./img/favicon.jpg", filename="logo-bot-plc.jpg")

class InfoCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.start_time = datetime.now()

    # Commande slash
    @discord.app_commands.command(name="info", description="Affiche des informations sur le bot.")
    async def info(self, interaction: discord.Interaction):
        # Déférer la réponse
        await interaction.response.defer()

        # Calcul de l'uptime
        now = datetime.now()
        uptime = now - self.start_time
        uptime_str = str(uptime).split(".")[0]  # Affiche uniquement heures:minutes:secondes

        # Embed d'information
        embed = discord.Embed(
            title="📊・Informations",
            color=0x212554
        )

        # --- Général ---
        embed.add_field(name="Version", value=f"[{VERSION}]({URL_RELEASE})", inline=True)
        embed.add_field(name="Langage", value=LANGAGE, inline=True)

        # --- Technique ---
        embed.add_field(name="Uptime", value=uptime_str, inline=True)

        # --- Footer ---
        date_jour = datetime.now().strftime("%d/%m/%Y %H:%M")
        embed.set_footer(text=f"Management - informations  • {date_jour}", icon_url="attachment://logo-bot-plc.jpg")

        # --- Boutons ---
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="GitHub", url=f"{URL_REPO}"))
        view.add_item(discord.ui.Button(label="Contributeurs", url=f"{URL_CONTRIBUTORS}"))

        embed.set_thumbnail(url="attachment://logo-bot-plc.jpg")
        await interaction.followup.send(embed=embed, file=file, view=view)
        await send_log(self.bot, f"Informations données avec succès.", interaction=interaction, level="DEBUG")

# Enregistrement sur le Cog
async def setup(bot: commands.Bot):
    await bot.add_cog(InfoCog(bot))
