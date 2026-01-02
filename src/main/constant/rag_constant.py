# Paramètres du chunk

CHUNK_SIZE = 500
OVERLAP = 50

# Paramètres LLM
NUMBER_RESULTS = 100


SECTOR_QUERIES = {
    "title": "nom du secteur d’activité",
    "sub_sectors": "liste des sous-secteurs associés au secteur",
    "company_size": "taille des entreprises du secteur TPE PME ETI",
    "summary": "description des activités du secteur, typologies de sites et contraintes métiers",

    "emissions_profile": "répartition des postes d’émissions carbone du secteur (process, utilities, bâtiment, transport, déchets)",

    "challenges": "principaux enjeux et défis du secteur",
    "regulations": "réglementations applicables au secteur",
    "systems_matrix": "systèmes, solutions et leviers techniques du secteur",
    "sector_path": "parcours de décarbonation recommandé pour le secteur",
    "use_case": "cas d’usage concrets par sous-secteur avec résultats chiffrés",
    "resources": "ressources, études, documents de référence du secteur",
}
