import json
import os
from typing import Set
from discord.ext import commands


class RSSstorage(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot


def chargement_articles_traites(filepath: str) -> Set[str]:
    """
    Charge l'ensemble des liens d'articles déjà traités depuis un fichier JSON.
    Retourne un Set pour des recherches rapides.
    """
    if not os.path.exists(filepath):
        return set()
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return set(data.get('links', []))
    except json.JSONDecodeError:
        print(f"⚠️ Erreur de lecture du JSON dans {filepath}. Réinitialisation.")
        return set()


def sauvegarde_article_traite(filepath: str, article_url: str, processed_links: Set[str]):
    """
    Ajoute un nouvel article traité à l'ensemble et sauvegarde l'ensemble des liens
    dans le fichier JSON.
    """
    # 1. Ajout de l'article au Set
    processed_links.add(article_url)

    # 2. Assure que le répertoire existe (CRÉATION DU DOSSIER)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    # 3. Sauvegarde (conversion du Set en List pour le JSON)
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({'links': list(processed_links)}, f, indent=4)
        print(f"✅ Fichier JSON mis à jour : {filepath}")
    except Exception as e:
        print(f"❌ Erreur lors de l'écriture du fichier JSON {filepath}: {e}")


# Enregistrement sur le Cog
async def setup(bot):
    await bot.add_cog(RSSstorage(bot))
