
from service.database_vect_service.database_vect_service import  DatabaseVectService
from service.llm_service.llm_service import LlmService
import os
from service.document_service.pdf_service import PdfService
import io
from service.bdd_service.bdd_service import PostgresService
from service.chunk_service.chunk_service import ChunkService
from service.embedding_service.embedding_service import EmbeddingService
import json
from model.config import Config
from constant import rag_constant
from fastapi import UploadFile
from config.logging_config import get_logger

# Logger pour ce module
logger = get_logger("rag_service")


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
        self.bdd_service = PostgresService()
        logger.info("RAG Service initialisé avec succès")

    
    def process_sector(self, file):    
        filename = file.filename
        logger.info(f"Traitement du secteur - fichier: {filename}")
        
        ## on crée une collection chroma
        collection = self.database_vect_service.get_or_create_collection(filename)
        
        document_to_load = PdfService(file, self.config)

        ##On extrait la donnée du pdf
        extract = document_to_load.extract_data()
        logger.debug("Extraction des données PDF terminée")
        
        ##Contient une liste de ProcessData (page_content, metadata) les éléments de la liste correspondent aux pages du pdf
        proceed = document_to_load.proceed_data(extract)
        ## chunk media
        document_chunked = self.chunk_service.chunk(proceed, rag_constant.CHUNK_SIZE,rag_constant.OVERLAP)
        logger.debug(f"Document découpé en {len(document_chunked)} chunks")
        
        # embed media
        document_embedded = self.embedding_service.embedding_bge_multilingual_batch(document_chunked)

        # Filtrer les chunks dont l'embedding a échoué (None)
        valid_pairs = [(chunk, emb) for chunk, emb in zip(document_chunked, document_embedded) if emb is not None]
        if len(valid_pairs) < len(document_chunked):
            logger.warning(f"{len(document_chunked) - len(valid_pairs)} embeddings ont échoué et seront exclus")
        document_chunked_filtered = [pair[0] for pair in valid_pairs]
        document_embedded_filtered = [pair[1] for pair in valid_pairs]

        ## store in db vect
        self.database_vect_service.collection_store_embedded_document(collection, document_chunked_filtered, document_embedded_filtered)
        logger.info(f"Stocké {len(document_chunked_filtered)} chunks dans ChromaDB")

        #embedding question
        embedded_fields = self.embedding_service.embedding_bge_multilingual_dict(rag_constant.SECTOR_QUERIES)

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
        
        ##On va donner results_dict au llm pour qu'il génère une réponse
        dict_to_string = json.dumps(results_dict, ensure_ascii=False)
        logger.debug(f"Contexte RAG préparé pour le LLM ({len(dict_to_string)} caractères)")

        ##appel llm le retour est un json au format demandé
        logger.info("Appel du LLM Mistral pour génération de la fiche secteur")
        mistral_request_secteur = self.llm_service.mistral_request_secteur(dict_to_string)
        fiche_secteur_json = json.dumps(mistral_request_secteur, ensure_ascii=False)

        #stocker la fiche secteur dans la BDD
        self.bdd_service.insert_new_fiche(mistral_request_secteur)
        logger.info(f"Fiche secteur créée et stockée avec succès pour: {filename}")

        return fiche_secteur_json

    def process_solution(self, file):
        filename = file.filename
        logger.info(f"Traitement de la solution - fichier: {filename}")
        
        ## on crée une collection chroma qui portera le nom du fichier
        collection = self.database_vect_service.get_or_create_collection(filename)
        
        document_to_load = PdfService(file, self.config)

        #On extrait la donnée du pdf
        extract = document_to_load.extract_data()
        logger.debug("Extraction des données PDF terminée")
        
        #Contient une liste de ProcessData (page_content, metadata) les éléments de la liste correspondent aux pages du pdf
        proceed = document_to_load.proceed_data(extract)
        # chunk media
        document_chunked = self.chunk_service.chunk(proceed, rag_constant.CHUNK_SIZE,rag_constant.OVERLAP)
        logger.debug(f"Document découpé en {len(document_chunked)} chunks")
        
        # embed media
        document_embedded = self.embedding_service.embedding_bge_multilingual_batch(document_chunked)

        # Filtrer les chunks dont l'embedding a échoué (None)
        valid_pairs = [(chunk, emb) for chunk, emb in zip(document_chunked, document_embedded) if emb is not None]
        if len(valid_pairs) < len(document_chunked):
            logger.warning(f"{len(document_chunked) - len(valid_pairs)} embeddings ont échoué et seront exclus")
        document_chunked_filtered = [pair[0] for pair in valid_pairs]
        document_embedded_filtered = [pair[1] for pair in valid_pairs]

        ## store in db vect
        self.database_vect_service.collection_store_embedded_document(collection, document_chunked_filtered, document_embedded_filtered)
        logger.info(f"Stocké {len(document_chunked_filtered)} chunks dans ChromaDB")

        #embedding question
        embedded_fields = self.embedding_service.embedding_bge_multilingual_dict(rag_constant.SOLUTION_QUERIES)

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
        
        ###On va donner results_dict au llm pour qu'il génère une réponse
        dict_to_string = json.dumps(results_dict, ensure_ascii=False)
        logger.debug(f"Contexte RAG préparé pour le LLM ({len(dict_to_string)} caractères)")

        ##appel llm le retour est un json au format demandé
        logger.info("Appel du LLM Mistral pour génération de la fiche solution")
        mistral_request_solution = self.llm_service.mistral_request_solution(dict_to_string)
        fiche_solution_json = json.dumps(mistral_request_solution, ensure_ascii=False)

        #stocker la fiche secteur dans la BDD
        self.bdd_service.insert_new_fiche(mistral_request_solution)
        logger.info(f"Fiche solution créée et stockée avec succès pour: {filename}")

        return fiche_solution_json


if __name__ == "__main__":
    #test simulé comme utilisé avec l'api
    rag_service_instance = rag_service()
    with open("src/main/service/ressources_pdf/a.pdf", "rb") as f:
        mock_pdf = UploadFile(file=f, filename="a.pdf")
        rag_service_instance.process_sector(mock_pdf)



