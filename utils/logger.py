import os
import discord
from datetime import datetime

#########################################
# VARIABLE
#########################################

LOG_LEVELS = {
    "DEBUG": 10,
    "INFO": 20,
    "WARNING": 30,
    "ERROR": 40
}

#########################################
# LOGGER
#########################################

async def send_log(bot: discord.Client, message: str, interaction: discord.Interaction = None, level: str = "INFO"):

    level = level.upper()
    
    # Vérification du niveau minimum requis
    current_mode = os.getenv("DEBUG_MODE", "INFO").upper()
    
    # Si le log actuel est moins important que la configuration du .env
    if LOG_LEVELS.get(level, 20) < LOG_LEVELS.get(current_mode, 20):
        return

    cmd_name = interaction.command.name if interaction and interaction.command else "Système"
    print(f"[{level}] {cmd_name} | {message}")

    log_channel_id = os.getenv("LOG_CHANNEL_ID")
    if not log_channel_id:
        return
        
    channel = bot.get_channel(int(log_channel_id))
    if not channel:
        return

    colors = {
        "INFO": discord.Color.blue(),
        "WARNING": discord.Color.yellow(),
        "ERROR": discord.Color.red()
    }
    
    embed = discord.Embed(
        title=f"🔧 Log ・ {cmd_name}",
        color=colors.get(level, discord.Color.default())
    )
    
    if interaction:
        embed.add_field(name="Utilisateur", value=f"{interaction.user.mention}")
        embed.add_field(name="Salon", value=interaction.channel.mention if interaction.channel else "DM")

    # Transcript
    embed.add_field(name="Niveau", value=f"{level}", inline=True)
    embed.add_field(name="Transcript", value=f"```{message}```", inline=False)

    # Footer
    logo_file = discord.File("img/favicon.jpg", filename="logo-bot-plc.jpg")
    date_jour = datetime.now().strftime("%d/%m/%Y %H:%M")
    embed.set_footer(text=f"Système - log • {date_jour}", icon_url="attachment://logo-bot-plc.jpg")

    try:
        await channel.send(embed=embed, file=logo_file)
    except Exception as e:
        await send_log(f"Idée 'Impossible d'envoyer l'embed de log : {e}", level="ERROR")