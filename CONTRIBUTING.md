# Guide de Contribution - Bot Discord

Ce document définit les standards de développement pour le dépôt. Toute contribution (humaine ou générée par IA) doit strictement respecter ces conventions.

## Architecture des Cogs
Le projet utilise une architecture modulaire basée sur les `Cogs` du framework `discord.py`. Les modules sont classés dans des sous-dossiers par domaine métier :
* `cogs/management/` : Commandes d'administration, de modération et de gestion du serveur.
* `cogs/utilitaires/` : Outils pratiques pour les utilisateurs (informations, météo, etc.).

## Structure Requise des Fichiers
Chaque fichier source Python doit obligatoirement respecter l'ordre de déclaration suivant :
1. **Dépendances (`imports`)** : Déclarer les modules standards d'abord, puis les modules externes (`discord`), et enfin les imports locaux.
2. **Variables de configuration** : Regrouper les constantes globales et l'extraction des variables d'environnement (ex: `os.getenv`).
3. **Logique métier (Classe Cog)** : Implémenter la classe héritant de `commands.Cog`, contenant la logique, les événements et les commandes.

## Règles de Développement (Directives IA)
* **Commandes Slash** : Utiliser exclusivement les interactions (`@app_commands.command`). Les anciennes commandes à préfixe (`ctx`) sont interdites.
* **Opérations Asynchrones** : Utiliser systématiquement `async`/`await`. Toute requête réseau doit utiliser `aiohttp` pour ne pas bloquer le thread principal.
* **Typage Fort** : Annoter rigoureusement les paramètres (ex: `interaction: discord.Interaction`) pour faciliter la lecture et la détection d'erreurs.
* **Langue** : Le code logique est en anglais, mais les descriptions des commandes et les retours utilisateurs doivent être en français.

## Procédure de déploiement
* Tester systématiquement le chargement du module via la fonction asynchrone `setup(bot)` en bas de chaque fichier.
* Vérifier que l'Embed Discord est utilisé en priorité pour structurer les réponses visuelles complexes.
* Mettre à jour du readme.md en gardant le même style d'écriture.