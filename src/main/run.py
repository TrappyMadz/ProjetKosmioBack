from controller import rag_controller
import os
import json
from dotenv import load_dotenv

app = rag_controller.rag_app

# 1. Charger les variables du fichier .env
# Cette ligne lit le fichier .env et met les clés/valeurs dans os.environ
load_dotenv() 

# 2. Lire le fichier de configuration JSON
try:
    with open('src/main/config/config.json', 'r') as f:
        config_data = json.load(f)
except FileNotFoundError:
    print("Erreur : Le fichier config.json n'a pas été trouvé.")
    exit()

# 3. Récupérer le jeton depuis l'environnement
# Utilisez .get() pour éviter une erreur si la variable n'est pas définie
access_token_from_env = os.getenv("OVH_API_KEY")

# 4. Injecter la variable dans la structure JSON
if access_token_from_env:
    # On met à jour la valeur "access-token"
    config_data['access-token'] = access_token_from_env
    print("Succès : Le jeton d'accès a été injecté dans la configuration.")
else:
    print("Avertissement : La variable CLE_API_OVHENDPOINTS n'a pas été trouvée dans l'environnement.")


# 5. Utiliser la configuration mise à jour (config_data)
# Exemple d'utilisation :
url = config_data['url_model_llm']
token = config_data['access-token']

print("-" * 30)
print(f"URL du Modèle : {url}")
print(f"Jeton utilisé : {token[:10]}... (masqué)") 

# config_data est maintenant l'objet JSON complet, prêt à être passé à votre client API.

##Lancer le serveur (ici c est pour flask, à modifier pour d autres frameworks)
#rag_controller.rag_app.run(debug=True, port=8123)