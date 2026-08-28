import discord
from discord.ext import commands
from variables import VERSION, DEVELOPPEURS
import datetime


class InfoCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.start_time = datetime.datetime.utcnow()

    # Commande slash
    @discord.app_commands.command(name="info", description="Affiche des informations sur le bot.")
    async def info(self, interaction: discord.Interaction):
        # Déférer la réponse
        await interaction.response.defer()

        # Calcul de l'uptime
        now = datetime.datetime.utcnow()
        uptime = now - self.start_time
        uptime_str = str(uptime).split(".")[0]  # Affiche uniquement heures:minutes:secondes

        # Embed d'information
        embed = discord.Embed(
            title="📊・INFORMATIONS",
            color=0x212554
        )

        # --- Général ---
        embed.add_field(name="Version", value=VERSION, inline=True)
        embed.add_field(name="Langage", value="Python 🐍", inline=True)
        embed.add_field(name="Dernière mise à jour", value="22/10/2025", inline=True)

        # --- Technique ---
        embed.add_field(name="Uptime", value=uptime_str, inline=True)

        # --- Participants ---
        embed.add_field(name="Participants", value=", ".join(DEVELOPPEURS), inline=False)

        # --- Footer ---
        embed.set_footer(text=f"{VERSION} | 💖 Développé par la promo 2025 du BTS SIO")

        # --- Boutons ---
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="GitHub", url="https://github.com/lycee-paul-louis-courier-bts-sio/discord-bot-plc"))
        view.add_item(discord.ui.Button(
            label="Tableau Kanban",
            url=(
                "https://www.notion.so/louismedo/"
                "Fonctionnalit-PLC-BOT-293bef81d6dc8086bc1dd188ccae5e63?source=copy_link"
                )
            )
        )

        file = discord.File("./img/favicon.jpg", filename="favicon.jpg")
        embed.set_thumbnail(url="attachment://favicon.jpg")
        await interaction.followup.send(embed=embed, file=file, view=view)


# Enregistrement sur le Cog
async def setup(bot: commands.Bot):
    await bot.add_cog(InfoCog(bot))
