import os
# Fichier de variables globales

# ID du salon de veille
VEILLE_CHANNEL_ID = os.getenv("VEILLE_CHANNEL_ID")
print(f"VEILLE_CHANNEL_ID chargé : {VEILLE_CHANNEL_ID}")

# ID du salon pour les CVEs
VEILLE_CVE_CHANNEL_ID = os.getenv("VEILLE_CVE_CHANNEL_ID")
print(f"VEILLE_CVE_CHANNEL_ID chargé : {VEILLE_CVE_CHANNEL_ID}")
