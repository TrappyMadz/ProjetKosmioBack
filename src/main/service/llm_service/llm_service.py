import requests
import json
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from concurrent.futures import ThreadPoolExecutor, as_completed
import service.llm_service.qualimetrie as qualimetrie 
import math

class LlmService():
    prompt_solution = """
    Tu est un modèle d’extraction d’information. 
    Tu dois uniquement que extraire les mots clés. 
    Si une information n'est pas trouvée, laisser la valeur de la clé vide.
    # Format de réponse
    Tu dois renvoyer un JSON valide.
    Extrait les informations clés suivantes :
    - type : "solution"
    - id : vide
    - title : Le titre de la solution
    - metadata : un dictionnaire de 8 entrées :
        - category : La catégorie de la solution
        - system : Le système utilisé
        - type : technique, organisationnelle ou comportentale suivant le type de solution
        - maturity : vide
        - cost_scale : vide
        - complexity : a quel point la solution est compliquée à mettre en place
        - last_update : vide
        - contributors : liste des entreprises qui ont contriduée à la fiche
    - summary : un resumé de la solution
    - content : un dictionnaire de 9 entrées :
        - context : un dictionnaire de 5 entrées :
            - objective : l'objectif global de la solution
            - target_sites : une liste des types de sites concernés (exemple : logements collectifs, tertiaire)
            - scope_includes : une liste d'éléments inclues !!!
            - scope_excludes : une liste d'éléments exclues !!!
            - prerequisites : une liste de prérecis réglementaires, techniques ou organisationnels
        - mecanism : un dictionnaire à 2 entrées :
            - description : Description simple du principe de fonctionnement
            - variants : Une liste des diffèrentes variantes possible au niveau du fonction
        - applicability : un dictionnaire à 3 entrées :
            - conditions : une liste des cas où l'usage de la solution semble pertient
            - avoid_if : une liste des cas où l'usage est a éviter
        - impacts : un dictionnaire de 4 entrées :
            - energy : estimation qualitative ou valeur de l'énergie dépensée
            - co2 : ordre de grandeur ou fourchette du co2 produit
            - costs : un dictionnaire à 3 entrées :
            - capex : dépenses d'investissement capex en détaille avec des chiffres
            - opex : dépenses d'exploitation opex en détaille avec des chiffres
            - co_benefits : une liste des bénéfices qu'amène la solution
        - levers : une liste leviers associés à la solution
        - implementation_path : une liste de dictionnaires : 
            - step : "Diagnostic initial", "Dimensionnement", "Installation", "Suivi"
            - details : les détails pour chaques étapes
        - risks : une liste de dictionnaire de la forme :
            - risk : nom du risque
        - exemples : une liste de dictionnaire de cas d'usage de la forme :
            - secteur : secteur d'usage
            - resume : explication de l'utilisée
            - link : lien vers la fiche secteur
        - resources : une liste de dictionnaire resource de la forme :
            - title : titre de la resource
            - type : type de resource
            - link : lien de la resource
    - contribution : dictionnaire de 3 entrées :
        - validation : vide
        - history : liste vide
        - improvement_proposal_link : vide
    - traceability : dictionnaire à 3 entrées :
        - source_pdf : vide
        - extraction_confidence : vide
        - chunks_used : liste vide
    """
    prompt_secteur = """
    Tu est un modèle d’extraction d’information.
    Tu dois uniquement que extraire les mots clés.
    - Si tu ne trouves pas une information, laisse la valeur de la clé vide.
    # Format de réponse
    Tu dois renvoyer un .json.
    Extrait les informations clés suivantes :
    - type : "sector"
    - id : vide
    - title : Le titre de la fiche qui correspond au nom du secteur
    - metadata : Un dictionnaire contenant 4 entrées :
        - sub_sectors : Une liste des sous secteurs associés, 
        - company_size : le type d’entreprise sous la forme TPE, PME ou ETI, 
        - last_update : vide
        - contributors : une listes des entreprises ayant contribués à cette publication
    - summary : résumé des activités, typologies de sites, contraintes métiers
    - content : un dictionnaire contenant 7 entrées : 
        - emissions_profile : un dictionnaire contenant 5 entrées qui définissent la répartition des postes d'émissions : 
            - process : en pourcentage ou ordre de grandeur,
            - utilities : en pourcentage ou ordre de grandeur,
            - building : en pourcentage,
            - transport : en pourcentage,
            - waste : en pourcentage
        - challenges : la liste de dictionnaire des enjeux sous la forme 
            - title : le titre de l'enjeu, 
            - description : la description de l’enjeux
        - regulations : la liste des réglementations importante à prendre en compte,
        - systems_matrix : la liste des systèmes et solutions clés sous la forme de dictionnaire : 
            - system : nom de la solution
            - impact : impact sous la forme d’une échelle (Faible, Moyen, Fort)
            - priority : prioritée sous forme d’une échelle de 1 à 5 ⭐,
            -solutions : liste des solutions
        - sector_path : parcours sectoriel recommandé sous forme d’une liste de dictionnaire qui décrit les actions à faire durant 5 phases (Quick wins (< 3 mois), Optimisations (3–12 mois), Investissements structurants, Nouvelles énergies / changement de combustible, Management & pilotage) : 
            - phase : nom de la phase
            - action : l’action associée à cette phase
        - use_case : une liste de dictionnaire d’action à réaliser par sous secteurs : 
            - sub_sector : le sous secteur concerné
            - action : une liste des actions à effectuer
            - results : une liste des résultats avec des chiffres
            - link : le lien vers la fiche projet associée
        - resources : une liste de dictionnaire contenant les resources utilisées sous la forme : 
            - title : titre de la resource
            - type : type de la resource
            - link : lien de la resource
    - contribution : dictionnaire contenant 4 entrées : 
        - completeness : le niveau de complétude de la fiche dans son ensemble (squelette, partielle, complète)
        - validator : vide
        - history : une liste vide
        - improvement_proposal_link : vide
    -traceability : un dictionnaire de 3 entrées
        - source_pdf : vide
        - extraction_confidence : vide
        - chunks_used : liste vide"""

    def __init__(self, config):
        self.config = config
    
    # Requete à mistral, retourne le json demandé par le prompt dans le payload
    def mistral_request(self,prompt,content):
        print("Envoi de la requête à Mistral avec le prompt :")
        print(prompt)
        url = self.config.url_model_llm

        payload = {
            "messages": [
                {"content": prompt, "role": "system"},
                {"content": content, "role": "user"}
            ],
            "model": self.config.model_llm,
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
            "logprobs": True
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.access_token}",
        }

        # 1. Configuration d'une session avec auto-retry
        # Cela permet de relancer la requête si la connexion est coupée brutalement
        session = requests.Session()
        retries = Retry(
            total=3,                # Nombre de tentatives
            backoff_factor=1,       # Attend 1s, 2s, 4s entre les essais
            status_forcelist=[502, 503, 504], # Retente si le serveur est surchargé
            raise_on_status=False
        )
        session.mount("https://", HTTPAdapter(max_retries=retries))
        session.mount("http://", HTTPAdapter(max_retries=retries))

        try:
            # 2. Ajout d'un timeout (indispensable)
            # (timeout_connexion, timeout_lecture)
            # On laisse 150 secondes au modèle pour générer le JSON complet
            response = session.post(
                url, 
                json=payload, 
                headers=headers, 
                verify=False, 
                timeout=(20, 150) 
            )
            print(f"Réponse reçue de Mistral avec le code {response.status_code}")

            if response.status_code == 200:
                response_data = response.json()
                # Sécurisation de l'accès aux données
                choices = response_data.get("choices", [])
                if not choices:
                    return {"error": "No choices in response"}

                text = choices[0]["message"]["content"]

                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    print("Failed to parse JSON content, returning raw text.")
                    return text
            else:
                print(f"Error {response.status_code}: {response.text}")
                return None

        except requests.exceptions.ChunkedEncodingError as e:
            print(f"Connexion interrompue pendant la lecture du flux (IncompleteRead): {e}")
            return {"error": "stream_interrupted", "details": str(e)}
        except requests.exceptions.Timeout:
            print("Le serveur Mistral a mis trop de temps à répondre (Timeout).")
            return {"error": "timeout"}
        except Exception as e:
            print(f"Erreur inattendue : {e}")
            return None
        
    # Fonction qui lance les 3 requetes mistral pour récupérer les différentes parties du json solution, puis les assemble en un json final et calcul le taux de complétion de la fiche solution
    def mistral_request_solution(self,content):

        ## Les prompts pour chaques parties
        prompt_title_metadata_summary = """
        Tu est un modèle d’extraction d’information.
        Tu dois uniquement que extraire les mots clés.
        Si une information n'est pas trouvée, laisser la valeur de la clé vide.
        
        # Format de réponse
        Tu dois renvoyer un JSON valide.
        
        Extrait les informations clés suivantes :
        - type : "solution"
        - id : vide
        - title : Le titre de la solution
        - metadata : un dictionnaire de 8 entrées :
            - category : La catégorie de la solution
            - system : Le système utilisé
            - type : technique, organisationnelle ou comportentale suivant le type de solution
            - maturity : vide
            - cost_scale : vide
            - complexity : a quel point la solution est compliquée à mettre en place
            - last_update : vide
            - contributors : liste des entreprises qui ont contriduée à la fiche
        - summary : un resumé de la solution
        """
        ## Attention les deux resultats de ces prompt son à integrer dans content
        prompt_content_firstpart = """
        Tu est un modèle d’extraction d’information.
        Tu dois uniquement que extraire les mots clés.
        Si une information n'est pas trouvée, laisser la valeur de la clé vide.
        # Format de réponse
        Tu dois renvoyer un JSON valide.
        Extrait les informations clés suivantes :
        - context : un dictionnaire de 5 entrées :
            - objective : l'objectif global de la solution
            - target_sites : une liste des types de sites concernés (exemple : logements collectifs, tertiaire)
            - scope_includes : une liste d'éléments inclues !!!
            - scope_excludes : une liste d'éléments exclues !!!
            - prerequisites : une liste de prérecis réglementaires, techniques ou organisationnels
        - mecanism : un dictionnaire à 2 entrées :
            - description : Description simple du principe de fonctionnement
            - variants : Une liste des diffèrentes variantes possible au niveau du fonction
        - applicability : un dictionnaire à 3 entrées :
            - conditions : une liste des cas où l'usage de la solution semble pertient
            - avoid_if : une liste des cas où l'usage est a éviter
        - impacts : un dictionnaire de 4 entrées :
            - energy : estimation qualitative ou valeur de l'énergie dépensée
            - co2 : ordre de grandeur ou fourchette du co2 produit
            - costs : un dictionnaire à 3 entrées :
            - capex : dépenses d'investissement capex en détaille avec des chiffres
            - opex : dépenses d'exploitation opex en détaille avec des chiffres
            - co_benefits : une liste des bénéfices qu'amène la solution
        - levers : une liste leviers associés à la solution
        """
        prompt_content_lastpart = """
        Tu est un modèle d’extraction d’information.
        Tu dois uniquement que extraire les mots clés.
        Si une information n'est pas trouvée, laisser la valeur de la clé vide.
        # Format de réponse
        Tu dois renvoyer un JSON valide.
        Extrait les informations clés suivantes :
        - implementation_path : une liste de dictionnaires : 
            - step : "Diagnostic initial", "Dimensionnement", "Installation", "Suivi"
            - details : les détails pour chaques étapes
        - risks : une liste de dictionnaire de la forme :
            - risk : nom du risque
        - exemples : une liste de dictionnaire de cas d'usage de la forme :
            - secteur : secteur d'usage
            - resume : explication de l'utilisée
            - link : lien vers la fiche secteur
        - resources : une liste de dictionnaire resource de la forme :
            - title : titre de la resource
            - type : type de resource
            - link : lien de la resource
        """

        # Lancement des 3 requêtes pour récupérer les json (exécution en parallèle)
        results = {}
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_to_key = {
                executor.submit(self.mistral_request, prompt_title_metadata_summary, content): "title_metadata_summary",
                executor.submit(self.mistral_request, prompt_content_firstpart, content): "content_firstpart",
                executor.submit(self.mistral_request, prompt_content_lastpart, content): "content_lastpart",
            }
            for future in as_completed(future_to_key):
                key = future_to_key[future]
                try:
                    results[key] = future.result()
                except Exception as e:
                    results[key] = {"error": str(e)}

        # Validation et normalisation des fragments
        def _safe_dict(res, name):
            if res is None:
                print(f"Fragment {name} returned None, using empty dict")
                return {}
            if isinstance(res, dict) and "error" in res:
                print(f"Fragment {name} error: {res.get('error')}")
                return {}
            if isinstance(res, dict):
                return res
            if isinstance(res, str):
                try:
                    parsed = json.loads(res)
                    if isinstance(parsed, dict):
                        return parsed
                except Exception:
                    print(f"Fragment {name} returned non-json string; using empty dict")
            return {}

        json_title_metadata_summary = _safe_dict(results.get("title_metadata_summary"), "title_metadata_summary")
        json_content_firstpart = _safe_dict(results.get("content_firstpart"), "content_firstpart")
        json_content_lastpart = _safe_dict(results.get("content_lastpart"), "content_lastpart")

        # Création du json final avec calcul du taux de completion
        final_json = {
            "type": "solution",
            "id": "",
            "title": json_title_metadata_summary.get("title", ""),
            "metadata": json_title_metadata_summary.get("metadata", {}),
            "summary": json_title_metadata_summary.get("summary", ""),
            "content": {}
        }

        # Fusionner en sécurité les deux parties de content
        final_content = {}
        if isinstance(json_content_firstpart, dict):
            final_content.update(json_content_firstpart)
        if isinstance(json_content_lastpart, dict):
            final_content.update(json_content_lastpart)
        final_json["content"] = final_content
        ## Calcul du taux de complétion
        tauxCompletion = qualimetrie.taux_remplissage(final_json)
        print(f"Taux de complétion : {tauxCompletion*100:.2f}%")

        ## Ajout des informations complèmentaires
        final_json["contribution"] = {
            "completeness": f"{tauxCompletion*100:.2f}%",
            "validation": "",
            "history": [],
            "improvement_proposal_link": ""
        }
        final_json["traceability"] = {
            "source_pdf": "",
            "extraction_confidence": "",
            "chunks_used": []
        }

        print("JSON final généré :")
        print(json.dumps(final_json, indent=2, ensure_ascii=False))

        return final_json
    
    # Fonction qui lance les 3 requetes mistral pour récupérer les différentes parties du json solution, puis les assemble en un json final et calcul le taux de complétion de la fiche solution, avec gestion des erreurs de flux et d'execution
    def mistral_request_secteur(self,content):

        ## Les prompts pour chaques parties
        prompt_title_metadata_summary = """
        Tu est un modèle d’extraction d’information.
        Tu dois uniquement que extraire les mots clés.
        Si une information n'est pas trouvée, laisser la valeur de la clé vide.
        
        # Format de réponse
        Tu dois renvoyer un JSON valide.
        
        Extrait les informations clés suivantes :
        - type : "sector"
        - id : vide
        - title : Le titre de la fiche qui correspond au nom du secteur
        - metadata : Un dictionnaire contenant 4 entrées :
            - sub_sectors : Une liste des sous secteurs associés, 
            - company_size : le type d’entreprise sous la forme TPE, PME ou ETI, 
            - last_update : vide
            - contributors : une listes des entreprises ayant contribués à cette publication
        - summary : résumé des activités, typologies de sites, contraintes métiers
        """
        ## Attention les deux resultats de ces prompt son à integrer dans content
        prompt_content_firstpart = """
        Tu est un modèle d’extraction d’information.
        Tu dois uniquement que extraire les mots clés.
        Si une information n'est pas trouvée, laisser la valeur de la clé vide.
        # Format de réponse
        Tu dois renvoyer un JSON valide.
        Extrait les informations clés suivantes :
         - emissions_profile : un dictionnaire contenant 5 entrées qui définissent la répartition des postes d'émissions : 
            - process : en pourcentage ou ordre de grandeur,
            - utilities : en pourcentage ou ordre de grandeur,
            - building : en pourcentage,
            - transport : en pourcentage,
            - waste : en pourcentage
        - challenges : la liste de dictionnaire des enjeux sous la forme 
            - title : le titre de l'enjeu, 
            - description : la description de l’enjeux
        - regulations : la liste des réglementations importante à prendre en compte,
        - systems_matrix : la liste des systèmes et solutions clés sous la forme de dictionnaire : 
            - system : nom de la solution
            - impact : impact sous la forme d’une échelle (Faible, Moyen, Fort)
            - priority : prioritée sous forme d’une échelle de 1 à 5 ⭐,
            -solutions : liste des solutions
        """
        prompt_content_lastpart = """
        Tu est un modèle d’extraction d’information.
        Tu dois uniquement que extraire les mots clés.
        Si une information n'est pas trouvée, laisser la valeur de la clé vide.
        # Format de réponse
        Tu dois renvoyer un JSON valide.
        Extrait les informations clés suivantes :
        - sector_path : parcours sectoriel recommandé sous forme d’une liste de dictionnaire qui décrit les actions à faire durant 5 phases (Quick wins (< 3 mois), Optimisations (3–12 mois), Investissements structurants, Nouvelles énergies / changement de combustible, Management & pilotage) : 
            - phase : nom de la phase
            - action : l’action associée à cette phase
        - use_case : une liste de dictionnaire d’action à réaliser par sous secteurs : 
            - sub_sector : le sous secteur concerné
            - action : une liste des actions à effectuer
            - results : une liste des résultats avec des chiffres
            - link : le lien vers la fiche projet associée
        - resources : une liste de dictionnaire contenant les resources utilisées sous la forme : 
            - title : titre de la resource
            - type : type de la resource
            - link : lien de la resource
        """

        # Lancement des 3 requêtes pour récupérer les json (exécution en parallèle)
        results = {}
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_to_key = {
                executor.submit(self.mistral_request, prompt_title_metadata_summary, content): "title_metadata_summary",
                executor.submit(self.mistral_request, prompt_content_firstpart, content): "content_firstpart",
                executor.submit(self.mistral_request, prompt_content_lastpart, content): "content_lastpart",
            }
            for future in as_completed(future_to_key):
                key = future_to_key[future]
                try:
                    results[key] = future.result()
                except Exception as e:
                    results[key] = {"error": str(e)}

        # Validation et normalisation des fragments
        def _safe_dict(res, name):
            if res is None:
                print(f"Fragment {name} returned None, using empty dict")
                return {}
            if isinstance(res, dict) and "error" in res:
                print(f"Fragment {name} error: {res.get('error')}")
                return {}
            if isinstance(res, dict):
                return res
            if isinstance(res, str):
                try:
                    parsed = json.loads(res)
                    if isinstance(parsed, dict):
                        return parsed
                except Exception:
                    print(f"Fragment {name} returned non-json string; using empty dict")
            return {}

        json_title_metadata_summary = _safe_dict(results.get("title_metadata_summary"), "title_metadata_summary")
        json_content_firstpart = _safe_dict(results.get("content_firstpart"), "content_firstpart")
        json_content_lastpart = _safe_dict(results.get("content_lastpart"), "content_lastpart")

        # Création du json final avec calcul du taux de completion
        final_json = {
            "type": "sector",
            "id": "",
            "title": json_title_metadata_summary.get("title", ""),
            "metadata": json_title_metadata_summary.get("metadata", {}),
            "summary": json_title_metadata_summary.get("summary", ""),
            "content": {}
        }

        # Fusionner en sécurité les deux parties de content
        final_content = {}
        if isinstance(json_content_firstpart, dict):
            final_content.update(json_content_firstpart)
        if isinstance(json_content_lastpart, dict):
            final_content.update(json_content_lastpart)
        final_json["content"] = final_content
        ## Calcul du taux de complétion
        tauxCompletion = qualimetrie.taux_remplissage(final_json)
        print(f"Taux de complétion : {tauxCompletion*100:.2f}%")

        ## Ajout des informations complèmentaires
        final_json["contribution"] = {
            "completeness": f"{tauxCompletion*100:.2f}%",
            "validation": "",
            "history": [],
            "improvement_proposal_link": ""
        }
        final_json["traceability"] = {
            "source_pdf": "",
            "extraction_confidence": "",
            "chunks_used": []
        }

        print("JSON final généré :")
        print(json.dumps(final_json, indent=2, ensure_ascii=False))

        return final_json
    
############# Fonctions obsolètes #############

    # Fonction obsolète ne traitant pas les erreurs de flux, à remplacer par mistral_request_solution qui traite les erreurs et utilise des requetes en parallèle pour les différentes parties du json solution
    def mistral_request_solution_obs(self, content):
        url = self.config.url_model_llm
        payload = {
            "messages": [
                {"content": self.prompt_solution, "role": "system"},
                {"content": content, "role": "user"}
            ],
            "model": self.config.model_llm,
            "temperature": 0.1,
            "response_format": {"type": "json_object"}
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.access_token}",
        }

        # 1. Configuration d'une session avec auto-retry
        # Cela permet de relancer la requête si la connexion est coupée brutalement
        session = requests.Session()
        retries = Retry(
            total=3,                # Nombre de tentatives
            backoff_factor=1,       # Attend 1s, 2s, 4s entre les essais
            status_forcelist=[502, 503, 504], # Retente si le serveur est surchargé
            raise_on_status=False
        )
        session.mount("https://", HTTPAdapter(max_retries=retries))
        session.mount("http://", HTTPAdapter(max_retries=retries))

        try:
            # 2. Ajout d'un timeout (indispensable)
            # (timeout_connexion, timeout_lecture)
            # On laisse 150 secondes au modèle pour générer le JSON complet
            response = session.post(
                url, 
                json=payload, 
                headers=headers, 
                verify=False, 
                timeout=(20, 150) 
            )

            if response.status_code == 200:
                response_data = response.json()
                # Sécurisation de l'accès aux données
                choices = response_data.get("choices", [])
                if not choices:
                    return {"error": "No choices in response"}

                text = choices[0]["message"]["content"]

                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    print("Failed to parse JSON content, returning raw text.")
                    return text
            else:
                print(f"Error {response.status_code}: {response.text}")
                return None

        except requests.exceptions.ChunkedEncodingError as e:
            print(f"Connexion interrompue pendant la lecture du flux (IncompleteRead): {e}")
            return {"error": "stream_interrupted", "details": str(e)}
        except requests.exceptions.Timeout:
            print("Le serveur Mistral a mis trop de temps à répondre (Timeout).")
            return {"error": "timeout"}
        except Exception as e:
            print(f"Erreur inattendue : {e}")
            return None


    def mistral_request_secteur_obs(self, content):
        url = self.config.url_model_llm
        payload = {
            "messages": [
                {"content": self.prompt_solution, "role": "system"},
                {"content": content, "role": "user"}
            ],
            "model": self.config.model_llm,
            "temperature": 0.1,
            "response_format": {"type": "json_object"}
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.access_token}",
        }

        # 1. Configuration d'une session avec auto-retry
        # Cela permet de relancer la requête si la connexion est coupée brutalement
        session = requests.Session()
        retries = Retry(
            total=3,                # Nombre de tentatives
            backoff_factor=1,       # Attend 1s, 2s, 4s entre les essais
            status_forcelist=[502, 503, 504], # Retente si le serveur est surchargé
            raise_on_status=False
        )
        session.mount("https://", HTTPAdapter(max_retries=retries))
        session.mount("http://", HTTPAdapter(max_retries=retries))

        try:
            # 2. Ajout d'un timeout (indispensable)
            # (timeout_connexion, timeout_lecture)
            # On laisse 150 secondes au modèle pour générer le JSON complet
            response = session.post(
                url, 
                json=payload, 
                headers=headers, 
                verify=False, 
                timeout=(20, 150) 
            )

            if response.status_code == 200:
                response_data = response.json()
                # Sécurisation de l'accès aux données
                choices = response_data.get("choices", [])
                if not choices:
                    return {"error": "No choices in response"}

                text = choices[0]["message"]["content"]

                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    print("Failed to parse JSON content, returning raw text.")
                    return text
            else:
                print(f"Error {response.status_code}: {response.text}")
                return None

        except requests.exceptions.ChunkedEncodingError as e:
            print(f"Connexion interrompue pendant la lecture du flux (IncompleteRead): {e}")
            return {"error": "stream_interrupted", "details": str(e)}
        except requests.exceptions.Timeout:
            print("Le serveur Mistral a mis trop de temps à répondre (Timeout).")
            return {"error": "timeout"}
        except Exception as e:
            print(f"Erreur inattendue : {e}")
            return None

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