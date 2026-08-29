# 🤖 PLC-Bot — Bot Discord du BTS SIO

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Supported-blue.svg)
![Framework](https://img.shields.io/badge/discord.py-2.4+-green.svg)

## 🚀 Présentation

Le projet **PLC-Bot** est l'assistant Discord officiel développé par et pour les étudiants du **BTS Services Informatiques aux Organisations (SIO)** du **Lycée Paul-Louis Courier**.

Conçu avec une approche DevOps, son objectif est d’**assister l’administration du serveur**, d’**automatiser la diffusion d’informations** et de fournir des outils pratiques (météo, boîte à idées) via une architecture modulaire hautement maintenable.

---

## ✨ Fonctionnalités du bot

| Fonctionnalité | Description | Commande / Déclencheur |
| :--- | :--- | :--- |
| **Informations** | Affiche la version, l'uptime et le lien du dépôt | `/info` |
| **Diagnostic** | Mesure la latence de l'API Discord | `/ping` |
| **Boîte à idées** | Soumet une idée formatée au conseil des élèves | `/idee-conseil-eleve` |
| **Statut dynamique** | Rotation automatique (Météo locale / GitHub) | *Automatique (Tâche de fond)* |

---

## 🏗️ Architecture du dépôt

L'application est structurée autour des **cogs** de `discord.py` pour garantir l'isolation des fonctionnalités :

```text
.
├── cogs/
│   ├── management/       # Commandes d'administration et de diagnostic
│   └── utilitaires/      # Outils utilisateurs (météo, idées, statut)
├── img/                  # Ressources statiques (favicon)
├── main.py               # Point d'entrée de l'application
├── docker-compose.yaml   # Manifeste de déploiement conteneurisé
├── Dockerfile            # Recette de construction de l'image
├── requirements.txt      # Dépendances Python
├── CONTRIBUTING.md       # Standards de code et règles d'IA
└── .env.example          # Template des variables d'environnement
```

---

## 🚀 Utiliser le dépôt

**1. Cloner le dépôt.**

```bash
git clone https://github.com/plc-btsio/discord-bot-plc.git
cd discord-bot-plc
```

* `git clone <url>` : Copie l'intégralité du dépôt distant sur ton ordinateur.
* `cd <dossier>` : Change le répertoire courant pour entrer dans le dossier fraîchement téléchargé.

**2. Créer la branche de travail.**

```bash
git checkout -b feat/nouvelle-fonctionnalite
```

* `checkout` : Commande Git pour changer de branche.
* `-b` : Argument qui demande à Git de créer cette nouvelle branche avant de basculer dessus.
* `feat/...` : Convention de nommage (feat pour feature/fonctionnalité, fix pour correction).

**Nommage des branches :**

| Exemple | Description |
| --- | --- |
| `feat/ajout-slash-command` | **Feature** : Ajout d'une nouvelle fonctionnalité au projet. |
| `fix/crash-api-meteo` | **Fix** : Correction d'un bug ou d'une erreur dans le code existant. |
| `docs/update-readme` | **Documentation** : Création ou modification des fichiers de documentation. |
| `chore/update-discord-py` | **Chore** : Tâche de maintenance logicielle (mise à jour des dépendances, configuration). |
| `refactor/optimisation-cogs` | **Refactor** : Réorganisation ou amélioration du code sans changer son comportement final. |

**3. Configurer les variables d'environnement.**

```text
Copier .env.example -> insérer vos clés API et les ID des salons
```

**Variables d'environnement :**

| Nom | Description |
| --- | --- |
| `DISCORD_BOT_TOKEN` | Jeton secret d'authentification indispensable pour connecter le code à l'API Discord. |
| `IDEA_CHANNEL_ID` | Identifiant numérique unique du salon de type "Forum" où le bot publiera les idées. |
| `OPENWEATHER_API_KEY` | Clé secrète fournie par OpenWeather permettant d'autoriser les requêtes vers leur API météo. |

**4. Lancer le projet localement.**

```bash
docker compose up --build
```

* `up` : Ordonne à Docker Compose de créer et démarrer les conteneurs définis dans le fichier `yaml`.
* `--build` : Force Docker à reconstruire l'image du conteneur. C'est indispensable pour que Docker prenne en compte les modifications faites dans le code source Python.

---

*💖 Développé avec passion par Louis MEDO, Louis Biseray, Ewen Gadonnaud et la promotion du BTS SIO.*
