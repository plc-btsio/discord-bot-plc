import discord
import os
from discord.ext import commands

# --- 1. Configuration et Chargement ---

DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")


# Récupération automatique des cogs dans les sous-dossiers
async def load_cogs():
    for folder in os.listdir("./cogs"):
        folder_path = os.path.join("./cogs", folder)
        if os.path.isdir(folder_path):
            for filename in os.listdir(folder_path):
                if filename.endswith(".py") and not filename.startswith("__"):
                    cog_path = f"cogs.{folder}.{filename[:-3]}"
                    try:
                        await bot.load_extension(cog_path)
                        print(f"✅ Cog chargé : {cog_path}")
                    except Exception as e:
                        print(f"❌ Erreur de chargement du cog {cog_path} : {e}")


# Permissions du bot
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

# Préfixe des commandes (Non utilisé, mais nécessaire pour discord.py)
bot = commands.Bot(command_prefix="*!*", intents=intents)


# Démarrage du bot
@bot.event
async def on_ready():
    print(f"Connecté en tant que {bot.user} !")
    await load_cogs()  # Chargement des cogs
    try:
        synced = await bot.tree.sync()  # Synchronisation des commandes slash
        print(f"{len(synced)} commandes slash synchronisées !")
    except Exception as e:
        print(e)


# Gestion des Erreurs Globales
@bot.event
async def on_command_error(ctx, error):
    """Gestion des erreurs de commandes préfixées"""
    if isinstance(error, commands.CommandNotFound):
        return
    print(f"❌ Erreur de commande : {error}")


if __name__ == "__main__":
    if not DISCORD_TOKEN:
        print("❌ ERREUR : 'DISCORD_BOT_TOKEN' est manquant dans le .env")
        exit(1)

    print("🚀 Démarrage du bot...")
    try:
        bot.run(DISCORD_TOKEN)
    except Exception as e:
        print(f"❌ Erreur critique au démarrage : {e}")
        exit(1)
