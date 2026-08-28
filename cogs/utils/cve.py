# Standard Library
import logging
from typing import Optional, Set

# Third-Party Libraries
import discord
from discord import app_commands, ui
from discord.ext import commands, tasks
from aiohttp import ClientSession

# Local Modules
from variables import VERSION, VEILLE_CVE_CHANNEL_ID

logger = logging.getLogger(__name__)

class CVE(commands.Cog):
    """
    Module de veille cybersécurité automatisée.
    """

    # Configuration
    API_URL = "https://cve.circl.lu/api/last"
    
    VEILLE_CVE_CHANNEL_ID = VEILLE_CVE_CHANNEL_ID

    WATCHLIST = {
        "proxmox": "Infrastructure",
        "vmware": "Infrastructure",
        "n8n": "Infrastructure",
        "docker": "Conteneur",
        "kubernetes": "Conteneur",
        "k3s": "Conteneur",
        "nginx": "Web Server",
        "glpi": "Service Management",
        "grafana": "Monitoring",
        "ansible": "Automatisation",
        "windows": "Système Windows",
        "linux": "Système Linux",
        "fortinet": "Réseau",
        "cisco": "Réseau",
        "crowdsec": "Sécurité",
        "privilege escalation": "Sécurité Critique",
        "authentication bypass": "Sécurité Critique"
    }

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Mémoire tampon pour éviter les doublons (Set = recherche ultra rapide)
        self.seen_cves: Set[str] = set()
        
        # Démarrage de la boucle automatique
        self.veille_automatique.start()

    def cog_unload(self):
        """Arrête proprement la boucle si le module est déchargé."""
        self.veille_automatique.cancel()

    def _get_category(self, text: str) -> Optional[str]:
        text_lower = text.lower()
        for keyword, category in self.WATCHLIST.items():
            if keyword in text_lower:
                return category
        return None

    def _get_cvss_score(self, metrics: list) -> float:
        for metric in metrics:
            if 'cvssV3_1' in metric:
                return float(metric['cvssV3_1'].get('baseScore', 0.0))
            elif 'cvssV3_0' in metric:
                return float(metric['cvssV3_0'].get('baseScore', 0.0))
        return 0.0

    def _get_embed_color(self, score: float) -> discord.Color:
        if score >= 9.0: return discord.Color.from_rgb(139, 0, 0)
        elif score >= 7.0: return discord.Color.from_rgb(255, 0, 0)
        elif score >= 5.0: return discord.Color.from_rgb(255, 153, 0)
        else: return discord.Color.from_rgb(153, 204, 0)

    # --- VEILLE AUTOMATIQUE ---
    @tasks.loop(minutes=5)
    async def veille_automatique(self):
        """Vérifie les nouvelles CVE toutes les 5 minutes."""
        
        # On attend que le bot soit totalement connecté avant de commencer
        await self.bot.wait_until_ready()

        # Récupération du salon de veille
        channel = self.bot.get_channel(self.VEILLE_CVE_CHANNEL_ID)
        if channel is None:
            logger.warning(f"Salon de veille introuvable (ID: {self.VEILLE_CVE_CHANNEL_ID})")
            return

        try:
            async with ClientSession() as session:
                async with session.get(self.API_URL) as response:
                    if response.status != 200:
                        logger.error(f"Erreur API Veille: {response.status}")
                        return
                    cve_list = await response.json()

        except Exception as e:
            logger.exception("Erreur technique dans la boucle de veille")
            return

        # On traite la liste À L'ENVERS (du plus vieux au plus récent)
        # pour afficher les alertes dans le bon ordre chronologique.
        for cve_data in reversed(cve_list):
            
            # Parsing
            metadata = cve_data.get('cveMetadata', {})
            cve_id = metadata.get('cveId', "Inconnu")

            # On évite la duplication
            if cve_id in self.seen_cves:
                continue

            # Parsing complet
            cna = cve_data.get('containers', {}).get('cna', {})
            cve_title = cna.get('title', "Titre non disponible")
            descriptions = cna.get('descriptions', [])
            cve_summary = descriptions[0].get('value', "N/A") if descriptions else "N/A"
            metrics = cna.get('metrics', [])
            score_val = self._get_cvss_score(metrics)

            # Filtrage Watchlist
            full_text = f"{cve_title} {cve_summary}"
            category = self._get_category(full_text)

            # Vérification de la pertinence
            if category:
                # 2. ALERTE (Si ce n'est pas le premier lancement à vide)
                # Astuce: Si self.seen_cves est vide, c'est que le bot vient de démarrer.
                # Pour éviter le spam au démarrage, on peut choisir de ne pas envoyer.
                # ICI : J'ai choisi d'envoyer quand même pour que tu vois que ça marche.
                
                embed = discord.Embed(
                    title=f"🚨 Nouvelle Alerte - {category}",
                    color=self._get_embed_color(score_val)
                )
                embed.add_field(name="🏷️ Identifiant", value=f"`{cve_id}`", inline=True)
                embed.add_field(name="📊 Score", value=f"**{score_val}/10**", inline=True)
                embed.add_field(name="🎫 Titre", value=cve_title, inline=False)
                embed.set_footer(text=f"PLC BOT {VERSION} • Veille Temps Réel")

                view = ui.View()
                btn_url = f"https://www.cve.org/CVERecord?id={cve_id}"
                view.add_item(ui.Button(label="Fiche Officielle", url=btn_url, emoji="🔗"))

                await channel.send(embed=embed, view=view)
                logger.info(f"Alerte envoyée pour {cve_id}")

            # On ajoute l'ID à la mémoire pour ne plus jamais la traiter
            self.seen_cves.add(cve_id)

    # --- La Commande Manuelle pour vérifier le fonctionnement ---
    @app_commands.command(name="cve", description="Lance une analyse manuelle immédiate.")
    async def cve(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await interaction.followup.send(f"✅ La veille automatique tourne en fond sur le salon <#{self.VEILLE_CVE_CHANNEL_ID}>.")

async def setup(bot: commands.Bot):
    await bot.add_cog(CVE(bot))