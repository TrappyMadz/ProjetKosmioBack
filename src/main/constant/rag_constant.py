# Paramètres du chunk
CHUNK_SIZE = 2000
OVERLAP = 400

# Paramètres de retrieval
N_RESULTS_INITIAL = 50
N_RESULTS_RERANKED = 5



# ============================================================================ #
#  QUERIES SECTEUR — utilisées pour le retrieval vectoriel                      #
#  Les descriptions doivent cibler le CONTENU RÉEL du document, pas la TDM.     #
# ============================================================================ #

SECTOR_QUERIES_METADATA_SUMMARY = {
    "title": "plan de transition sectoriel, nom du secteur industriel étudié",
    "sub_sectors": "sous-secteurs industriels couverts, filières de production, variantes ou segments du secteur",
    "company_size": "taille des entreprises concernées, TPE PME ETI grands groupes industriels",
    "contributors": "entreprises participantes, partenaires industriels, organismes ayant contribué au rapport",
    "summary": "présentation du secteur industriel, description de la filière, activités principales, procédés de fabrication, volumes de production annuels en France",
}

SECTOR_QUERIES_FIRST_PART_A = {
    # --- Description & Émissions ---
    "description": "présentation détaillée du secteur industriel, description des activités principales, procédés de fabrication, volumes de production en France, positionnement international",
    "emissions_profile": "répartition des émissions de CO2 et gaz à effet de serre par poste : procédés industriels en pourcentage, consommation d'énergie utilities, bâtiments, transport logistique, déchets, bilan carbone de la filière",
}

SECTOR_QUERIES_FIRST_PART_B = {
    # --- Enjeux ---
    "challenges": "enjeux majeurs de la décarbonation du secteur, défis technologiques, contraintes économiques, compétitivité internationale, dépendance aux matières premières, transition énergétique, impact sur l'emploi",

    # --- Réglementations ---
    "regulations": "cadre réglementaire, système d'échange de quotas EU-ETS, SNBC stratégie nationale bas carbone, taxonomie européenne, CBAM mécanisme d'ajustement carbone aux frontières, directive sur les émissions industrielles",

    # --- Systèmes ---
    "systems_matrix": "technologies de décarbonation, solutions techniques identifiées, captage et stockage du CO2, efficacité énergétique, économie circulaire recyclage, substitution de combustibles, électrification des procédés, récupération de chaleur",
}

SECTOR_QUERIES_LAST_PART = {
    # --- Parcours sectoriel ---
    "sector_path": "feuille de route de décarbonation, actions à court terme quick wins, optimisations à moyen terme, investissements structurants, changement de combustible, jalons de réduction des émissions à 2030 et 2050",

    # --- Cas d'usage ---
    "use_case": "exemples concrets de mise en œuvre, projets pilotes, sites industriels ayant déployé des solutions de décarbonation, résultats chiffrés de réduction d'émissions, retours d'expérience",

    # --- Ressources ---
    "resources": "documents de référence, rapports techniques, guides méthodologiques, publications scientifiques, liens URL vers les ressources en ligne",
}


# ============================================================================ #
#  QUERIES SOLUTION — utilisées pour le retrieval vectoriel                     #
# ============================================================================ #

SOLUTION_QUERIES_METADATA_SUMMARY = {
    # --- Identité ---
    "title": "nom de la solution technique, intitulé de la technologie ou du procédé",
    "category": "catégorie de la solution : efficacité énergétique, récupération de chaleur, énergies renouvelables, captage CO2, économie circulaire",
    "system": "système technique concerné : chaudière, four, échangeur, compresseur, réseau de chaleur, procédé industriel",
    "type": "nature de la solution : technique, organisationnelle ou comportementale",
    "maturity": "niveau de maturité technologique TRL, solution éprouvée, en développement ou émergente",
    "cost_scale": "ordre de grandeur du coût d'investissement, échelle de coût faible moyen élevé",
    "complexity": "complexité de mise en œuvre, facilité d'intégration, durée du déploiement",
    "contributors": "entreprises ou organismes ayant contribué à la rédaction de la fiche, partenaires industriels",

    # --- Résumé ---
    "summary": "description générale de la solution, principe de fonctionnement en quelques phrases, bénéfices principaux pour la réduction des émissions",
}

SOLUTION_QUERIES_FIRST_PART = {
    # --- Contexte ---
    "context_objective": "objectif principal de la solution en termes de réduction d'émissions ou d'économie d'énergie",
    "context_target_sites": "types de sites industriels concernés par la solution, secteurs d'application, logements collectifs, tertiaire",
    "context_scope_includes": "périmètre couvert par la solution, éléments inclus dans le champ d'application",
    "context_scope_excludes": "éléments hors périmètre, cas non couverts par la solution",
    "context_prerequisites": "prérequis techniques réglementaires ou organisationnels nécessaires à la mise en œuvre",

    # --- Mécanisme ---
    "mechanism_description": "principe de fonctionnement détaillé de la solution, processus technique, réactions chimiques ou physiques impliquées",
    "mechanism_variants": "variantes technologiques disponibles, déclinaisons possibles de la solution, options de dimensionnement",

    # --- Applicabilité ---
    "applicability_conditions": "conditions dans lesquelles la solution est pertinente et efficace, critères de faisabilité",
    "applicability_avoid_if": "situations où la solution est déconseillée, contre-indications techniques ou économiques",
    "applicability_constraints": "contraintes techniques, réglementaires ou opérationnelles liées à l'utilisation de la solution",

    # --- Impacts ---
    "impact_energy": "gains énergétiques, économies d'énergie en kWh ou pourcentage, réduction de la consommation",
    "impact_co2": "réduction des émissions de CO2 en tonnes par an ou en pourcentage, potentiel de décarbonation",
    "impact_capex": "coût d'investissement CAPEX en euros, fourchette de prix, exemples chiffrés",
    "impact_opex": "coûts d'exploitation OPEX, économies opérationnelles, coûts de maintenance",
    "impact_roi": "retour sur investissement, temps de retour en années, rentabilité économique",
    "impact_co_benefits": "co-bénéfices de la solution : amélioration du confort, qualité de l'air, réduction du bruit, création d'emplois",

    # --- Leviers ---
    "levers": "leviers d'action pour maximiser l'impact de la solution, facteurs clés de succès, bonnes pratiques",
}

SOLUTION_QUERIES_LAST_PART = {
    # --- Mise en œuvre ---
    "implementation_path": "étapes de mise en œuvre : diagnostic initial audit énergétique, dimensionnement et étude de faisabilité, installation et déploiement, suivi et mesure des performances",

    # --- Risques ---
    "risks": "risques techniques ou économiques associés à la solution, points de vigilance, obstacles potentiels",

    # --- Exemples ---
    "exemples": "cas d'usage réels, retours d'expérience sectoriels, entreprises ayant déployé la solution avec résultats chiffrés",

    # --- Ressources ---
    "resources": "documents de référence, guides techniques, liens vers les publications et fiches projets associées"
}
