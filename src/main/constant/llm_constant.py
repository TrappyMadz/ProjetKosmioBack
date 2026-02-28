# --- Constantes pour les LLM ---
LLM_TEMPERATURE = 0.1

# --- Prompt principal ---
PROMPT_HEADER = """
Tu es un modele d'extraction et de synthese d'information specialise dans les rapports techniques de transition industrielle et de decarbonation.

A partir du contexte fourni (extraits d'un document PDF), tu dois extraire et reformuler les informations demandees de maniere structuree et complete.

# REGLES IMPERATIVES
1. IGNORE completement les passages suivants s'ils apparaissent dans le contexte :
   - Tables des matieres, sommaires, index de figures ou de tableaux
   - Mentions legales, pages de copyright, informations sur l'editeur
   - Numeros de page, en-tetes et pieds de page recurrents
   - Legendes de figures ou tableaux sans contenu descriptif
2. PRIVILEGIE les informations substantielles :
   - Donnees chiffrees (pourcentages, tonnes de CO2, couts en euros)
   - Noms de technologies et procedes industriels
   - Descriptions de mecanismes techniques
   - Reglementations et normes citees
3. SYNTHETISE les informations provenant de plusieurs passages dans un meme champ si elles sont complementaires.
4. Si une information n'est PAS trouvee dans le contexte fourni, laisse la valeur de la cle vide (chaine vide "" ou liste vide []).
5. Formule des phrases claires, completes et factuelles en francais.
6. Chaque annotation [Source: fichier, Page: N] dans le contexte indique l'origine du texte - utilise cela pour croiser les informations.

# Format de reponse
Tu dois renvoyer un JSON valide conforme au schema fourni.

Extrait les informations cles suivantes :
"""

# ============================================================================ #
#  PROMPTS SOLUTION                                                            #
# ============================================================================ #

PROMPT_SOLUTION_TITLE_METADATA_SUMMARY = PROMPT_HEADER + """
- title : Un titre clair et descriptif qui identifie la solution technique (forme nominale ou verbale)
- metadata : un dictionnaire de 8 entrees :
    - category : La categorie generale de la solution (ex: "Efficacite energetique", "Recuperation de chaleur", "Energies renouvelables")
    - system : Le systeme technique ou equipement principal concerne (ex: "Chaudiere", "Four industriel", "Reseau de chaleur")
    - type : Le type de la solution parmi : "technique", "organisationnelle" ou "comportementale"
    - maturity : Le niveau de maturite technologique si mentionne (ex: "Mature", "En developpement", "Emergente"), sinon vide
    - cost_scale : L'ordre de grandeur du cout si mentionne (ex: "Faible", "Modere", "Eleve"), sinon vide
    - complexity : Le niveau de complexite de mise en oeuvre (ex: "Simple", "Moderee", "Complexe")
    - last_update : vide
    - contributors : Liste des noms des entreprises, organismes ou personnes ayant contribue a cette fiche
- summary : Un resume de 2-3 phrases decrivant le principe de la solution et ses benefices principaux en termes de reduction d'emissions ou d'economie d'energie
"""

PROMPT_SOLUTION_CONTENT_FIRSTPART = PROMPT_HEADER + """
- contexte : un dictionnaire de 5 entrees :
    - objective : L'objectif principal de la solution en une phrase claire et precise
    - target_sites : Liste des types de sites industriels ou batiments concernes (ex: ["sites industriels lourds", "logements collectifs", "tertiaire"])
    - scope_includes : Liste des elements et perimetres inclus dans la solution
    - scope_excludes : Liste des elements explicitement exclus du perimetre
    - prerequisites : Liste des prerequis reglementaires, techniques ou organisationnels, chacun detaille en une phrase
- mecanism : un dictionnaire a 2 entrees :
    - description : Description du principe de fonctionnement en 3-4 phrases techniques mais accessibles
    - variants : Liste des variantes ou declinaisons possibles, chacune decrite en une phrase
- applicability : un dictionnaire a 3 entrees :
    - conditions : Liste des cas ou la solution est pertinente, chacun en une phrase
    - avoid_if : Liste des cas ou la solution est deconseillee, chacun en une phrase
    - constraints : Liste des contraintes techniques ou operationnelles sous forme de groupes nominaux
- impacts : un dictionnaire de 4 entrees :
    - energy : Estimation des economies d'energie avec des chiffres si disponibles (kWh, pourcentage de reduction)
    - co2 : Reduction des emissions de CO2 avec des chiffres si disponibles (tonnes/an, pourcentage)
    - costs : un dictionnaire a 3 entrees :
        - capex : Detail des couts d'investissement avec des chiffres (en euros ou euros/unite)
        - opex : Detail des couts d'exploitation et des economies operationnelles avec des chiffres
        - roi : Retour sur investissement (temps de retour en annees, TRI si mentionne)
    - co_benefits : Liste des co-benefices (ex: ["amelioration du confort thermique", "reduction du bruit", "qualite de l'air"])
- levers : Liste des leviers d'action concrets pour maximiser l'efficacite de la solution, chacun en une phrase
"""

PROMPT_SOLUTION_CONTENT_LASTPART = PROMPT_HEADER + """
- implementation_path : une liste avec un dictionnaire pour chaque step :
    - step : "Diagnostic initial", "Dimensionnement", "Installation", "Suivi"
    - details : les details de la demarche a suivre pour cette etape en quelques phrases
- risks : une liste de risques sous forme de dictionnaires :
    - risk : description du risque technique, economique ou operationnel en une phrase
    - mitigation : mesure d'attenuation ou de prevention du risque, sinon vide
- examples : une liste de dictionnaire de cas d'usage de la forme :
    - secteur : secteur du cas d'usage sous forme de groupe nominal
    - resume : explication de l'utilisation en 1-2 phrases
    - link : vide
- resources : Liste des ressources documentaires sous forme de dictionnaires :
    - title : Titre du document ou de la ressource
    - type : Type de ressource (ex: "PDF", "Site web", "Guide technique", "Rapport")
    - link : URL de la ressource si mentionnee, sinon vide
"""


# ============================================================================ #
#  PROMPTS SECTEUR                                                             #
# ============================================================================ #

PROMPT_SECTEUR_TITLE_METADATA_SUMMARY = PROMPT_HEADER + """
- type : "sector"
- id : vide
- title : Le titre de la fiche qui correspond au nom du secteur
- metadata : Un dictionnaire contenant 4 entrees :
    - sub_sectors : Liste des sous-secteurs industriels couverts par le rapport
    - company_size : Les types d'entreprises concernees (ex: "TPE, PME ou ETI" ou "Grands groupes industriels")
    - last_update : vide
    - contributors : Liste des organismes et entreprises ayant contribue a cette publication
- summary : Resume de 3-4 phrases decrivant le secteur (activites principales, volumes de production, nombre de sites, procedes de fabrication principaux, enjeux de decarbonation). NE PAS resumer les mentions legales ou informations editoriales.
"""

PROMPT_SECTEUR_CONTENT_FIRSTPART_A = PROMPT_HEADER + """
- description : Description detaillee du secteur en 4-6 phrases couvrant les activites principales, les procedes de fabrication, les volumes de production en France et le positionnement international.
- emissions_profile : une liste contenant un dictionnaire avec 5 entrees qui definissent la repartition des postes d'emissions. ATTENTION : renseigne UNIQUEMENT les pourcentages EXPLICITEMENT mentionnes dans le contexte. Si le contexte ne donne pas de repartition par poste, laisse les valeurs vides ("") :
    - process : en pourcentage si mentionne, sinon ""
    - utilities : en pourcentage si mentionne, sinon ""
    - building : en pourcentage si mentionne, sinon ""
    - transport : en pourcentage si mentionne, sinon ""
    - waste : en pourcentage si mentionne, sinon ""
"""

PROMPT_SECTEUR_CONTENT_FIRSTPART_B = PROMPT_HEADER + """
- contexte : la liste de dictionnaire des enjeux DISTINCTS du secteur. Chaque enjeu doit couvrir un theme DIFFERENT (environnemental, economique, social, technique). NE PAS repeter le meme enjeu reformule. Forme :
    - title : le titre court et specifique de l'enjeu
    - description : la description de l'enjeu en 2-3 phrases avec des donnees chiffrees si disponibles
- regulations : la liste des reglementations NOMMEES dans le contexte (ex: SNBC, EU-ETS, MACF, loi AGEC). Ne pas inventer de reglementations.
- systems_matrix : la liste des systemes et solutions cles sous la forme de dictionnaire :
    - system : nom du systeme ou domaine technique
    - impact : impact sous la forme d'une echelle (Faible, Moyen, Fort)
    - priority : priorite sous forme d'une echelle de 1 a 5,
    - solutions : liste des solutions techniques concretes mentionnees dans le contexte
"""

PROMPT_SECTEUR_CONTENT_LASTPART = PROMPT_HEADER + """
- sector_path : Parcours de decarbonation sectoriel sous forme d'une liste ordonnee de dictionnaires. Extrais les phases telles qu'elles sont NOMMEES dans le document. N'invente PAS de noms de phases generiques.
    Chaque entree doit contenir :
    - phase : Nom de la phase tel qu'il apparait dans le document source
    - action : Description des actions recommandees pour cette phase en 1-2 phrases
- use_case : Liste de cas d'usage concrets par sous-secteur :
    - sub_sector : Nom du sous-secteur concerne
    - actions : Description precise des actions ou technologies mises en oeuvre
    - results : Resultats obtenus avec des chiffres EXTRAITS du contexte. Si pas de chiffres, ecrire "Non chiffre dans le document".
    - link : vide
- resources : Liste des DOCUMENTS et RAPPORTS de reference nommes dans le contexte. NE PAS inclure de donnees brutes de tableaux techniques.
    - title : Titre clair et complet du document
    - type : Type (ex: "PDF", "Rapport", "Site web", "Base de donnees", "Etude")
    - link : URL si mentionnee dans le texte, sinon vide
"""