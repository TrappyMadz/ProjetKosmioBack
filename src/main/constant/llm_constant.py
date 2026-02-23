# --- Constantes pour les LLM ---
LLM_TEMPERATURE = 0.1

# --- Prompts pour l'extraction d'information ---
PROMPT_HEADER = """
        Tu est un modèle d’extraction d’information.
        Tu dois uniquement que extraire les mots clés.
        Si une information n'est pas trouvée, laisser la valeur de la clé vide.
        Tu dois formuler des phrases claires en français qui serviront dans un document récapitulatif.
            
        # Format de réponse
        Tu dois renvoyer un JSON valide.
            
        Extrait les informations clés suivantes :
        """

# --- Prompts pour les solutions ---

PROMPT_SOLUTION_TITLE_METADATA_SUMMARY = PROMPT_HEADER + """
        - title : Un titre en forme nominale ou verbale qui illustre la solution sous forme de string
        - metadata : un dictionnaire de 8 entrées :
            - category : La catégorie dans laquelle pourrait ce placer la solution en un groupe nominal
            - system : Le système dans la catégorie proposée sous la forme d'un groupe nominal
            - type : technique, organisationnelle ou comportentale suivant le type de solution en un mot
            - maturity : vide
            - cost_scale : a quel point la solution est couteuse à mettre en place en un mot
            - complexity : a quel point la solution est compliquée à mettre en place en un mot
            - last_update : la date d'aujourd'hui sous forme de string jj-mm-aaa
            - contributors : une liste des contributeurs de cette fiche, nom de personne ou d'entreprise
        - summary : définition rapide de la solution sous forme d'une ou deux phrases et qui en donne les bénéfices principaux
        """

PROMPT_SOLUTION_CONTENT_FIRSTPART = PROMPT_HEADER + """
            - context : un dictionnaire de 5 entrées :
                - objective : le but final de la solution en une phrase
                - target_sites : une liste des types de sites concernés (exemple : logements collectifs, tertiaire, sites industriels)
                - scope_includes : une liste d'éléments inclues !!!
                - scope_excludes : une liste d'éléments exclues !!!
                - prerequisites : une liste de prérecis réglementaires, techniques ou organisationnels chaqu'un détaillé un
            - mecanism : un dictionnaire à 2 entrées :
                - description : Description simple du principe de fonctionnement en 3-4 phrases
                - variants : Une liste des diffèrentes variantes possible au niveau du fonctionnement en une phrase chaqu'une
              - applicability : un dictionnaire à 3 entrées :
                - conditions : une liste des cas où l'usage où la solution semble pertient en une phrase
                - avoid_if : une liste des cas où l'usage où la solution est a éviter en une phrase
                - contraints : une liste des contraintes apportées par la solution sous forme de groupes nominaux
            - impacts : un dictionnaire de 4 entrées :
                - energy : estimation qualitative ou valeur de l'énergie dépensée par la mise en place de la solution en une phrase
                - co2 : ordre de grandeur ou fourchette du co2 produit par la mise en place de la solution
                - costs : un dictionnaire à 2 entrées :
                - capex : dépenses d'investissement capex en détaille de quelques phrases avec des chiffres
                - opex : dépenses d'exploitation opex en détaille de quelques phrases avec des chiffres
                - roi : retour sur invertissement de la solution en quelques phrases
                - co_benefits : une liste des bénéfices autres qu'amène la solution sous forme de groupes nominaux (exemple: amélioration du confort)
            - levers : une liste des actions concrètes ou facteurs clés sur lesquels on peut agir pour faire fonctionner la solution ou en amplifier l’impact sous forme de phrase
            """

PROMPT_SOLUTION_CONTENT_LASTPART = PROMPT_HEADER + """
        - implementation_path : une liste avec un distionnaire pour chaque step : 
            - step : "Diagnostic initial", "Dimensionnement", "Installation", "Suivi"
            - details : les détails de la démarche à suivre pour cette étape en quelques phrases
        - risks : une liste de risques que pourraient apporter la solution sous forme de phrase ou groupe nominal
        - exemples : une liste de dictionnaire de cas d'usage de la forme :
            - secteur : secteur du cas d'usage sous forme de groupe nominal
            - resume : explication de l'utilisée en 1-2 phrases
            - link : vide
        - resources : une liste de dictionnaire de ressource de la forme :
            - title : titre de la resource sous forme de groupe nominal
            - type : type de resource (exemple : site web, pdf)
            - link : lien de la resource uniquement sous la forme d'un URL
        """


# --- Prompts pour les fiches secteurs ---
PROMPT_SECTEUR_TITLE_METADATA_SUMMARY = PROMPT_HEADER + """
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

PROMPT_SECTEUR_CONTENT_FIRSTPART = PROMPT_HEADER + """
        
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

PROMPT_SECTEUR_CONTENT_LASTPART = PROMPT_HEADER + """
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