import os
import discord
from datetime import datetime

# Hiérarchie des niveaux de logs (plus le chiffre est haut, plus c'est critique)
LOG_LEVELS = {
    "DEBUG": 10,
    "INFO": 20,
    "WARNING": 30,
    "ERROR": 40
}

async def send_log(bot: discord.Client, message: str, interaction: discord.Interaction = None, level: str = "INFO"):
    level = level.upper()
    
    # Vérification du niveau minimum requis
    current_mode = os.getenv("DEBUG_MODE", "INFO").upper()
    
    # Si le log actuel est moins important que la configuration du .env, on stoppe tout
    if LOG_LEVELS.get(level, 20) < LOG_LEVELS.get(current_mode, 20):
        return

    # Suite du code inchangée
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
        title=f"🔧 Log | {cmd_name}",
        description=f"```{message}```",
        color=colors.get(level, discord.Color.default()),
        timestamp=datetime.utcnow()
    )
    
    if interaction:
        embed.add_field(name="Utilisateur", value=f"{interaction.user} ({interaction.user.mention})")
        embed.add_field(name="Salon", value=interaction.channel.mention if interaction.channel else "DM")

    try:
        await channel.send(embed=embed)
    except Exception as e:
        print(f"[ERROR] Impossible d'envoyer l'embed de log : {e}")