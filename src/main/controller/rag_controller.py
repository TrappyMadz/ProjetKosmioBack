from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from service.rag_service import rag_service
from dotenv import load_dotenv
from model.fiche_data import Fiche
import os
import json

# Initialisation de l'application FastAPI
load_dotenv() 
rag_app = FastAPI(
    title="WikiCO2 API",
    description="API pour le traitement de documents PDF avec RAG",
    version="1.0.0"
)

frontend_port = os.getenv("FRONTEND_PORT")
custom_origin = "http://localhost:" + frontend_port

origins = [
    custom_origin,
]

rag_app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*",]
)

# Initialisation du service
rag_service_instance = rag_service()

@rag_app.get("/")
async def home():
    return {"message": "Bonjour, bienvenue dans l'application wikiCO2 pfecytech2025"}

# solution et secteur
@rag_app.post("/v1/process/solution")
async def process_solution(pdf: UploadFile = File(...)):
    """
    Cette api prend un pdf et renvoie à l'utilisateur :
    - Si le fichier n'est pas un pdf, une erreur 400
    - Le json d'une solution classé correctement sous le format WO2 du contenu du pdf si tout s'est bien passé
    - Une erreur 500 si une erreur se produit
    """
    # Vérification du type de fichier
    if not pdf.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Le fichier doit être un PDF"
        )
    
    try:
        # Traitement du fichier
        result = rag_service_instance.process_solution(pdf)
        return json.loads(result)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du traitement du fichier: {str(e)}"
        )

@rag_app.post("/v1/process/sector")
async def process_sector(pdf: UploadFile = File(...)):
    """
    Cette api prend un pdf et renvoie à l'utilisateur :
    - Si le fichier n'est pas un pdf, une erreur 400
    - Le json d'un secteur classé correctement sous le format WO2 du contenu du pdf si tout s'est bien passé
    - Une erreur 500 si une erreur se produit
    """
    # Vérification du type de fichier
    if not pdf.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Le fichier doit être un PDF"
        )
    
    try:
        # Traitement du fichier
        result = rag_service_instance.process_sector(pdf)
        return json.loads(result)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du traitement du fichier: {str(e)}"
        )

@rag_app.get("/v1/get/{id}/history")
def get_fiche_history(id: int):
    """
    Renvoie la liste des anciennes version d'une fiche demandée. 
    Renvoie une erreur 404 si la fiche n'existe pas ou qu'elle n'a pas "d'ancienne version" (aucune modifications ?).
    """
    try:
        history = rag_service_instance.bdd_service.get_one_fiche_history(id)
        if history is None:
            raise HTTPException(
                status_code=404,
                detail="La fiche n'existe pas ou n'a jamais été modifiée (et n'a donc aucune ancienne version)"
            )
        return history
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        print(f"Erreur serveur : {e}")
        raise HTTPException(
            status_code=500,
            detail="Erreur serveur"
        )

@rag_app.put("/v1/update/{id}")
async def update_fiche(id: int, data: Fiche):
    """
    Met à jour la fiche avec les nouvelles informations. Il faut absolument renvoyer TOUTES les infos, même celles qui ne changent pas,
    car l'ancienne fiche est écrasée (elle se retrouvera dans la base d'archives).
    Renvoie une erreur 404 si la fiche n'existe pas, et une 500 si une autre erreur surviens. 
    Renvoie un objet json contenant un message de confirmation et l'id de la fiche mise à jour en cas de succès.
    """
    try:
        updated_id = rag_service_instance.bdd_service.update_fiche(id, data.model_dump())

        if updated_id is None:
            raise HTTPException(
                status_code=404,
                detail=f"Mise à jour impossible : la fiche {id} n'existe pas."
            )
        return {
            "message": f"Fiche {id} mise à jour avec succès",
            "id": updated_id
        }
    except HTTPException as http_err:
        # On relaisse passer l'erreur 404 qu'on a levée juste au-dessus
        raise http_err
    except Exception as e:
        print(f"Erreur serveur lors de l'update : {e}")
        raise HTTPException(
            status_code=500,
            detail="Erreur interne du serveur lors de la mise à jour"
        )

@rag_app.get("/v1/get/solution")
async def get_all_fiche_solution():
    """
    Renvoie la liste des fiches de type solution dans leur dernière version
    """
    try:
        fiches = rag_service_instance.bdd_service.get_all_solutions()
        if fiches is None:
            raise HTTPException(
                status_code=404,
                detail=f"Aucune fiche trouvée !"
            )
        return fiches
    except HTTPException as http_err:
        # On relaisse passer l'erreur 404 qu'on a levée juste au-dessus
        raise http_err
    except Exception as e:
        print(f"Erreur : {e}")
        raise HTTPException(
            status_code=500,
            detail="Erreur interne du serveur"
        )

@rag_app.get("/v1/get/sector")
async def get_all_fiche_sector():
    """
    Renvoie la liste des fiches de type secteur dans leur dernière version
    """
    try:
        fiches = rag_service_instance.bdd_service.get_all_sectors()
        if fiches is None:
            raise HTTPException(
                status_code=404,
                detail=f"Aucune fiche trouvée !"
            )
        return fiches
    except HTTPException as http_err:
        # On relaisse passer l'erreur 404 qu'on a levée juste au-dessus
        raise http_err
    except Exception as e:
        print(f"Erreur : {e}")
        raise HTTPException(
            status_code=500,
            detail="Erreur interne du serveur"
        )

@rag_app.get("/v1/get/{id}")
async def get_fiche_by_id(id: int):
    """
    Renvoie la fiche d'id id ou 404 si la fiche n'existe pas
    """
    try:
        fiche = rag_service_instance.bdd_service.get_fiche_by_id(id)
        if fiche is None:
            raise HTTPException(
                status_code=404,
                detail=f"La fiche {id} n'existe pas."
            )
        return fiche
    except HTTPException as http_err:
        # On relaisse passer l'erreur 404 qu'on a levée juste au-dessus
        raise http_err
    except Exception as e:
        print(f"Erreur : {e}")
        raise HTTPException(
            status_code=500,
            detail="Erreur interne du serveur"
        )






# Pour lancer l'application :
# uvicorn main:rag_app --reload