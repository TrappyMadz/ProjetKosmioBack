# Projet wikiCO2 (Backend)

## Introduction

Ce projet contient des APIs pour pouvoir utiliser un Proof of concept permettant de générer des fiches en .md.

## Architecture technique

- **Langage :** Python 3.11
- **Base de données :** PostgreSQL 15
- **Conteneurisation :** Docker & Docker Compose
- **Driver BDD :** psycopg2-binary

## Outils

- Le chunking de document se fait avec la bibliothèque **langchain**. La bibliothèque est complète et est facilement paramétrable.

- Le modèle d'embedding est celui fourni par **OVH AI endpoints** : **bge-multilingual-gemma2**, il est ainsi nécessaire de posséder une clé d'accès pour pouvoir faire des appels API concernant l'embedding.
- La base de données vectorielle utilisée est ChromaDB, elle se présente sous la forme de collections contenant plusieurs éléments : [[documents, embeddings, metadatas, id],...]
- Le LLM utilisé est un modèle mistral installé sur les serveurs d'OVH : Mixtral-​8x7B-​Instruct-​v0.1, il est possible de le modifier dans config/config.json.
- Un Visual LM installé sur les serveurs d'OVH est utilisé pour le traitement et l'interprétation des images : Mistral-​Small-​3.2-​24B-​Instruct-​2506, il est possible de le modifier dans config/config.json.

## Pre-requis

- git
- docker
- clé d'accès OVH Endpoints

## Installation

### Cloner le projet

```bash
git clone git@github.com:TrappyMadz/ProjetKosmioBack.git
```

### Configurer le projet

Le projet comporte quelques variables à initialiser.

- Dupliquer le fichier `.env.example` et de le renommer en `.env`.
- Modifier les paramètres à votre convenance.

**Exemple de .env :**

```ini
# ---- Config file ----
# Rename this file ".env" before launching the project with docker-compose up --build

# --- Backend config ---
# -- External ports, if those ports are already in use on your device change them. --
# Changes made here only affect how YOU access the services. It does not change the internal configuration of the containers.

# App port : the backend will be accessible from http://localhost:BACKEND_APP_PORT
BACKEND_APP_PORT=8000

# Database port : used to access the database from your device.
BACKEND_DB_PORT=5432

# -- Database configuration --

# Enter here the database credentials. Theses are exemple ones and should be changed
POSTGRES_USER=my_pg_user
POSTGRES_PASSWORD=my_pg_password
POSTGRES_DB=kosmio_db

# -- API KEYS --
# Put your keys here, do not share it

OVH_API_KEY=your_ovh_api_key_here

```

### Lancer l'application

Utilisez docker compose pour construire et lancer les conteneurs :

```bash
docker compose up --build
```

_(Ajoutez l'option `-d` pour le lancer en arrière plan)_

## Fonctionnement

Une fois les conteneurs lancés :

- Api backend : accessible sur `http://localhost:BACKEND_APP_PORT/docs`
- Base de données : accessible sur `http://localhost:BACKEND_DB_PORT`

***Mode dev seulement :** modifier le contenu d'un des .py du projet et enregistrer redémarerra automatiquement le serveur. Conteneur et code sont liés*

## Commandes utiles

- Arrêter les conteneurs :
  ```bash
  docker compose down
  ```
- Voir les logs _(si vous l'avez lancé avec l'option `-d`)_ :
  ```bash
  docker compose logs -f
  ```
  _lazydocker est conseillé pour une meilleure visualisation des logs_

## Troubleshoot

- erreur :

```
ConnectionError, Max retries exceeded
```

Il est possible que vous rencontrier ce type d'erreur à cause du surplus d'appels pour l'embedding, dans ce cas attendez quelques secondes et recommencer ou bien augmenter la durée du sleep entre chaque appel au modèle d'embedding (src/main/service/embedding_service)

## Remarques
