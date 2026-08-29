import os
import discord
from discord.ext import commands, tasks
import aiohttp
import asyncio
from utils.logger import send_log

#########################################
# VARIABLE
#########################################

OPENWEATHER_KEY = os.getenv("OPENWEATHER_API_KEY")
WEATHER_LOCATION = os.getenv("WEATHER_LOCATION", "Tours,FR")
ROTATION_INTERVAL_SEC = 300
GITHUB_URL = "https://github.com/plc-btsio/discord-bot-plc"

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

#########################################
# DISCORD COMMAND
#########################################

class StatusFeature(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.current_status_index = 0
        self.weather_cache = "Météo indisponible"
        self.status_loop.start()

    def cog_unload(self):
        self.status_loop.cancel()

    async def fetch_weather(self):
        if not OPENWEATHER_KEY:
            await send_log(self.bot, f"BOT STATUS - API Key manquante", level="ERROR")
            return

        url = f"http://api.openweathermap.org/data/2.5/weather?q={WEATHER_LOCATION}&appid={OPENWEATHER_KEY}&units=metric&lang=fr"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        temp = round(data["main"]["temp"])
                        weather_main = data["weather"][0]["main"]
                        desc = data["weather"][0]["description"]
                        emoji = EMOJI_MAP.get(weather_main, "🌤️")
                        
                        return f"{emoji} {temp}°C à {WEATHER_LOCATION.split(',')[0]} - {desc.capitalize()}"
                    else:
                        return f"WEATHER STATUS | Erreur API ({response.status})"
        except Exception:
            await send_log(self.bot, f"BOT STATUS - Erreur de connexion Météo", level="WARNING")
            return

    @tasks.loop(seconds=ROTATION_INTERVAL_SEC)
    async def status_loop(self):
        await self.bot.wait_until_ready()

        if self.current_status_index == 0:
            self.weather_cache = await self.fetch_weather()
            activity = discord.Activity(
                type=discord.ActivityType.watching,
                name=self.weather_cache
            )
            await self.bot.change_presence(activity=activity)
            self.current_status_index = 1

        else:
            activity = discord.Activity(
                type=discord.ActivityType.playing,
                name="Contribuer ➜ /info"
            )
            await self.bot.change_presence(activity=activity)
            self.current_status_index = 0

async def setup(bot):
    await bot.add_cog(StatusFeature(bot))