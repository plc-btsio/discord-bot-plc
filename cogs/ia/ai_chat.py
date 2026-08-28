import discord
import os
from discord.ext import commands
from discord import app_commands
from collections import defaultdict
from datetime import datetime, timedelta

# Import de la bibliothèque officielle Hugging Face
from huggingface_hub import AsyncInferenceClient
from huggingface_hub.utils import HfHubHTTPError
import asyncio


class AIchat(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # --- Commandes Slash ---
    @app_commands.command(name="ask", description="Pose une question à l'IA (Llama 3)")
    @app_commands.describe(question="La question que tu veux poser")
    async def ask(self, interaction: discord.Interaction, question: str):
        """Commande principale pour interroger l'IA"""

        # Vérification du rate limit
        is_allowed, wait_time = check_rate_limit(interaction.user.id)
        if not is_allowed:
            await interaction.response.send_message(
                f"⏳ Vous avez atteint la limite de requêtes. "
                f"Veuillez patienter {wait_time} secondes.",
                ephemeral=True,
            )
            return

        # Validation de la question
        if len(question) > 500:
            await interaction.response.send_message(
                "❌ Votre question est trop longue (maximum 500 caractères).",
                ephemeral=True,
            )
            return

        # Déférer la réponse immédiatement
        try:
            await interaction.response.defer()
        except discord.errors.NotFound:
            print("⚠️ L'interaction a expiré avant que le bot ne puisse répondre.")
            return

        # Construire l'historique de conversation
        history = get_conversation_history(interaction.user.id)

        # Message système (toujours en premier)
        messages = [
            {
                "role": "system",
                "content": (
                    "Tu incarnes Paul-Louis Courier, un érudit et "
                    "écrivain français. "
                    "Tes réponses sont claires, concises, précises et "
                    "rédigées dans un français "
                    "soutenu mais accessible. Tu es professionnel, "
                    "courtois et vas droit au but. "
                    "Tu peux faire référence aux messages précédents "
                    "de la conversation."
                ),
            }
        ]

        # Ajouter l'historique (si existant)
        messages.extend(history)

        # Ajouter la nouvelle question
        messages.append({"role": "user", "content": question})

        try:
            separator = "=" * 50
            print(f"\n{separator}")
            print("📨 Nouvelle requête /ask")
            print(f"👤 Utilisateur : {interaction.user.name} (ID: {interaction.user.id})")
            print(f"❓ Question : {question}")
            print(f"💬 Historique : {len(history)} messages")
            print(f"{separator}\n")

            # Appel à l'API Hugging Face
            response = await asyncio.wait_for(
                hf_client.chat_completion(
                    model=MODEL_ID,
                    messages=messages,
                    max_tokens=600,  # Augmenté pour réponses
                    temperature=0.7,
                    stream=False,
                ),
                timeout=30.0,  # Timeout de 30 secondes
            )

            # Extraction de la réponse
            reponse_ia = response.choices[0].message.content.strip()

            # Ajouter à l'historique
            add_to_conversation(interaction.user.id, "user", question)
            add_to_conversation(interaction.user.id, "assistant", reponse_ia)

            # Préparer le message
            embed = discord.Embed(
                title="💬 Réponse de Paul-Louis Courier", color=discord.Color.green()
            )
            embed.add_field(name="📝 Votre question", value=question, inline=False)

            # Tronquer si nécessaire
            reponse_finale = truncate_response(reponse_ia)
            embed.add_field(name="✍️ Réponse", value=reponse_finale, inline=False)

            # Ajouter un footer avec info de conversation
            history_len = len(get_conversation_history(interaction.user.id))
            embed.set_footer(
                text=(
                    f"💾 Conversation : {history_len // 2} échanges | "
                    "Utilisez /clear pour réinitialiser"
                )
            )

            await interaction.followup.send(embed=embed)

            print(f"✅ Réponse envoyée avec succès à {interaction.user.name}")

        except asyncio.TimeoutError:
            print("⏱️ Timeout : L'API a mis trop de temps à répondre")
            await interaction.followup.send(
                "⏱️ L'API a mis trop de temps à répondre. Veuillez réessayer.",
                ephemeral=True,
            )

        except HfHubHTTPError as e:
            print(f"❌ Erreur HTTP de l'API Hugging Face : {e}")
            await interaction.followup.send(
                "⚠️ Une erreur est survenue avec l'API de "
                "Hugging Face.\n"
                f"```{e.server_message}```",
                ephemeral=True,
            )

        except Exception as e:
            print(f"❌ Erreur inattendue : {type(e).__name__}: {e}")
            await interaction.followup.send(
                "❌ Une erreur inattendue est survenue. "
                "Consultez la console pour plus de détails.",
                ephemeral=True,
            )

    @app_commands.command(
        name="clear", description="Efface l'historique de ta conversation avec l'IA"
    )
    async def clear(self, interaction: discord.Interaction):
        """Réinitialise l'historique de conversation de l'utilisateur"""
        clear_conversation(interaction.user.id)

        embed = discord.Embed(
            title="🗑️ Conversation réinitialisée",
            description=("Votre historique de conversation a été effacé avec succès !"),
            color=discord.Color.orange(),
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        print(f"🗑️ Conversation effacée pour {interaction.user.name}")


DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")

# Modèle utilisé
MODEL_ID = "meta-llama/Meta-Llama-3-8B-Instruct"

# Configuration du rate limiting (5 requêtes par minute par utilisateur)
RATE_LIMIT_REQUESTS = 5
RATE_LIMIT_WINDOW = 60

# Client IA initialisé une seule fois
hf_client = AsyncInferenceClient(token=HF_TOKEN)

# Système de rate limiting simple
user_requests = defaultdict(list)

# Stockage des conversations (limité dans le temps)
conversations = {}
CONVERSATION_TIMEOUT = 600  # 10 minutes

# --- 3. Fonctions Utilitaires ---


def check_rate_limit(user_id: int) -> tuple[bool, int]:
    """
    Vérifie si l'utilisateur a dépassé la limite de requêtes.
    Retourne (est_autorisé, temps_restant_en_secondes)
    """
    now = datetime.now()
    cutoff = now - timedelta(seconds=RATE_LIMIT_WINDOW)

    # Nettoyer les anciennes requêtes
    user_requests[user_id] = [
        req_time for req_time in user_requests[user_id] if req_time > cutoff
    ]

    if len(user_requests[user_id]) >= RATE_LIMIT_REQUESTS:
        oldest_request = user_requests[user_id][0]
        window_delta = timedelta(seconds=RATE_LIMIT_WINDOW)
        wait_time = int((oldest_request + window_delta - now).total_seconds())
        return False, wait_time

    user_requests[user_id].append(now)
    return True, 0


def get_conversation_history(user_id: int) -> list:
    """Récupère l'historique de conversation d'un utilisateur"""
    if user_id not in conversations:
        conversations[user_id] = {"messages": [], "last_activity": datetime.now()}

    # Vérifier si la conversation n'a pas expiré
    timeout_delta = timedelta(seconds=CONVERSATION_TIMEOUT)
    time_elapsed = datetime.now() - conversations[user_id]["last_activity"]
    if time_elapsed > timeout_delta:
        conversations[user_id]["messages"] = []

    conversations[user_id]["last_activity"] = datetime.now()
    return conversations[user_id]["messages"]


def add_to_conversation(user_id: int, role: str, content: str):
    """Ajoute un message à l'historique de conversation"""
    history = get_conversation_history(user_id)
    history.append({"role": role, "content": content})

    # Limiter à 10 derniers échanges (20 messages)
    if len(history) > 20:
        # Garde le premier message système et les 19 derniers
        conversations[user_id]["messages"] = history[-19:]


def clear_conversation(user_id: int):
    """Efface l'historique de conversation d'un utilisateur"""
    if user_id in conversations:
        conversations[user_id]["messages"] = []


def truncate_response(reponse: str, max_length: int = 1900) -> str:
    """Tronque une réponse à la dernière phrase complète"""
    if len(reponse) <= max_length:
        return reponse

    # Couper à la dernière phrase complète
    truncated = reponse[:max_length]
    last_period = max(truncated.rfind("."), truncated.rfind("!"), truncated.rfind("?"))

    if last_period > max_length * 0.7:
        suffix = "\n\n*[Réponse tronquée]*"
        return truncated[: last_period + 1] + suffix

    return truncated + "...\n\n*[Réponse tronquée]*"


async def setup(bot):
    await bot.add_cog(AIchat(bot))
