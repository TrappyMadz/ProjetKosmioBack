from controller import rag_controller
import os
import json
from dotenv import load_dotenv
from service.bdd_service.bdd_service import PostgresService

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

exemple = {
        "type": "secteur",
        "id": "sec_98765",
        "title": "Industrie Agroalimentaire",
        "metadata": {
            "sub_sectors": [
                "Laiterie",
                "Plats préparés",
                "Boissons",
                "Boulangerie industrielle"
            ],
            "company_size": "PME / ETI",
            "last_update": "2025-11-20",
            "contributors": [
                "Groupe de travail IAA",
                "CITEPA"
            ]
        },
        "summary": "Le secteur agroalimentaire transforme des produits agricoles en aliments. Il est caractérisé par des besoins importants en chaleur (cuisson, pasteurisation) et en froid (conservation).",
        "content": {
            "description": "Avec plus de 15 000 entreprises en France, l'IAA est le premier secteur industriel. Les contraintes sanitaires et la gestion de la chaîne du froid sont structurantes pour la consommation énergétique.",
            "emissions_profile": {
                "process": "60% (Cuisson, évaporation, séchage)",
                "utilities": "25% (Froid industriel, air comprimé, vapeur)",
                "building": "5% (Chauffage locaux, éclairage)",
                "transport": "8% (Logistique aval)",
                "waste": "2% (Effluents)"
            },
            "challenges": [
                {
                    "title": "Décarbonation de la chaleur",
                    "description": "Sortir des chaudières gaz pour la production de vapeur et d'eau chaude."
                },
                {
                    "title": "Fluides frigorigènes",
                    "description": "Remplacement des HFC à fort GWP par des fluides naturels (NH3, CO2, Propane)."
                }
            ],
            "regulations": [
                "Décret Tertiaire (pour les sièges et entrepôts)",
                "F-Gas (Froid)",
                "Quota CO2 (sites ETS)"
            ],
            "systems_matrix": [
                {
                    "system": "Production de froid",
                    "impact": "Moyen à Fort",
                    "priority": "⭐⭐⭐",
                    "solutions": [
                        "HP Flottante",
                        "Récupération de chaleur sur groupes froid",
                        "Free-cooling"
                    ]
                },
                {
                    "system": "Production de vapeur",
                    "impact": "Très Fort",
                    "priority": "⭐⭐⭐",
                    "solutions": [
                        "Chaudière Biomasse",
                        "Pompes à chaleur HT",
                        "Électrification"
                    ]
                },
                {
                    "system": "Air comprimé",
                    "impact": "Faible",
                    "priority": "⭐",
                    "solutions": [
                        "Variation de vitesse",
                        "Détection de fuites"
                    ]
                }
            ],
            "sector_path": [
                {
                    "phase": "Quick wins (< 3 mois)",
                    "action": "Pilotage énergétique, calorifugeage des réseaux, réparation des fuites d'air/vapeur."
                },
                {
                    "phase": "Optimisations (3–12 mois)",
                    "action": "Mise en place de HP flottante, récupération de chaleur fatale simple."
                },
                {
                    "phase": "Investissements structurants",
                    "action": "Installation de PAC industrielles, chaudière biomasse."
                },
                {
                    "phase": "Nouvelles énergies / changement de combustible",
                    "action": "Substitution gaz par biomasse ou électrification des procédés."
                },
                {
                    "phase": "Management & pilotage",
                    "action": "Certification ISO 50001 et mise en place d'un système de management de l'énergie (SME)."
                }
            ],
            "use_cases": [
                {
                    "sub_sector": "Laiterie",
                    "actions": "Installation d'une PAC sur les buées de séchage.",
                    "results": "-40% de consommation gaz.",
                    "link": "https://wikico2.org/projet/dairy-hp"
                },
                {
                    "sub_sector": "Boulangerie",
                    "actions": "Récupération de chaleur sur fours pour ECS.",
                    "results": "Autonomie eau chaude nettoyage.",
                    "link": ""
                }
            ],
            "resources": [
                {
                    "title": "Guide ADEME - Efficacité énergétique en IAA",
                    "type": "Guide technique",
                    "link": "https://example.com/guide-ademe"
                },
                {
                    "title": "Bref Clean Technologies",
                    "type": "Réglementaire",
                    "link": "https://example.com/bref-clean-tech"
                }
            ]
        },
        "contribution": {
            "completeness": "Complète",
            "validator": "Jean Dupont (Expert Sectoriel)",
            "history": [
                "2025-11-20: Validation finale",
                "2025-01-10: Création initiale"
            ],
            "improvement_proposal_link": "https://wikico2.org/feedback/sec_98765"
        },
        "traceability": {
            "source_pdf": "Etude_Sectorielle_IAA_2024.pdf",
            "extraction_confidence": 0.88,
            "chunks_used": [
                "chk_101",
                "chk_102",
                "chk_table_3"
            ]
        }
    }
