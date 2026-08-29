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

Voici la section réécrite selon ta structure exacte :

**1. Cloner le dépôt.** Télécharge le code source du projet sur ta machine pour pouvoir travailler dessus.

```bash
git clone https://github.com/plc-btsio/discord-bot-plc.git
cd discord-bot-plc
```

* `git clone <url>` : Copie l'intégralité du dépôt distant sur ton ordinateur.
* `cd <dossier>` : Change le répertoire courant pour entrer dans le dossier fraîchement téléchargé.

**2. Créer la branche de travail.** Isole tes futurs développements du code principal pour tester sans casser l'existant.

```bash
git checkout -b feat/nouvelle-fonctionnalite
```

* `checkout` : Commande Git pour changer de branche.
* `-b` : Argument qui demande à Git de créer cette nouvelle branche avant de basculer dessus.
* `feat/...` : Convention de nommage (feat pour feature/fonctionnalité, fix pour correction).

**3. Configurer les variables d'environnement.** Prépare le fichier secret contenant les identifiants nécessaires au lancement.

```bash
cp .env.example .env
```

* `cp <source> <destination>` : Copie le fichier d'exemple (template) pour créer ton propre fichier `.env` que tu pourras modifier avec ton token Discord. Le `.env` est ignoré par Git, ce qui sécurise tes clés.

**4. Lancer le projet localement.** Démarre le bot dans un environnement isolé via Docker pour tester tes modifications.

```bash
docker compose up --build
```

* `up` : Ordonne à Docker Compose de créer et démarrer les conteneurs définis dans le fichier `yaml`.
* `--build` : Force Docker à reconstruire l'image du conteneur. C'est indispensable pour que Docker prenne en compte les modifications que tu viens de faire dans le code source Python.

---

*💖 Développé avec passion par Louis MEDO, Louis Biseray, Ewen Gadonnaud et la promotion du BTS SIO.*
