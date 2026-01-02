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

@rag_app.post("/v1/process")
async def process(pdf: UploadFile = File(...)):
    """
    doc à écrire
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
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du traitement du fichier: {str(e)}"
        )

# Pour lancer l'application :
# uvicorn main:rag_app --reload