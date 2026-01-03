
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
        self.config = Config(load_file("src/main/config/config.json"))
        # services declaration
        self.chunk_service = ChunkService(self.config)
        self.embedding_service = EmbeddingService(self.config)
        self.database_vect_service = DatabaseVectService(self.config) 
        self.llm_service = LlmService(self.config)

    #TODO
    def process_sector(self, file):
        ## on récupère le fichier pdf
        file_like = io.BytesIO(file)
        file_like.filename = "a.pdf"  # Ajouter l'attribut filename

        ## on crée une collection chroma
        collection = self.database_vect_service.get_or_create_collection("c.pdf")
        
        #document_to_load = PdfService(file_like, self.config)
#
        ##On extrait la donnée du pdf
        #extract = document_to_load.extract_data()
        #
        ###Contient une liste de ProcessData (page_content, metadata) les éléments de la liste correspondent aux pages du pdf
        #proceed = document_to_load.proceed_data(extract)
        ### chunk media
        #document_chunked = self.chunk_service.chunk(proceed, rag_constant.CHUNK_SIZE,rag_constant.OVERLAP)
        #print(f"document chunked :{document_chunked}\n")
        ## embed media
        #document_embedded = self.embedding_service.embedding_bge_multilingual(document_chunked)

        ## store in db vect
        #self.database_vect_service.collection_store_embedded_document(collection, document_chunked, document_embedded)

        ##embedding question
        embedded_fields = self.embedding_service.embedding_bge_multilingual_batch(rag_constant.SECTOR_QUERIES)

        ## retrieve from db vect
        results_dict = {}
        for field, embedding in embedded_fields.items():
            results = collection.query(
                query_embeddings=embedding,
                n_results=3,
            )
            # Extraction des documents uniquement
            documents = results.get("documents", [])

            # documents = [[doc1, doc2, doc3]] → on aplati
            if documents and len(documents) > 0:
                results_dict[field] = documents[0]
            else:
                results_dict[field] = []
        print(f"Résultats pour le champ {results_dict}")
        
        ##On va donner results_dict au llm pour qu'il génère une réponse
        
        



if __name__ == "__main__":
    rag_service_instance = rag_service()
    
    # Lire le PDF en bytes (comme l'API le reçoit)
    import os
    base_path = os.path.dirname(__file__)
    pdf_path = os.path.join(base_path, "ressources_pdf/a.pdf")
    
    with open(pdf_path, 'rb') as f:
        pdf_bytes = f.read()  # Lire tout le contenu en bytes
    
    # Passer les bytes à process
    rag_service_instance.process_sector(pdf_bytes)
