### taux de remplissage d'un json, recherche des champs vides.

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


# confiance : 

def confiance_global(logprobs: list):
    if not logprobs:
        return 0.0
    avg_logprob = sum(t["logprob"] for t in logprobs) / len(logprobs)
    confiance = math.exp(avg_logprob)
    return round(confiance, 3)

