from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from service.rag_service import rag_service

# Initialisation de l'application FastAPI
rag_app = FastAPI(
    title="WikiCO2 API",
    description="API pour le traitement de documents PDF avec RAG",
    version="1.0.0"
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
        result = rag_service_instance.process_solution(pdf.file)
        return result
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
        result = rag_service_instance.process_sector(pdf.file)
        result = rag_service_instance.process_sector(pdf.file)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du traitement du fichier: {str(e)}"
        )

# Pour lancer l'application :
# uvicorn main:rag_app --reload