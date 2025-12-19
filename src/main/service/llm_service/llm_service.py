import requests


class LlmService():
    prompt_solution = "Tu est un modèle d’extraction d’information. Extrait les informations clés suivantes :\n\n- type : \"solution\"\n- id : vide\n- title : Le titre de la solution\n- metadata : un dictionnaire de 8 entrées :\n  - category : La catégorie de la solution\n  - system : Le système utilisé\n  - type : technique, organisationnelle ou comportentale suivant le type de solution\n  - maturity : \n  - cost_scale : trouver une échelle\n  - complexity : à quel point la solution est compliquée à mettre en place\n  - last_update : vide\n  - contributors : liste des entreprises qui ont contribué à la fiche\n- summary : un résumé de la solution\n- content : un dictionnaire de 9 entrées :\n  - context : un dictionnaire de 5 entrées :\n    - objective : l'objectif global de la solution\n    - target_sites : une liste des types de sites concernés (exemple : logements collectifs, tertiaire)\n    - scope_includes : une liste d'éléments inclus\n    - scope_excludes : une liste d'éléments exclus\n    - prerequisites : une liste de prérequis réglementaires, techniques ou organisationnels\n  - mecanism : un dictionnaire à 2 entrées :\n    - description : description simple du principe de fonctionnement\n    - variants : une liste des différentes variantes possibles\n  - applicability : un dictionnaire à 3 entrées :\n    - conditions : une liste des cas où l'usage de la solution est pertinent\n    - avoid_if : une liste des cas où l'usage est à éviter\n    - constraints : contraintes identifiées\n  - impacts : un dictionnaire de 4 entrées :\n    - energy : estimation qualitative ou valeur de l'énergie économisée ou valorisée\n    - co2 : ordre de grandeur ou fourchette du CO2 évité\n    - costs : un dictionnaire à 3 entrées :\n      - capex : dépenses d'investissement CAPEX avec chiffres\n      - opex : dépenses d'exploitation OPEX avec chiffres\n      - roi : retour sur investissement avec chiffres\n    - co_benefits : une liste des bénéfices apportés par la solution\n  - levers : une liste de leviers associés à la solution\n  - implementation_path : une liste de dictionnaires :\n    - step : Diagnostic initial, Dimensionnement, Installation, Suivi\n    - details : détails pour chaque étape\n  - risks : une liste de dictionnaires :\n    - risk : nom du risque\n    - mitigation : mesures de mitigation\n  - examples : une liste de dictionnaires de cas d'usage :\n    - secteur : secteur d'usage\n    - resume : explication de l'utilisation\n    - link : lien vers la fiche secteur\n  - resources : une liste de dictionnaires de ressources :\n    - title : titre de la ressource\n    - type : type de ressource\n    - link : lien de la ressource\n- contribution : un dictionnaire de 3 entrées :\n  - validation : vide\n  - history : liste vide\n  - improvement_proposal_link : vide\n- traceability : un dictionnaire de 3 entrées :\n  - source_pdf : vide\n  - extraction_confidence : vide\n  - chunks_used : liste vide\n\n# Directives\n- Les informations doivent uniquement provenir du texte fourni.\n- Si une information n'est pas trouvée, laisser la valeur de la clé vide.\n\n# Format de réponse\nTu dois renvoyer un JSON valide."
    prompt_secteur = "Tu est un modèle d’extraction d’information. Extrait les informations clés suivantes :\n\n- type : \"secteur\"\n- id : vide # à implémenter après le passage de l'IA\n- title : Le titre de la fiche qui correspond au nom du secteur\n- metadata : Un dictionnaire contenant 4 entrées :\n  - sub_sectors : Une liste des sous secteurs associés,\n  - company_size : le type d’entreprise sous la forme TPE, PME ou ETI,\n  - last_update : vide\n  - contributors : une listes des entreprises ayant contribués à cette publication\n- summary : résumé des activités, typologies de sites, contraintes métiers\n- content : un dictionnaire contenant 7 entrées :\n  - emissions_profile : un dictionnaire contenant 5 entrées qui définissent la répartition des postes d'émissions :\n    - process : en pourcentage ou ordre de grandeur,\n    - utilities : en pourcentage ou ordre de grandeur,\n    - building : en pourcentage,\n    - transport : en pourcentage,\n    - waste : en pourcentage\n  - challenges : la liste de dictionnaire des enjeux sous la forme :\n    - title : le titre de l'enjeu,\n    - description : la description de l’enjeu\n  - regulations : la liste des réglementations importantes à prendre en compte,\n  - systems_matrix : la liste des systèmes et solutions clés sous la forme de dictionnaire :\n    - system : nom de la solution\n    - impact : impact sous la forme d’une échelle (Faible, Moyen, Fort)\n    - priority : priorité sous forme d’une échelle de 1 à 5 ⭐,\n    - solutions : liste des solutions\n  - sector_path : parcours sectoriel recommandé sous forme d’une liste de dictionnaire qui décrit les actions à faire durant 5 phases (Quick wins (< 3 mois), Optimisations (3–12 mois), Investissements structurants, Nouvelles énergies / changement de combustible, Management & pilotage) :\n    - phase : nom de la phase\n    - action : l’action associée à cette phase\n  - use_case : une liste de dictionnaire d’action à réaliser par sous secteurs :\n    - sub_sector : le sous secteur concerné\n    - action : une liste des actions à effectuer\n    - results : une liste des résultats avec des chiffres\n    - link : le lien vers la fiche projet associée\n  - resources : une liste de dictionnaire contenant les ressources utilisées sous la forme :\n    - title : titre de la ressource\n    - type : type de la ressource\n    - link : lien de la ressource\n- contribution : dictionnaire contenant 4 entrées :\n  - completeness : le niveau de complétude de la fiche dans son ensemble (squelette, partielle, complète)\n  - validator : vide\n  - history : une liste vide\n  - improvement_proposal_link : vide\n- traceability : un dictionnaire de 3 entrées :\n  - source_pdf : vide\n  - extraction_confidence : vide\n  - chunks_used : liste vide\n\n# Directives\n- Les informations doivent uniquement venir du texte que je te donne.\n- Si tu ne trouves pas une information, laisse la valeur de la clé vide.\n\n# Format de réponse\nTu dois renvoyer un .json"

    def __init__(self, config):
        self.config = config

    # requetes mistral
    # Prend en entrée le texte (prompt déjà inclue) et print la réponse pour l'instant
    def mistral_request_solution(self, content):
        url = self.config.url_model_llm
        payload = {
            "max_tokens": 512,
            "messages": [
                {
                    "content" : self.prompt_solution,
                    "role" : "system"
                },
                {
                    "content": content,
                    "role": "user"
                }
            ],
            "model": self.config.model_llm,
            "temperature": 1,
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "solution_sheet",
                    "schema": {
                        "type": "object",
                        "required": [
                        "type",
                        "id",
                        "title",
                        "metadata",
                        "summary",
                        "content",
                        "contribution",
                        "traceability"
                        ],
                        "properties": {
                            "type": { "type": "string" },
                            "id": { "type": "string" },
                            "title": { "type": "string" },

                            "metadata": {
                                "type": "object",
                                "required": [
                                "category",
                                "system",
                                "type",
                                "maturity",
                                "cost_scale",
                                "complexity",
                                "last_update",
                                "contributors"
                                ],
                                "properties": {
                                    "category": { "type": "string" },
                                    "system": { "type": "string" },
                                    "type": { "type": "string" },
                                    "maturity": { "type": "string" },
                                    "cost_scale": { "type": "string" },
                                    "complexity": { "type": "string" },
                                    "last_update": { "type": "string" },
                                    "contributors": {
                                        "type": "array",
                                        "items": { "type": "string" }
                                    }
                                }
                            },

                            "summary": { "type": "string" },

                            "content": {
                                "type": "object",
                                "required": [
                                "context",
                                "mecanism",
                                "applicability",
                                "impacts",
                                "levers",
                                "implementation_path",
                                "risks",
                                "examples",
                                "resources"
                                ],
                                "properties": {

                                "context": {
                                    "type": "object",
                                    "required": [
                                    "objective",
                                    "target_sites",
                                    "scope_includes",
                                    "scope_excludes",
                                    "prerequisites"
                                    ],
                                    "properties": {
                                    "objective": { "type": "string" },
                                    "target_sites": { "type": "array", "items": { "type": "string" } },
                                    "scope_includes": { "type": "array", "items": { "type": "string" } },
                                    "scope_excludes": { "type": "array", "items": { "type": "string" } },
                                    "prerequisites": { "type": "array", "items": { "type": "string" } }
                                    }
                                },

                                "mecanism": {
                                    "type": "object",
                                    "required": ["description", "variants"],
                                    "properties": {
                                    "description": { "type": "string" },
                                    "variants": { "type": "array", "items": { "type": "string" } }
                                    }
                                },

                                "applicability": {
                                    "type": "object",
                                    "required": ["conditions", "avoid_if"],
                                    "properties": {
                                    "conditions": { "type": "array", "items": { "type": "string" } },
                                    "avoid_if": { "type": "array", "items": { "type": "string" } }
                                    }
                                },

                                "impacts": {
                                    "type": "object",
                                    "required": ["energy", "co2", "costs", "co_benefits"],
                                    "properties": {
                                    "energy": { "type": "string" },
                                    "co2": { "type": "string" },
                                    "costs": {
                                        "type": "object",
                                        "required": ["capex", "opex"],
                                        "properties": {
                                        "capex": { "type": "string" },
                                        "opex": { "type": "string" }
                                        }
                                    },
                                    "co_benefits": { "type": "array", "items": { "type": "string" } }
                                    }
                                },

                                "levers": { "type": "array", "items": { "type": "string" } },

                                "implementation_path": {
                                    "type": "array",
                                    "items": {
                                    "type": "object",
                                    "required": ["step", "details"],
                                    "properties": {
                                        "step": { "type": "string" },
                                        "details": { "type": "string" }
                                    }
                                    }
                                },

                                "risks": {
                                    "type": "array",
                                    "items": {
                                    "type": "object",
                                    "required": ["risk"],
                                    "properties": {
                                        "risk": { "type": "string" }
                                    }
                                    }
                                },

                                "examples": {
                                    "type": "array",
                                    "items": {
                                    "type": "object",
                                    "required": ["secteur", "resume", "link"],
                                    "properties": {
                                        "secteur": { "type": "string" },
                                        "resume": { "type": "string" },
                                        "link": { "type": "string" }
                                    }
                                    }
                                },

                                "resources": {
                                    "type": "array",
                                    "items": {
                                    "type": "object",
                                    "required": ["title", "type", "link"],
                                    "properties": {
                                        "title": { "type": "string" },
                                        "type": { "type": "string" },
                                        "link": { "type": "string" }
                                    }
                                    }
                                }
                                }
                            },

                            "contribution": {
                                "type": "object",
                                "required": ["validation", "history", "improvement_proposal_link"],
                                "properties": {
                                "validation": { "type": "string" },
                                "history": { "type": "array", "items": { "type": "string" } },
                                "improvement_proposal_link": { "type": "string" }
                                }
                            },

                            "traceability": {
                                "type": "object",
                                "required": ["source_pdf", "extraction_confidence", "chunks_used"],
                                "properties": {
                                "source_pdf": { "type": "string" },
                                "extraction_confidence": { "type": "string" },
                                "chunks_used": { "type": "array", "items": { "type": "string" } }
                                }
                            }
                        }
                    }
                }
            }
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


    def mistral_request_secteur(self, content):
        url = self.config.url_model_llm
        payload = {
            "max_tokens": 512,
            "messages": [
                {
                    "content" : self.prompt_secteur,
                    "role" : "system"
                },
                {
                    "content": content,
                    "role": "user"
                }
            ],
            "model": self.config.model_llm,
            "temperature": 0,
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "secteur_sheet",
                    "schema": {
                        "type": "object",
                        "required": [
                            "type",
                            "id",
                            "title",
                            "metadata",
                            "summary",
                            "content",
                            "contribution",
                            "traceability"
                        ],
                        "properties": {
                            "type": {
                            "type": "string",
                            "const": "secteur"
                            },
                            "id": {
                            "type": ["string", "null"]
                            },
                            "title": {
                            "type": "string"
                            },
                            "metadata": {
                            "type": "object",
                            "required": [
                                "sub_sectors",
                                "company_size",
                                "last_update",
                                "contributors"
                            ],
                            "properties": {
                                "sub_sectors": {
                                "type": "array",
                                "items": { "type": "string" }
                                },
                                "company_size": {
                                "type": "string",
                                "enum": ["TPE", "PME", "ETI", "PME / ETI", ""]
                                },
                                "last_update": {
                                "type": ["string", "null"]
                                },
                                "contributors": {
                                "type": "array",
                                "items": { "type": "string" }
                                }
                            }
                            },
                            "summary": {
                            "type": "string"
                            },
                            "content": {
                            "type": "object",
                            "required": [
                                "emissions_profile",
                                "challenges",
                                "regulations",
                                "systems_matrix",
                                "sector_path",
                                "use_cases",
                                "resources"
                            ],
                            "properties": {
                                "emissions_profile": {
                                "type": "object",
                                "required": [
                                    "process",
                                    "utilities",
                                    "building",
                                    "transport",
                                    "waste"
                                ],
                                "properties": {
                                    "process": { "type": "string" },
                                    "utilities": { "type": "string" },
                                    "building": { "type": "string" },
                                    "transport": { "type": "string" },
                                    "waste": { "type": "string" }
                                }
                                },
                                "challenges": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "required": ["title", "description"],
                                    "properties": {
                                    "title": { "type": "string" },
                                    "description": { "type": "string" }
                                    }
                                },
                                "regulations": {
                                "type": "array",
                                "items": { "type": "string" }
                                },
                                "systems_matrix": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "required": ["system", "impact", "priority", "solutions"],
                                    "properties": {
                                    "system": { "type": "string" },
                                    "impact": {
                                        "type": "string",
                                        "enum": ["Faible", "Moyen", "Fort", "Moyen à Fort", "Très Fort", ""]
                                    },
                                    "priority": {
                                        "type": "string",
                                        "pattern": "^⭐{1,5}$"
                                    },
                                    "solutions": {
                                        "type": "array",
                                        "items": { "type": "string" }
                                    }
                                    }
                                }
                                },
                                "sector_path": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "required": ["phase", "action"],
                                    "properties": {
                                    "phase": { "type": "string" },
                                    "action": { "type": "string" }
                                    }
                                }
                                },
                                "use_cases": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "required": ["sub_sector", "actions", "results", "link"],
                                    "properties": {
                                    "sub_sector": { "type": "string" },
                                    "actions": { "type": "string" },
                                    "results": { "type": "string" },
                                    "link": { "type": "string" }
                                    }
                                }
                                },
                                "resources": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "required": ["title", "type", "link"],
                                    "properties": {
                                    "title": { "type": "string" },
                                    "type": { "type": "string" },
                                    "link": { "type": "string" }
                                    }
                                }
                                }
                            }
                            },
                            "contribution": {
                            "type": "object",
                            "required": [
                                "completeness",
                                "validator",
                                "history",
                                "improvement_proposal_link"
                            ],
                            "properties": {
                                "completeness": {
                                "type": "string",
                                "enum": ["squelette", "partielle", "complète", "Complète", ""]
                                },
                                "validator": {
                                "type": ["string", "null"]
                                },
                                "history": {
                                "type": "array",
                                "items": { "type": "string" }
                                },
                                "improvement_proposal_link": {
                                "type": ["string", "null"]
                                }
                            }
                            },
                            "traceability": {
                            "type": "object",
                            "required": [
                                "source_pdf",
                                "extraction_confidence",
                                "chunks_used"
                            ],
                            "properties": {
                                "source_pdf": {
                                "type": ["string", "null"]
                                },
                                "extraction_confidence": {
                                "type": ["number", "null"],
                                "minimum": 0,
                                "maximum": 1
                                },
                                "chunks_used": {
                                "type": "array",
                                "items": { "type": "string" }
                                }
                            }
                            }
                        }
                        }
                }
        }}}

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
