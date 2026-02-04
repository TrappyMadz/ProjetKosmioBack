from pydantic import BaseModel
from typing import Dict, Any

class Fiche(BaseModel):
    type: str
    title: str
    summary: str
    metadata: Dict[str, Any] = {}
    content: Dict[str, Any] = {}
    contribution: Dict[str, Any] = {}
    traceability: Dict[str, Any] = {}