## 🤖 - Bot Discord Paul Louis Courier (PLC-Bot)

## 🚀 - Présentation du Projet :

Le **PLC-Bot** est un projet collaboratif mené par les étudiants du **BTS Services Informatiques aux Organisations (SIO)** du **Lycée Paul-Louis Courier**.

Il a été conçu pour le serveur Discord du BTS afin d'**automatiser les tâches d'administration** et de relayer les dernières informations de **Pronote** directement sur le Discord (modifications d'emploi du temps, menu de la cantine, etc.).

---

## ✨ - Fonctionnalités Actuelles (Déployées) :

|         Catégorie        | Commande / Fonction     | Description Détaillée                                                                                                                            |
| :----------------------: | :---------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------- |
|         **Base**         | `/help`, `/ping`        | Commandes d'aide et de vérification de l'état du Bot. **Messages de bienvenue** automatiques aux nouveaux membres.                               |
| **Veille Technologique** | Publication automatique | 𝗣𝘂𝗯𝗹𝗶𝗰𝗮𝘁𝗶𝗼𝗻 𝗮𝘂𝘁𝗼𝗺𝗮𝘁𝗶𝗾𝘂𝗲 d’articles de veille technologique dans un salon dédié, accompagnée d’un **résumé généré par IA**. |
| **Veille CVE** | Publication automatique | 𝗣𝘂𝗯𝗹𝗶𝗰𝗮𝘁𝗶𝗼𝗻 𝗮𝘂𝘁𝗼𝗺𝗮𝘁𝗶𝗾𝘂𝗲 d’articles de CVE publié par le **CIRCL** dans un salon dédié. |
| **IA Conversationnelle** | `/ask`                  | 𝗜𝗻𝘁𝗲𝗿𝗮𝗰𝘁𝗶𝗼𝗻 𝗮𝘃𝗲𝗰 𝘂𝗻𝗲 𝗜𝗔 (modèle **LLaMA**) pour poser des questions techniques directement depuis Discord.                   |
| **Conseil des élèves** | `/propose-idee` | 𝗣𝗿𝗼𝗽𝗼𝘀𝗶𝘁𝗶𝗼𝗻 d’idées mises en forme par l’IA dans le salon dédié. |

---

## 🚧 - Fonctionnalités en Cours de Développement :

|  Catégorie  | Commande / Fonction        | Description Détaillée                                                                                                                                                |
| :---------: | :------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Pronote** | Notifications automatiques | 𝗡𝗼𝘁𝗶𝗳𝗶𝗰𝗮𝘁𝗶𝗼𝗻 𝗱𝗲𝘀 𝗰𝗵𝗮𝗻𝗴𝗲𝗺𝗲𝗻𝘁𝘀 𝗣𝗿𝗼𝗻𝗼𝘁𝗲 *(professeur absent, cours modifié, etc.)* — **fonctionnalité actuellement en développement.** |

---

## 💡 - Fonctionnalités Futures (Projets à venir) :

* **Intégration Pronote/Éléa** : Notification des **notes** ou des **devoirs** récents (nécessite une connexion API sécurisée et validée).
* **Administration** : Commandes avancées pour la **modération** et l'**organisation** du serveur.

---

## 📦 Utilisation du bot

1. Copier le docker compose ci-dessous.
```yaml
---
services:
  bot-plc:
    image: ghcr.io/lycee-paul-louis-courier-bts-sio/discord-bot-plc:latest
    container_name: bot-plc
    restart: unless-stopped
    env_file:
      - .env
```

2. Remplir le `.env` comme ceci :
```.env
VEILLE_CVE_CHANNEL_ID="votre_salon_cve"
VEILLE_CHANNEL_ID="votre_salon_veille_tech"
IDEA_CHANNEL_ID="votre_salon_idees"
DISCORD_BOT_TOKEN="token_de_votre_bot"
HF_TOKEN="token_api_ia"
```

---

## 🤝 - Contribution :

Ce projet est la propriété et l'initiative des étudiants du **BTS SIO du Lycée Paul-Louis Courier**.
Nous **encourageons la collaboration** et les suggestions.

Pour toute question, contribution ou opportunité de partenariat, veuillez contacter l'un des **responsables de projet** ou le **coordinateur de la filière**.

*💖 Développé avec passion par la promotion **2025** du BTS SIO.*