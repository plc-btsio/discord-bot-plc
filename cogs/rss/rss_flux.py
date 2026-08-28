"""
Discord RSS feed monitoring cog for tech watch.
Monitors RSS feeds, selects random articles, and posts AI summaries to forum.
"""

import os
import asyncio
import random
from datetime import datetime, timedelta, time
from typing import Set, Optional

import discord
import feedparser
from discord.ext import commands, tasks
from huggingface_hub import AsyncInferenceClient
from huggingface_hub.utils import HfHubHTTPError

from .storage import chargement_articles_traites, sauvegarde_article_traite

# Configuration
MODEL_ID = "meta-llama/Meta-Llama-3-8B-Instruct"
PROCESSED_FILE = "cogs/rss/processed_articles.json"

RSS_URLS = [
    "https://www.lemondeinformatique.fr/flux-rss/reseaux/rss.xml",
    "https://www.lemondeinformatique.fr/flux-rss/os/rss.xml",
    "https://www.lemondeinformatique.fr/flux-rss/services-it/rss.xml",
]

# Environment variables
try:
    VEILLE_CHANNEL_ID = int(os.getenv("VEILLE_CHANNEL_ID", "1429819792130441316"))
except (TypeError, ValueError):
    VEILLE_CHANNEL_ID = None

try:
    LOG_CHANNEL_ID = int(os.getenv("RSS_LOG_CHANNEL_ID", "1431295319185948873"))
except (TypeError, ValueError):
    LOG_CHANNEL_ID = None

HF_TOKEN = os.getenv("HF_TOKEN")


class RSSFlux(commands.Cog):
    """
    RSS monitoring cog for technical watch.

    Monitors multiple RSS feeds, selects a random article daily at 8:00 UTC,
    generates an AI summary, and creates a forum post on Discord.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.hf_client = AsyncInferenceClient(model=MODEL_ID, token=HF_TOKEN)

        if VEILLE_CHANNEL_ID is not None:
            self.verification_flux_rss.start()
        else:
            asyncio.create_task(
                self._log(
                    "VEILLE_CHANNEL_ID non configuré ou invalide. "
                    "La tâche RSS ne démarrera pas.",
                    level="error"
                )
            )

    def cog_unload(self):
        """Cancel recurring loop when cog is unloaded."""
        if self.verification_flux_rss.is_running():
            self.verification_flux_rss.cancel()

    async def _log(self, message: str, level: str = "info") -> None:
        """
        Send log messages to Discord channel instead of console.

        Args:
            message: Log message to send
            level: Log level (info, warning, error)
        """
        if LOG_CHANNEL_ID is None:
            print(f"[{level.upper()}] {message}")
            return

        try:
            channel = self.bot.get_channel(LOG_CHANNEL_ID)
            if channel is None:
                channel = await self.bot.fetch_channel(LOG_CHANNEL_ID)

            # Emoji mapping for log levels
            emoji_map = {
                "info": "ℹ️",
                "warning": "⚠️",
                "error": "❌",
                "success": "✅"
            }

            emoji = emoji_map.get(level, "📝")
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            embed = discord.Embed(
                title=f"{emoji} RSS Log - {level.upper()}",
                description=message,
                color=self._get_log_color(level),
                timestamp=discord.utils.utcnow()
            )
            embed.set_footer(text=f"Local time: {timestamp}")

            await channel.send(embed=embed)

        except Exception as e:
            print(f"[LOG ERROR] Failed to send log to Discord: {e}")
            print(f"[{level.upper()}] {message}")

    @staticmethod
    def _get_log_color(level: str) -> int:
        """Get embed color based on log level."""
        colors = {
            "info": 0x3498DB,
            "warning": 0xF39C12,
            "error": 0xE74C3C,
            "success": 0x2ECC71
        }
        return colors.get(level, 0x95A5A6)

    def _obtenir_nouveaux_articles(self, processed_links: Set[str]) -> list:
        """
        Parse all RSS feeds and return unprocessed articles from the last 7 days.

        Args:
            processed_links: Set of already processed article links

        Returns:
            list: List of new article dictionaries
        """
        all_new_articles = []
        date_7_days_ago = datetime.now() - timedelta(hours=168)

        for url in RSS_URLS:
            feed = feedparser.parse(url)

            for entry in feed.entries:
                link = entry.link

                if link in processed_links:
                    continue

                try:
                    date_pub = datetime(*entry.updated_parsed[:6])

                    if date_pub < date_7_days_ago:
                        continue

                    all_new_articles.append({
                        "title": entry.title,
                        "link": link,
                        "date": date_pub,
                        "summary": entry.summary,
                        "source_url": url
                    })

                except Exception as e:
                    asyncio.create_task(
                        self._log(
                            f"Erreur de parsing pour {entry.title} ({url}): {e}",
                            level="warning"
                        )
                    )

        return all_new_articles

    async def _generer_resume_ia(self, article: dict) -> str:
        """
        Generate article summary using Llama 3 via Hugging Face API.

        Args:
            article: Article dictionary containing title and summary

        Returns:
            str: AI-generated summary or error message
        """
        messages = [
            {
                "role": "system",
                "content": (
                    "Tu incarnes Paul-Louis Courier, un érudit français, qui rédige un "
                    "compte-rendu clair et concis (maximum 160 mots) de l'actualité IT "
                    "pour des étudiants. Adopte un ton érudit et incisif."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Rédige un compte-rendu à partir du titre et du résumé suivant : "
                    f"Titre de l'article : {article['title']}\n"
                    f"Contenu à résumer : {article['summary']}"
                )
            }
        ]

        try:
            response = await asyncio.wait_for(
                self.hf_client.chat_completion(
                    model=MODEL_ID,
                    messages=messages,
                    max_tokens=250,
                    temperature=0.7,
                    stream=False,
                ),
                timeout=30.0,
            )

            return response.choices[0].message.content.strip()

        except asyncio.TimeoutError:
            await self._log(
                "Timeout : L'API Hugging Face a mis trop de temps à répondre.",
                level="error"
            )
            return "⏱️ **Timeout de l'API.** Le résumé n'a pu être généré."

        except HfHubHTTPError as e:
            await self._log(f"Erreur HTTP de l'API Hugging Face : {e}", level="error")
            return "⚠️ **Erreur API.** Le résumé n'a pu être généré."

        except Exception as e:
            await self._log(
                f"Erreur inattendue lors de la génération du résumé : {type(e).__name__}: {e}",
                level="error"
            )
            return "❌ **Erreur inattendue.** Le résumé n'a pu être généré."

    async def _publier_post_discord(self, article: dict, summary: str) -> bool:
        """
        Post the summary in ForumChannel by creating a new forum post.

        Args:
            article: Article dictionary
            summary: AI-generated summary

        Returns:
            bool: True if post was created successfully
        """
        main_channel = self.bot.get_channel(VEILLE_CHANNEL_ID)

        if not isinstance(main_channel, discord.ForumChannel):
            await self._log(
                f"Le channel ID {VEILLE_CHANNEL_ID} n'est pas un ForumChannel.",
                level="error"
            )
            return False

        embed = discord.Embed(
            title="Synthèse de l'article",
            url=article['link'],
            description=summary,
            color=0x40E0D0,
            timestamp=article['date']
        )
        embed.set_footer(text="Veille Technologique PLC | Débattez de l'article ci-dessous ! 👇")

        post_name = article['title'][:100]

        try:
            await main_channel.create_thread(
                name=post_name,
                content=f"**Article : {article['title']}**\nLien source : {article['link']}",
                embed=embed,
                auto_archive_duration=4320
            )

            await self._log(f"Post Forum créé : {post_name}", level="success")
            return True

        except discord.Forbidden:
            await self._log(
                "Permission refusée : Impossible de créer des Posts dans ce ForumChannel.",
                level="error"
            )
            return False

        except Exception as e:
            await self._log(f"Erreur lors de la création du Post : {e}", level="error")
            return False

    async def executer_veille(self, force: bool = False) -> Optional[dict]:
        """
        Execute the RSS monitoring and article posting process.

        Args:
            force: If True, bypass day-of-week check

        Returns:
            dict: Posted article info or None if no article was posted
        """
        if not force and datetime.now().weekday() != 4:
            await self._log(
                "Jour non Vendredi. La veille hebdomadaire est ignorée.",
                level="info"
            )
            return None

        await self._log("Veille démarrée : Vérification des flux...", level="info")

        processed_links = chargement_articles_traites(PROCESSED_FILE)
        new_articles = self._obtenir_nouveaux_articles(processed_links)

        if not new_articles:
            await self._log(
                "Aucun nouvel article trouvé dans la fenêtre de 7 jours.",
                level="info"
            )
            return None

        article_to_post = random.choice(new_articles)
        await self._log(
            f"Article sélectionné : {article_to_post['title']}",
            level="info"
        )

        summary = await self._generer_resume_ia(article_to_post)
        success = await self._publier_post_discord(article_to_post, summary)

        if success:
            sauvegarde_article_traite(
                PROCESSED_FILE,
                article_to_post['link'],
                processed_links
            )
            await self._log(
                f"Veille terminée. Article posté : {article_to_post['title']}",
                level="success"
            )
            return article_to_post

        return None

    @tasks.loop(time=time(hour=8, minute=0))
    async def verification_flux_rss(self):
        """Main RSS monitoring task - runs daily at 8:00 UTC."""
        await self.executer_veille(force=False)

    @verification_flux_rss.before_loop
    async def avant_verification_flux_rss(self):
        """Wait for bot readiness before starting the monitoring loop."""
        await self.bot.wait_until_ready()

        if not self.verification_flux_rss.is_running():
            await self._log(
                "Délai de 5 minutes avant le premier lancement de la veille RSS...",
                level="info"
            )
            await asyncio.sleep(300)

        await self._log(
            "Bot prêt, surveillance RSS démarrée (Planifiée à 8h00 UTC).",
            level="success"
        )


async def setup(bot: commands.Bot):
    """Register the RSSFlux cog."""
    await bot.add_cog(RSSFlux(bot))
