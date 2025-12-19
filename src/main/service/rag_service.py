
from service.database_vect_service.database_vect_service import  DatabaseVectService
from service.llm_service.llm_service import LlmService
import os
from service.document_service.pdf_service import PdfService
import io

from service.chunk_service.chunk_service import ChunkService
from service.embedding_service.embedding_service import EmbeddingService
import json
from model.config import Config
from constant import rag_constant


def load_file(file):
    path = f"{os.getcwd()}"
    with open(f"{path}/{file}", 'r', encoding='utf-8') as read_file:
        return json.load(read_file)
        

class rag_service():
    def __init__(self):  #remettre src/main
        self.config = Config(load_file("config/config.json"))
        # services declaration
        self.chunk_service = ChunkService(self.config)
        self.embedding_service = EmbeddingService(self.config)
        self.database_vect_service = DatabaseVectService(self.config) 
        self.llm_service = LlmService(self.config)

    #TODO
    def process(self, file):
        ## on récupère le fichier pdf
        file_like = io.BytesIO(file)
        file_like.filename = "a.pdf"  # Ajouter l'attribut filename

        ## on crée une collection chroma
        collection = self.database_vect_service.get_or_create_collection(file_like.filename)
        
        document_to_load = PdfService(file_like, self.config)

        #On extrait la donnée du pdf
        extract = document_to_load.extract_data()
        
        ##Contient une liste de ProcessData (page_content, metadata) les éléments de la liste correspondent aux pages du pdf
        proceed = document_to_load.proceed_data(extract)
        ## chunk media
        document_chunked = self.chunk_service.chunk(proceed, rag_constant.CHUNK_SIZE,rag_constant.OVERLAP)
        ## embed media
        document_embedded = self.embedding_service.embedding_bge_multilingual(document_chunked)

        ## store in db vect
        self.database_vect_service.collection_store_embedded_document(collection, document_chunked, document_embedded)

        ## retrieve from db vect
        



if __name__ == "__main__":
    rag_service_instance = rag_service()
    
    # Lire le PDF en bytes (comme l'API le reçoit)
    import os
    base_path = os.path.dirname(__file__)
    pdf_path = os.path.join(base_path, "ressources_pdf/a.pdf")
    
    with open(pdf_path, 'rb') as f:
        pdf_bytes = f.read()  # Lire tout le contenu en bytes
    
    # Passer les bytes à process
    rag_service_instance.process(pdf_bytes)
