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


SOLUTION_QUERIES = {
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

    # --- Mise en œuvre ---
    "implementation_diagnostic": "diagnostic initial pour la mise en œuvre de la solution",
    "implementation_dimensioning": "dimensionnement de la solution",
    "implementation_installation": "installation ou déploiement de la solution",
    "implementation_monitoring": "suivi et pilotage après installation",

    # --- Risques ---
    "risks": "risques associés à la solution et mesures de mitigation",

    # --- Exemples ---
    "examples": "cas d’usage sectoriels de la solution",

    # --- Ressources ---
    "resources": "ressources documentaires sur la solution"
}

