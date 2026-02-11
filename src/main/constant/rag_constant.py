# Paramètres du chunk

CHUNK_SIZE = 500
OVERLAP = 50

# Paramètres LLM
N_RESULTS = 4

SECTOR_QUERIES_METADATA_SUMMARY = {
    "title": "le titre de la fiche qui correspond au nom du secteur",
    "sub_sectors": "liste des sous-secteurs associés au secteur",
    "company_size": "type d'entreprise sous la forme TPE, PME ou ETI",
    "contributors": "liste des entreprises ayant contribué à cette publication",
    "summary": "résumé des activités, typologies de sites, contraintes métiers",
}

SECTOR_QUERIES_FIRST_PART = {
    # --- Émissions ---
    "emissions_profile": "répartition des postes d'émissions : process, utilities, building, transport, waste en pourcentage ou ordre de grandeur",

    # --- Enjeux ---
    "challenges": "liste des enjeux avec le titre et la description de chaque enjeu",

    # --- Réglementations ---
    "regulations": "liste des réglementations importantes à prendre en compte",

    # --- Systèmes ---
    "systems_matrix": "liste des systèmes et solutions clés avec le nom du système, l'impact (Faible, Moyen, Fort), la priorité (échelle de 1 à 5) et la liste des solutions",
}

SECTOR_QUERIES_LAST_PART = {
    # --- Parcours sectoriel ---
    "sector_path": "parcours sectoriel recommandé avec les phases (Quick wins, Optimisations, Investissements structurants, Nouvelles énergies, Management & pilotage) et les actions associées à chaque phase",

    # --- Cas d'usage ---
    "use_case": "liste des actions à réaliser par sous-secteur avec le sous-secteur concerné, les actions à effectuer, les résultats chiffrés et le lien vers la fiche projet",

    # --- Ressources ---
    "resources": "liste des ressources documentaires avec le titre, le type et le lien de chaque ressource",
}



SOLUTION_QUERIES_METADATA_SUMMARY = {
    # --- Identité ---
    "title": "nom de la solution",
    "category": "catégorie de la solution",
    "system": "système technique utilisé par la solution",
    "type": "type de solution technique organisationnelle ou comportementale",
    "maturity": "niveau de maturité de la solution",
    "cost_scale": "échelle de coût de la solution",
    "complexity": "complexité de mise en œuvre de la solution",
    "contributors": "entreprises ou acteurs ayant contribué à la solution",

    # --- Résumé ---
    "summary": "résumé et description générale de la solution",
}


SOLUTION_QUERIES_FIRST_PART = {
    # --- Contexte ---
    "context_objective": "objectif principal de la solution",
    "context_target_sites": "types de sites concernés par la solution",
    "context_scope_includes": "éléments inclus dans le périmètre de la solution",
    "context_scope_excludes": "éléments exclus du périmètre de la solution",
    "context_prerequisites": "prérequis réglementaires techniques ou organisationnels",

    # --- Mécanisme ---
    "mechanism_description": "principe de fonctionnement de la solution",
    "mechanism_variants": "variantes ou déclinaisons possibles de la solution",

    # --- Applicabilité ---
    "applicability_conditions": "conditions d’usage pertinentes de la solution",
    "applicability_avoid_if": "cas où la solution est déconseillée",
    "applicability_constraints": "contraintes liées à l’utilisation de la solution",

    # --- Impacts ---
    "impact_energy": "économies ou valorisation d’énergie liées à la solution",
    "impact_co2": "réduction ou évitement des émissions de CO2",
    "impact_capex": "coûts d’investissement CAPEX de la solution",
    "impact_opex": "coûts d’exploitation OPEX de la solution",
    "impact_roi": "retour sur investissement de la solution",
    "impact_co_benefits": "bénéfices indirects ou co-bénéfices",

    # --- Leviers ---
    "levers": "leviers techniques ou organisationnels associés à la solution",
 }
 

SOLUTION_QUERIES_LAST_PART = {
    # --- Mise en œuvre ---
    "implementation_path": "liste des étapes de mise en œuvre : Diagnostic initial, Dimensionnement, Installation, Suivi avec les détails pour chaque étape",

    # --- Risques ---
    "risks": "liste des risques associés à la solution",

    # --- Exemples ---
    "exemples": "liste des cas d'usage sectoriels avec le secteur, un résumé de l'utilisation et le lien vers la fiche secteur",

    # --- Ressources ---
    "resources": "liste des ressources documentaires avec le titre, le type et le lien de chaque ressource"
}

