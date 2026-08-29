"""
Discord bot cog for displaying weather information in bot presence.
"""

import os
import asyncio
import aiohttp
import discord
from discord.ext import commands, tasks

# Environment variables
OPENWEATHER_KEY = os.getenv("OPENWEATHER_API_KEY")
WEATHER_LOCATION = os.getenv("WEATHER_LOCATION", "Tours,FR")
UPDATE_INTERVAL_MIN = int(os.getenv("WEATHER_INTERVAL_MIN", "5"))
WEATHER_LOG_CHANNEL_ID = os.getenv("WEATHER_LOG_CHANNEL_ID")

# Parse channel ID safely
try:
    WEATHER_LOG_CHANNEL_ID = int(WEATHER_LOG_CHANNEL_ID) if WEATHER_LOG_CHANNEL_ID else None
except (TypeError, ValueError):
    WEATHER_LOG_CHANNEL_ID = None

# Weather condition to emoji mapping
EMOJI_MAP = {
    "Clear": "☀️",
    "Clouds": "☁️",
    "Rain": "🌧️",
    "Drizzle": "🌦️",
    "Thunderstorm": "⛈️",
    "Snow": "❄️",
    "Mist": "🌫️",
    "Fog": "🌫️",
}


class WeatherStatus(commands.Cog):
    """Cog to update bot presence with current weather information."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()
        self.last = None  # Cache for last weather data
        self.update_task.start()

    def cog_unload(self):
        """Cleanup when cog is unloaded."""
        self.update_task.cancel()
        asyncio.create_task(self.session.close())

    async def fetch_weather(self) -> dict | None:
        """
        Fetch current weather data from OpenWeatherMap API.

        Returns:
            dict | None: Weather data or None if error occurs
        """
        if not OPENWEATHER_KEY:
            print("WeatherStatus: OPENWEATHER_API_KEY not set")
            return None

        try:
            params = {
                "q": WEATHER_LOCATION,
                "appid": OPENWEATHER_KEY,
                "units": "metric",
                "lang": "fr"
            }
            url = "https://api.openweathermap.org/data/2.5/weather"

            async with self.session.get(url, params=params, timeout=15) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    print(f"WeatherStatus: API error {resp.status}: {text}")
                    return None
                return await resp.json()

        except asyncio.TimeoutError:
            print("WeatherStatus: timeout fetching weather")
            return None
        except Exception as e:
            print(f"WeatherStatus: unexpected error: {e}")
            return None

    def format_presence(self, data: dict) -> str:
        """
        Format weather data into a presence string.

        Args:
            data: Weather data dictionary from API

        Returns:
            str: Formatted presence string (e.g., "☀️ 18°C Tours")
        """
        try:
            temp = round(data["main"]["temp"])
            cond = data["weather"][0]["main"]
            city = data.get("name") or WEATHER_LOCATION
            emoji = EMOJI_MAP.get(cond, "")
            return f"{emoji} {temp}°C {city}"
        except Exception:
            return "Météo indisponible"

    @tasks.loop(minutes=UPDATE_INTERVAL_MIN)
    async def update_task(self):
        """Main task loop to update bot presence with weather."""
        await self.bot.wait_until_ready()

        data = await self.fetch_weather()
        if not data:
            print("WeatherStatus: data empty, skipping presence update")
            return

        text = self.format_presence(data)

        # Skip update if text hasn't changed
        if self.last and self.last.get("text") == text:
            return

        self.last = {"text": text, "ts": discord.utils.utcnow()}
        activity = discord.Activity(type=discord.ActivityType.watching, name=text)

        try:
            await self.bot.change_presence(activity=activity)

            # Send log to Discord channel if configured
            if WEATHER_LOG_CHANNEL_ID is not None:
                asyncio.create_task(self._send_log_channel(text, data))

        except Exception as e:
            print(f"WeatherStatus: failed to change presence: {e}")

    @update_task.before_loop
    async def before_update(self):
        """Wait for bot to be ready before starting update loop."""
        await self.bot.wait_until_ready()
        await asyncio.sleep(5)  # Initial delay

    async def _send_log_channel(self, text: str, data: dict | None = None) -> None:
        """
        Send weather update log to configured Discord channel.

        Args:
            text: Formatted weather text
            data: Optional weather data dictionary
        """
        try:
            channel = self.bot.get_channel(WEATHER_LOG_CHANNEL_ID)

            # Fallback to fetch if channel not in cache
            if channel is None:
                try:
                    channel = await self.bot.fetch_channel(WEATHER_LOG_CHANNEL_ID)
                except Exception:
                    print(
                        f"WeatherStatus: cannot find channel "
                        f"{WEATHER_LOG_CHANNEL_ID} to post logs."
                    )
                    return

            # Build embed
            embed = discord.Embed(
                title="🔄 Mise à jour météo",
                description=text,
                color=0x2F3136,
                timestamp=discord.utils.utcnow()
            )

            # Add extra fields if data available
            if data:
                try:
                    description = data["weather"][0]["description"]
                    temperature = f'{round(data["main"]["temp"])}°C'

                    embed.add_field(name="Conditions", value=description, inline=True)
                    embed.add_field(name="Température", value=temperature, inline=True)
                except Exception:
                    pass

            await channel.send(embed=embed)

        except Exception as e:
            print(f"WeatherStatus: failed to send log message: {e}")


async def setup(bot: commands.Bot):
    """Register the WeatherStatus cog."""
    await bot.add_cog(WeatherStatus(bot))
