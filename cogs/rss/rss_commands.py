"""
Discord commands for RSS monitoring management.
"""

import os

import discord
from discord.ext import commands
from discord import app_commands

# Environment variable for authorized role
try:
    ADMIN_ROLE_ID = int(os.getenv("RSS_ADMIN_ROLE_ID", "1431297238356988057"))
except (TypeError, ValueError):
    ADMIN_ROLE_ID = None


class RSSCommands(commands.Cog):
    """Commands for managing RSS monitoring."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _has_admin_role(self, interaction: discord.Interaction) -> bool:
        """
        Check if user has the required admin role.

        Args:
            interaction: Discord interaction object

        Returns:
            bool: True if user has admin role or is server owner
        """
        if ADMIN_ROLE_ID is None:
            await interaction.response.send_message(
                "❌ Le rôle administrateur RSS n'est pas configuré.",
                ephemeral=True
            )
            return False

        # Allow server owner to bypass role check
        if interaction.user.id == interaction.guild.owner_id:
            return True

        # Check if user has the required role
        member = interaction.guild.get_member(interaction.user.id)
        if member is None:
            return False

        role = discord.utils.get(member.roles, id=ADMIN_ROLE_ID)
        if role is None:
            await interaction.response.send_message(
                "❌ Vous n'avez pas les permissions nécessaires pour utiliser cette commande.",
                ephemeral=True
            )
            return False

        return True

    @app_commands.command(
        name="veille-force",
        description="Force l'exécution immédiate de la veille technologique RSS"
    )
    async def force_veille(self, interaction: discord.Interaction):
        """
        Force immediate execution of RSS monitoring.

        This command bypasses the daily schedule and posts an article immediately.
        Requires admin role or server owner permissions.
        """
        # Check permissions
        if not await self._has_admin_role(interaction):
            return

        # Defer response as this operation can take time
        await interaction.response.defer(ephemeral=True)

        # Get the RSS cog
        rss_cog = self.bot.get_cog("RSSFlux")
        if rss_cog is None:
            await interaction.followup.send(
                "❌ Le module RSS n'est pas chargé.",
                ephemeral=True
            )
            return

        try:
            # Execute the monitoring with force=True
            article = await rss_cog.executer_veille(force=True)

            if article is None:
                await interaction.followup.send(
                    "ℹ️ Aucun nouvel article trouvé ou la veille a échoué.",
                    ephemeral=True
                )
                return

            # Success response with article info
            embed = discord.Embed(
                title="✅ Veille forcée exécutée",
                description="Un article a été posté avec succès !",
                color=0x2ECC71,
                timestamp=discord.utils.utcnow()
            )
            embed.add_field(
                name="Article posté",
                value=f"[{article['title']}]({article['link']})",
                inline=False
            )
            embed.add_field(
                name="Date de publication",
                value=article['date'].strftime("%d/%m/%Y à %H:%M"),
                inline=True
            )
            embed.add_field(
                name="Source",
                value=article['source_url'],
                inline=True
            )

            await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            await interaction.followup.send(
                f"❌ Erreur lors de l'exécution de la veille : {e}",
                ephemeral=True
            )

    @app_commands.command(
        name="veille-status",
        description="Affiche le statut de la veille RSS"
    )
    async def veille_status(self, interaction: discord.Interaction):
        """
        Display RSS monitoring status.

        Shows information about the RSS monitoring task, including whether it's running,
        next scheduled execution, and configuration.
        """
        rss_cog = self.bot.get_cog("RSSFlux")
        if rss_cog is None:
            await interaction.response.send_message(
                "❌ Le module RSS n'est pas chargé.",
                ephemeral=True
            )
            return

        # Get task status
        task = rss_cog.verification_flux_rss
        is_running = task.is_running()

        embed = discord.Embed(
            title="📊 Statut de la Veille RSS",
            color=0x3498DB if is_running else 0xE74C3C,
            timestamp=discord.utils.utcnow()
        )

        # Task status
        status_emoji = "✅" if is_running else "❌"
        embed.add_field(
            name="État",
            value=f"{status_emoji} {'Actif' if is_running else 'Inactif'}",
            inline=True
        )

        # Next execution
        if is_running and task.next_iteration:
            next_run = task.next_iteration.strftime("%d/%m/%Y à %H:%M UTC")
            embed.add_field(
                name="Prochaine exécution",
                value=next_run,
                inline=True
            )

        # Configuration
        from .rss_flux import RSS_URLS, VEILLE_CHANNEL_ID
        embed.add_field(
            name="Nombre de flux RSS",
            value=str(len(RSS_URLS)),
            inline=True
        )
        embed.add_field(
            name="Channel cible",
            value=f"<#{VEILLE_CHANNEL_ID}>" if VEILLE_CHANNEL_ID else "Non configuré",
            inline=True
        )
        embed.add_field(
            name="Horaire planifié",
            value="Tous les jours à 8h00 UTC",
            inline=True
        )

        embed.set_footer(text="Utilisez /veille-force pour forcer une exécution")

        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    """Register the RSSCommands cog."""
    await bot.add_cog(RSSCommands(bot))
