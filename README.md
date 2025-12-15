# Projet wikiCO2

## Introduction
 Ce projet contient des APIs pour pouvoir utiliser un Proof of concept permettant de générer des fiches en .md.
## Outils
- Le chunking de document se fait avec la bibliothèque **langchain**. La bibliothèque est complète et est facilement paramétrable.

- Le modèle d'embedding est celui fourni par **OVH AI endpoints** : **bge-multilingual-gemma2**, il est ainsi nécessaire de posséder une clé d'accès pour pouvoir faire des appels API concernant l'embedding. 
- La base de données vectorielle utilisée est ChromaDB, elle se présente sous la forme de collections contenant plusieurs éléments : [[documents, embeddings, metadatas, id],...]
- Le LLM utilisé est un modèle mistral installé sur les serveurs d'OVH : Mixtral-​8x7B-​Instruct-​v0.1, il est possible de le modifier dans config/config.json.
- Un Visual LM installé sur les serveurs d'OVH est utilisé pour le traitement et l'interprétation des images : Mistral-​Small-​3.2-​24B-​Instruct-​2506, il est possible de le modifier dans config/config.json.

## Pre-requis
- Python 3.10+
- langchain
- chromaDB
- clé d'accès OVH Endpoints

### Installation python env à executer

```bash
# Assurer-vous que python3-venv est installé
apt-get install python3-venv

# Créer un environnement virtuel (Python 3.5 ou plus récent)
python3 -m venv venv

# Activer l'environment virtuel 
source venv/bin/activate

# Upgrade pip within the virtual environment
pip install --upgrade pip

# Contient toutes les dépendances nécessaires (se placer à la racine du projet)
pip install -r requirements.txt
```

Il faut toujours activer l'environnement virtuel python avant de lancer le projet.
## Lancer l'application en local

```bash
#placer vous à la racine du projet
ProjetKosmioBack/

#Démarrer le serveur fastAPI
a mettre

## APIs
Vous pouvez directement tester les APIs dans le swagger UI à l'adresse suivante :
```
adresse à mettre
```
## Config

Il vous faut paramétrer dans config/config.json votre token qui donne accès aux APIs AI Endpoints de OVH nécessaire au lancement du projet et les autres paramètres nécessaires :

```bash
"access-token": le token d'accès aux API AI endpoints de OVH
"url_model_llm": L'endpoint du LLM utilisé pour répondre à l'utilisateur
"model_llm": le nom exact du LLM
"max_token_llm": La limite de token en sortie (fixer environ 1000 par défaut)
"temperature_llm": Le degré d'originalité des réponse (fixer 0 par défaut)
"url_model_vlm": L'endpoint du modele d'interprétation des images fournies
"model_vlm": Le nom exact du VLM
"max_token_vlm":  La limite de token en sortie (fixer environ 1000 par défaut)
"temperature_vlm":  Le degré d'originalité des réponse (fixer 0 par défaut)
"url_embedding_model": L'endpoint du model d'embedding  
```
## Troubleshoot

- erreur :
```
ConnectionError, Max retries exceeded
```
Il est possible que vous rencontrier ce type d'erreur à cause du surplus d'appels pour l'embedding, dans ce cas attendez quelques secondes et recommencer ou bien augmenter la durée du sleep entre chaque appel au modèle d'embedding (src/main/service/embedding_service)
## Remarques
