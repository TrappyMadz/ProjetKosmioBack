from controller import rag_controller
import os
import json
from dotenv import load_dotenv
import uvicorn
from service.bdd_service.bdd_service import PostgresService
from config.logging_config import setup_logging, get_logger

# Initialiser le logging dès le démarrage
setup_logging(log_level="INFO")
logger = get_logger(__name__)

app = rag_controller.rag_app

if __name__ == "__main__":

    # 1. Charger les variables du fichier .env
    # Cette ligne lit le fichier .env et met les clés/valeurs dans os.environ
    load_dotenv() 

    # 2. Lire le fichier de configuration JSON
    try:
        with open('src/main/config/config.json', 'r') as f:
            config_data = json.load(f)
    except FileNotFoundError:
        logger.error("Le fichier config.json n'a pas été trouvé.")
        exit()

    # 3. Récupérer le jeton depuis l'environnement
    # Utilisez .get() pour éviter une erreur si la variable n'est pas définie
    access_token_from_env = os.getenv("OVH_API_KEY")

    # 4. Injecter la variable dans la structure JSON
    if access_token_from_env:
        # On met à jour la valeur "access-token"
        config_data['access-token'] = access_token_from_env
        logger.info("Le jeton d'accès a été injecté dans la configuration.")
    else:
        logger.warning("La variable OVH_API_KEY n'a pas été trouvée dans l'environnement.")


    ##Lancer le serveur fastapi avec uvicorn
    logger.info("Démarrage du serveur FastAPI sur le port 8123")
    uvicorn.run(
            "controller.rag_controller:rag_app",  # module:app
            host="0.0.0.0",
            port=8123,
            reload=True  # équivalent de debug=True
        )