### taux de remplissage d'un json, recherche des champs vides.
import json
import math


def recherche_Tot_Vide(json, videT=0, totT=0):
    
    totT = 0
    videT = 0
    if isinstance(json, dict) and len(json) > 0:
        for v in json.values():
            vide, tot = recherche_Tot_Vide(v, 0, 0)
            videT += vide
            totT += tot

    elif isinstance(json, list) and len(json) > 0:
        for v in json:
            vide, tot = recherche_Tot_Vide(v, 0, 0)
            videT += vide
            totT += tot
    
    else :
        if ( json == "" or json == [] or json == {} or json is None):
            videT += 1
        totT += 1

    return videT, totT


def taux_remplissage(json):
    videT, totT = recherche_Tot_Vide(json, 0, 0)
    if totT == 0:
        return 0.0
    taux = (totT - videT) / totT
    return taux

def confiance(text, logprobs):
    """
    text: string JSON généré par le LLM
    logprobs: liste type Mistral -> [{"token": "...", "logprob": -0.23}, ...]
    """

    # ---------- reconstruire tokens avec positions ----------
    tokens = []
    current_pos = 0

    for item in logprobs:
        token = item["token"]
        lp = item["logprob"]

        start = current_pos
        end = start + len(token)

        tokens.append({
            "token": token,
            "logprob": lp,
            "start": start,
            "end": end
        })

        current_pos = end

    # ---------- extraire champs string ----------
    try:
        data = json.loads(text)
    except Exception:
        return {"global_confidence": 0, "fields": {}}

    def extract_strings(obj, path=""):
        results = []

        if isinstance(obj, dict):
            for k, v in obj.items():
                new_path = f"{path}.{k}" if path else k
                results.extend(extract_strings(v, new_path))

        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                new_path = f"{path}[{i}]"
                results.extend(extract_strings(item, new_path))

        elif isinstance(obj, str):
            results.append({"path": path, "value": obj})

        return results

    fields = extract_strings(data)

    # ---------- calcul confiance par champ ----------
    field_scores = {}

    for field in fields:
        value = field["value"]
        path = field["path"]

        start_index = text.find(value)
        if start_index == -1:
            continue

        end_index = start_index + len(value)

        relevant = [
            t["logprob"]
            for t in tokens
            if t["start"] >= start_index
            and t["end"] <= end_index
            and len(t["token"].strip()) > 2  # ignore petits tokens
        ]

        if not relevant:
            continue

        mean_logprob = sum(relevant) / len(relevant)

        # transformation en probabilité 0-1
        confidence = math.exp(mean_logprob)

        # pénalité si tokens très improbables
        low_prob_ratio = sum(lp < -4 for lp in relevant) / len(relevant)

        adjusted_confidence = confidence * (1 - low_prob_ratio)

        field_scores[path] = round(adjusted_confidence, 4)

    # ---------- score global ----------
    if field_scores:
        global_confidence = sum(field_scores.values()) / len(field_scores)
    else:
        global_confidence = 0

    return {
        "global_confidence": round(global_confidence, 4),
        "fields": field_scores
    }



### Json bien constitué : pas de champs manquant et pas de champs inventés

def json_bien_constitue(json):
    if json["type"].lower() == "solution":
        return json_bien_constitue_solution(json)
    elif json["type"].lower() == "sector":
        return json_bien_constitue_secteur(json)
    else:
        raise ValueError("Type de fiche inconnu. Le champ 'type' doit être soit 'solution' soit 'secteur'. Nous ne pouvons savoir si le json est bien constitué.")
    
def json_bien_constitue_solution(data):
    champs_attendus_n1 = {"type", "id", "title", "metadata", "summary", "content", "contribution", "traceability"}
    champs_json = set(data.keys())
    res_entrop = []
    res_enmoins = []
    res_entrop.append("premier niveau du json :" + str(champs_json.difference(champs_attendus_n1)))
    res_enmoins.append("premier niveau du json :" + str(champs_attendus_n1.difference(champs_json)))

    if "metadata" in champs_json:
        champs_attendus_n2 = {
            "category", "system", "type", "maturity",
            "cost_scale", "complexity", "last_update", "contributors"
        }
        champs_metadata = set(data["metadata"].keys())
        res_entrop.append("metadata :" + str(champs_metadata.difference(champs_attendus_n2)))
        res_enmoins.append("metadata :" + str(champs_attendus_n2.difference(champs_metadata)))

    if "content" in champs_json:
        champs_attendus_n2 = {
            "context", "mecanism", "applicability", "impacts",
            "levers", "implementation_path", "risks", "examples", "resources"
        }
        champs_content = set(data["content"].keys())
        res_entrop.append("content :" + str(champs_content.difference(champs_attendus_n2)))
        res_enmoins.append("content :" + str(champs_attendus_n2.difference(champs_content)))

        if "context" in champs_content:
            champs_attendus_n3 = {"objective", "scope_includes", "scope_excludes", "prerequisites"}
            res_entrop.append("content.context :" + str(set(data["content"]["context"].keys()).difference(champs_attendus_n3)))
            res_enmoins.append("content.context :" + str(champs_attendus_n3.difference(set(data["content"]["context"].keys()))))

        if "mecanism" in champs_content:
            champs_attendus_n3 = {"description", "variants"}
            res_entrop.append("content.mecanism :" + str(set(data["content"]["mecanism"].keys()).difference(champs_attendus_n3)))
            res_enmoins.append("content.mecanism :" + str(champs_attendus_n3.difference(set(data["content"]["mecanism"].keys()))))

        if "applicability" in champs_content:
            champs_attendus_n3 = {"conditions", "avoid_if"}
            res_entrop.append("content.applicability :" + str(set(data["content"]["applicability"].keys()).difference(champs_attendus_n3)))
            res_enmoins.append("content.applicability :" + str(champs_attendus_n3.difference(set(data["content"]["applicability"].keys()))))

        if "impacts" in champs_content:
            champs_attendus_n3 = {"energy", "co2", "costs", "co_benefits"}
            res_entrop.append("content.impacts :" + str(set(data["content"]["impacts"].keys()).difference(champs_attendus_n3)))
            res_enmoins.append("content.impacts :" + str(champs_attendus_n3.difference(set(data["content"]["impacts"].keys()))))

        if "implementation_path" in champs_content:
            ip = data["content"]["implementation_path"]
            champs_attendus_n3 = {"step", "details"}
            if isinstance(ip, list) and len(ip) > 0:
                try : 
                    res_entrop.append("content.implementation_path :" + str(set(ip[0].keys()).difference(champs_attendus_n3)))
                    res_enmoins.append("content.implementation_path :" + str(champs_attendus_n3.difference(set(ip[0].keys()))))
                except Exception as e:
                    res_enmoins.append("content.implementation_path :" + str(champs_attendus_n3))
            else:
                res_enmoins.append("content.implementation_path (liste vide) :" + str(champs_attendus_n3))

        if "risks" in champs_content:
            risks = data["content"]["risks"]
            champs_attendus_n3 = {"risk"}
            if isinstance(risks, list) and len(risks) > 0:
                try :
                    res_entrop.append("content.risks :" + str(set(risks[0].keys()).difference(champs_attendus_n3)))
                    res_enmoins.append("content.risks :" + str(champs_attendus_n3.difference(set(risks[0].keys()))))
                except Exception as e:
                    res_enmoins.append("content.risks :" + str(champs_attendus_n3))
            else:
                res_enmoins.append("content.risks (liste vide) :" + str(champs_attendus_n3))

        if "examples" in champs_content:
            examples = data["content"]["examples"]
            champs_attendus_n3 = {"title", "type", "link"}
            if isinstance(examples, list) and len(examples) > 0:
                try :
                    res_entrop.append("content.examples :" + str(set(examples[0].keys()).difference(champs_attendus_n3)))
                    res_enmoins.append("content.examples :" + str(champs_attendus_n3.difference(set(examples[0].keys()))))
                except Exception as e:
                    res_enmoins.append("content.examples :" + str(champs_attendus_n3))
            else:
                res_enmoins.append("content.examples (liste vide) :" + str(champs_attendus_n3))

        if "resources" in champs_content:
            resources = data["content"]["resources"]
            champs_attendus_n3 = {"title", "type", "link"}
            if isinstance(resources, list) and len(resources) > 0:
                try :
                    res_entrop.append("content.resources :" + str(set(resources[0].keys()).difference(champs_attendus_n3)))
                    res_enmoins.append("content.resources :" + str(champs_attendus_n3.difference(set(resources[0].keys()))))
                except Exception as e:
                    res_enmoins.append("content.resources :" + str(champs_attendus_n3))
            else:
                res_enmoins.append("content.resources (liste vide) :" + str(champs_attendus_n3))


    if "contribution" in champs_json:
        champs_attendus_n2 = {"validation_level", "history", "improvement_proposal_link"}
        res_entrop.append("contribution :" + str(set(data["contribution"].keys()).difference(champs_attendus_n2)))
        res_enmoins.append("contribution :" + str(champs_attendus_n2.difference(set(data["contribution"].keys()))))

    if "traceability" in champs_json:
        champs_attendus_n2 = {"source_pdf", "extraction_confidence", "chunks_used"}
        res_entrop.append("traceability :" + str(set(data["traceability"].keys()).difference(champs_attendus_n2)))
        res_enmoins.append("traceability :" + str(champs_attendus_n2.difference(set(data["traceability"].keys()))))

    return [res_entrop, res_enmoins]

def json_bien_constitue_secteur(data):
    champs_attendus_n1 = {"type", "id", "title", "metadata", "summary", "content", "contribution", "traceability"}
    champs_json = set(data.keys())
    res_entrop = []
    res_enmoins = []
    res_entrop.append("premier niveau du json :" + str(champs_json.difference(champs_attendus_n1)))
    res_enmoins.append("premier niveau du json :" + str(champs_attendus_n1.difference(champs_json)))

    if "metadata" in champs_json:
        champs_attendus_n2 = {"sub_sectors", "company_size", "last_update", "contributors"}
        res_entrop.append("metadata :" + str(set(data["metadata"].keys()).difference(champs_attendus_n2)))
        res_enmoins.append("metadata :" + str(champs_attendus_n2.difference(set(data["metadata"].keys()))))

    if "content" in champs_json:
        champs_attendus_n2 = {
            "emissions_profile", "challenges", "regulations",
            "systems_matrix", "sector_path", "use_case", "resources"
        }
        champs_content = set(data["content"].keys())
        res_entrop.append("content :" + str(champs_content.difference(champs_attendus_n2)))
        res_enmoins.append("content :" + str(champs_attendus_n2.difference(champs_content)))
        if "emissions_profile" in champs_content:
            champs_attendus_n3 = {"process", "utilities", "building", "transport", "waste"}
            res_entrop.append("content.emissions_profile :" + str(set(data["content"]["emissions_profile"].keys()).difference(champs_attendus_n3)))
            res_enmoins.append("content.emissions_profile :" + str(champs_attendus_n3.difference(set(data["content"]["emissions_profile"].keys()))))

        if "challenges" in champs_content:
            challenges = data["content"]["challenges"]
            champs_attendus_n3 = {"title", "description"}
            if isinstance(challenges, list) and len(challenges) > 0:
                try : 
                    res_entrop.append("content.challenges :" + str(set(challenges[0].keys()).difference(champs_attendus_n3)))
                    res_enmoins.append("content.challenges :" + str(champs_attendus_n3.difference(set(challenges[0].keys()))))
                except Exception as e:
                    res_enmoins.append("content.challenges :" + str(champs_attendus_n3))
            else:
                res_enmoins.append("content.challenges (liste vide) :" + str(champs_attendus_n3))
            

        if "systems_matrix" in champs_content:
            systems = data["content"]["systems_matrix"]
            champs_attendus_n3 = {"system", "impact", "priority", "solutions"}
            if isinstance(systems, list) and len(systems) > 0:
                try :
                    res_entrop.append("content.systems_matrix :" + str(set(systems[0].keys()).difference(champs_attendus_n3)))
                    res_enmoins.append("content.systems_matrix :" + str(champs_attendus_n3.difference(set(systems[0].keys()))))
                except Exception as e:
                    res_enmoins.append("content.systems_matrix :" + str(champs_attendus_n3))
            else:
                res_enmoins.append("content.systems_matrix (liste vide) :" + str(champs_attendus_n3))

        if "sector_path" in champs_content:
            path = data["content"]["sector_path"]
            champs_attendus_n3 = {"phase", "action"}
            if isinstance(path, list) and len(path) > 0:
                try : 
                    res_entrop.append("content.sector_path :" + str(set(path[0].keys()).difference(champs_attendus_n3)))
                    res_enmoins.append("content.sector_path :" + str(champs_attendus_n3.difference(set(path[0].keys()))))
                except Exception as e:
                    res_enmoins.append("content.sector_path :" + str(champs_attendus_n3))
            else:
                res_enmoins.append("content.sector_path (liste vide) :" + str(champs_attendus_n3))

        if "use_case" in champs_content:
            use_case = data["content"]["use_case"]
            champs_attendus_n3 = {"sub_sector", "actions", "results", "link"}
            if isinstance(use_case, list) and len(use_case) > 0:
                try :
                    res_entrop.append("content.use_case :" + str(set(use_case[0].keys()).difference(champs_attendus_n3)))
                    res_enmoins.append("content.use_case :" + str(champs_attendus_n3.difference(set(use_case[0].keys()))))
                except Exception as e:
                    res_enmoins.append("content.use_case :" + str(champs_attendus_n3))
            else:
                res_enmoins.append("content.use_case (liste vide) :" + str(champs_attendus_n3))

        if "resources" in champs_content:
            resources = data["content"]["resources"]
            champs_attendus_n3 = {"title", "type", "link"}
            if isinstance(resources, list) and len(resources) > 0:
                try :
                    res_entrop.append("content.resources :" + str(set(resources[0].keys()).difference(champs_attendus_n3)))
                    res_enmoins.append("content.resources :" + str(champs_attendus_n3.difference(set(resources[0].keys()))))
                except Exception as e:
                    res_enmoins.append("content.resources :" + str(champs_attendus_n3))
            else:
                res_enmoins.append("content.resources (liste vide) :" + str(champs_attendus_n3))

    if "contribution" in champs_json:
        champs_attendus_n2 = {"completeness", "validator", "history", "improvement_proposal_link"}
        res_entrop.append("contribution :" + str(set(data["contribution"].keys()).difference(champs_attendus_n2)))
        res_enmoins.append("contribution :" + str(champs_attendus_n2.difference(set(data["contribution"].keys()))))

    if "traceability" in champs_json:
        champs_attendus_n2 = {"source_pdf", "extraction_confidence", "chunks_used"}
        res_entrop.append("traceability :" + str(set(data["traceability"].keys()).difference(champs_attendus_n2)))
        res_enmoins.append("traceability :" + str(champs_attendus_n2.difference(set(data["traceability"].keys()))))

    return [res_entrop, res_enmoins]