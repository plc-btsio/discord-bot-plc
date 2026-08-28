import os
# Fichier de variables globales

# Version du bot
VERSION = os.getenv("APP_VERSION")
print(f"APP VERSION : {VERSION}")

# Développeurs du bot
DEVELOPPEURS = ("Ewen GADONNAUD", "Louis MEDO", "Amine KADA")

# ID du salon de veille
VEILLE_CHANNEL_ID = os.getenv("VEILLE_CHANNEL_ID")
print(f"VEILLE_CHANNEL_ID chargé : {VEILLE_CHANNEL_ID}")

# ID du salon pour les CVEs
VEILLE_CVE_CHANNEL_ID = os.getenv("VEILLE_CVE_CHANNEL_ID")
print(f"VEILLE_CVE_CHANNEL_ID chargé : {VEILLE_CVE_CHANNEL_ID}")
