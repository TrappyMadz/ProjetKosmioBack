import requests


class LlmService():
    prompt_solution = "Tu est un modèle d’extraction d’information. Extrait les informations clés suivantes :\n\n- type : \"solution\"\n- id : vide\n- title : Le titre de la solution\n- metadata : un dictionnaire de 8 entrées :\n  - category : La catégorie de la solution\n  - system : Le système utilisé\n  - type : technique, organisationnelle ou comportentale suivant le type de solution\n  - maturity : \n  - cost_scale : trouver une échelle\n  - complexity : à quel point la solution est compliquée à mettre en place\n  - last_update : vide\n  - contributors : liste des entreprises qui ont contribué à la fiche\n- summary : un résumé de la solution\n- content : un dictionnaire de 9 entrées :\n  - context : un dictionnaire de 5 entrées :\n    - objective : l'objectif global de la solution\n    - target_sites : une liste des types de sites concernés (exemple : logements collectifs, tertiaire)\n    - scope_includes : une liste d'éléments inclus\n    - scope_excludes : une liste d'éléments exclus\n    - prerequisites : une liste de prérequis réglementaires, techniques ou organisationnels\n  - mecanism : un dictionnaire à 2 entrées :\n    - description : description simple du principe de fonctionnement\n    - variants : une liste des différentes variantes possibles\n  - applicability : un dictionnaire à 3 entrées :\n    - conditions : une liste des cas où l'usage de la solution est pertinent\n    - avoid_if : une liste des cas où l'usage est à éviter\n    - constraints : contraintes identifiées\n  - impacts : un dictionnaire de 4 entrées :\n    - energy : estimation qualitative ou valeur de l'énergie économisée ou valorisée\n    - co2 : ordre de grandeur ou fourchette du CO2 évité\n    - costs : un dictionnaire à 3 entrées :\n      - capex : dépenses d'investissement CAPEX avec chiffres\n      - opex : dépenses d'exploitation OPEX avec chiffres\n      - roi : retour sur investissement avec chiffres\n    - co_benefits : une liste des bénéfices apportés par la solution\n  - levers : une liste de leviers associés à la solution\n  - implementation_path : une liste de dictionnaires :\n    - step : Diagnostic initial, Dimensionnement, Installation, Suivi\n    - details : détails pour chaque étape\n  - risks : une liste de dictionnaires :\n    - risk : nom du risque\n    - mitigation : mesures de mitigation\n  - examples : une liste de dictionnaires de cas d'usage :\n    - secteur : secteur d'usage\n    - resume : explication de l'utilisation\n    - link : lien vers la fiche secteur\n  - resources : une liste de dictionnaires de ressources :\n    - title : titre de la ressource\n    - type : type de ressource\n    - link : lien de la ressource\n- contribution : un dictionnaire de 3 entrées :\n  - validation : vide\n  - history : liste vide\n  - improvement_proposal_link : vide\n- traceability : un dictionnaire de 3 entrées :\n  - source_pdf : vide\n  - extraction_confidence : vide\n  - chunks_used : liste vide\n\n# Directives\n- Les informations doivent uniquement provenir du texte fourni.\n- Si une information n'est pas trouvée, laisser la valeur de la clé vide.\n\n# Format de réponse\nTu dois renvoyer un JSON valide."
    prompt_secteur = "Tu est un modèle d’extraction d’information. Extrait les informations clés suivantes :\n\n- type : \"secteur\"\n- id : vide # à implémenter après le passage de l'IA\n- title : Le titre de la fiche qui correspond au nom du secteur\n- metadata : Un dictionnaire contenant 4 entrées :\n  - sub_sectors : Une liste des sous secteurs associés,\n  - company_size : le type d’entreprise sous la forme TPE, PME ou ETI,\n  - last_update : vide\n  - contributors : une listes des entreprises ayant contribués à cette publication\n- summary : résumé des activités, typologies de sites, contraintes métiers\n- content : un dictionnaire contenant 7 entrées :\n  - emissions_profile : un dictionnaire contenant 5 entrées qui définissent la répartition des postes d'émissions :\n    - process : en pourcentage ou ordre de grandeur,\n    - utilities : en pourcentage ou ordre de grandeur,\n    - building : en pourcentage,\n    - transport : en pourcentage,\n    - waste : en pourcentage\n  - challenges : la liste de dictionnaire des enjeux sous la forme :\n    - title : le titre de l'enjeu,\n    - description : la description de l’enjeu\n  - regulations : la liste des réglementations importantes à prendre en compte,\n  - systems_matrix : la liste des systèmes et solutions clés sous la forme de dictionnaire :\n    - system : nom de la solution\n    - impact : impact sous la forme d’une échelle (Faible, Moyen, Fort)\n    - priority : priorité sous forme d’une échelle de 1 à 5 ⭐,\n    - solutions : liste des solutions\n  - sector_path : parcours sectoriel recommandé sous forme d’une liste de dictionnaire qui décrit les actions à faire durant 5 phases (Quick wins (< 3 mois), Optimisations (3–12 mois), Investissements structurants, Nouvelles énergies / changement de combustible, Management & pilotage) :\n    - phase : nom de la phase\n    - action : l’action associée à cette phase\n  - use_case : une liste de dictionnaire d’action à réaliser par sous secteurs :\n    - sub_sector : le sous secteur concerné\n    - action : une liste des actions à effectuer\n    - results : une liste des résultats avec des chiffres\n    - link : le lien vers la fiche projet associée\n  - resources : une liste de dictionnaire contenant les ressources utilisées sous la forme :\n    - title : titre de la ressource\n    - type : type de la ressource\n    - link : lien de la ressource\n- contribution : dictionnaire contenant 4 entrées :\n  - completeness : le niveau de complétude de la fiche dans son ensemble (squelette, partielle, complète)\n  - validator : vide\n  - history : une liste vide\n  - improvement_proposal_link : vide\n- traceability : un dictionnaire de 3 entrées :\n  - source_pdf : vide\n  - extraction_confidence : vide\n  - chunks_used : liste vide\n\n# Directives\n- Les informations doivent uniquement venir du texte que je te donne.\n- Si tu ne trouves pas une information, laisse la valeur de la clé vide.\n\n# Format de réponse\nTu dois renvoyer un .json"

    def __init__(self, config):
        self.config = config

    #juste pour faire une requete mixtral simple
    def mistral_request(self, content):
        url = self.config.url_model_llm
        payload = {
            "max_tokens": 512,
            "messages": [
                {
                    "content": content,
                    "role": "user"
                }
            ],
            "model": self.config.model_llm,
            "temperature": 0,
            "response_format": {"type": "json_object"}
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.access_token}",
        }

        response = requests.post(url, json=payload, headers=headers, verify=False)
        if response.status_code == 200:
            # Handle response
            response_data = response.json()
            # Parse JSON response
            choices = response_data["choices"]
            for choice in choices:
                text = choice["message"]["content"]
                # Process text and finish_reason
                print(text)
        else:
            print("Error:", response.status_code)

    #requete solution
    def solution_request(self):
        self.mistral_request(self.prompt_solution)

    #requete secteur
    def secteur_request(self):
        self.mistral_request(self.prompt_secteur)

    #TODO
    def rag_nlp_completion(self, retrieved_sentences):
        url = self.config.url_model_llm

        messages = [
            #preprompt
            {"role": "system",
             "content": (
                    #préparer le preprompt en donnant les consignes ainsi que le modèle de sortie
                )
            },

            {
                "role": "user",
                "content": f"""Informations fournies : {retrieved_sentences} \

        """
            }
        ]

        payload = {
            "model": self.config.model_llm,
            "temperature": 0,
            "max_tokens": 2000,
            "messages": messages
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.access_token}",
        }

        response = requests.post(url, json=payload, headers=headers, verify = False)
        if response.status_code == 200:
            response_data = response.json()
            return response_data["choices"][0]["message"]["content"]
        else:
            print("Erreur:", response.status_code)
            return None
