
from service.database_vect_service.database_vect_service import  DatabaseVectService
from service.llm_service.llm_service import LlmService
import os
from service.document_service.pdf_service import PdfService
import io
from service.bdd_service.bdd_service import PostgresService
from service.chunk_service.chunk_service import ChunkService
from service.embedding_service.embedding_service import EmbeddingService
from service.rerank_service.rerank_service import ReRankService
from service.bucket_service.bucket_service import BucketService
import json
from model.config import Config
from constant import rag_constant
from config.logging_config import get_logger

# Logger pour ce module
logger = get_logger("fiches_service")


def load_file(file):
    path = f"{os.getcwd()}"
    with open(f"{path}/{file}", 'r', encoding='utf-8') as read_file:
        return json.load(read_file)
        

class fiches_service():
    def __init__(self):  #remettre src/main
        self.config = Config(load_file("src/main/config/config.json"))

        # services declaration
        self.chunk_service = ChunkService(self.config)
        self.embedding_service = EmbeddingService(self.config)
        self.database_vect_service = DatabaseVectService(self.config) 
        self.llm_service = LlmService(self.config)
        self.bdd_service = PostgresService()
        self.rerank_service = ReRankService()
        self.bucket_service = BucketService()
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
        embedded_fields_metadata_summary = self.embedding_service.embedding_bge_multilingual_dict(rag_constant.SECTOR_QUERIES_METADATA_SUMMARY)
        embedded_fields_content_firstpart = self.embedding_service.embedding_bge_multilingual_dict(rag_constant.SECTOR_QUERIES_FIRST_PART)
        embedded_fields_content_lastpart = self.embedding_service.embedding_bge_multilingual_dict(rag_constant.SECTOR_QUERIES_LAST_PART)

        ## retrieve from db vect
        all_sources = []

        results_metadata_summary = self.database_vect_service.retrieve_from_collection(collection, embedded_fields_metadata_summary, all_sources, self.rerank_service)
        results_first_part = self.database_vect_service.retrieve_from_collection(collection, embedded_fields_content_firstpart, all_sources, self.rerank_service)
        results_last_part = self.database_vect_service.retrieve_from_collection(collection, embedded_fields_content_lastpart, all_sources, self.rerank_service)

        # Dédoublonner les sources par file_name + page + chunk
        seen = set()
        unique_sources = []
        for s in all_sources:
            key = (s["file_name"], s["page"], s["chunk"])
            if key not in seen:
                seen.add(key)
                unique_sources.append(s)

        dict_to_string_metadata_summary = json.dumps(results_metadata_summary, ensure_ascii=False)
        dict_to_string_first_part = json.dumps(results_first_part, ensure_ascii=False)
        dict_to_string_last_part = json.dumps(results_last_part, ensure_ascii=False)
        logger.debug(f"Contexte RAG préparé pour le LLM (metadata: {len(dict_to_string_metadata_summary)}, first: {len(dict_to_string_first_part)}, last: {len(dict_to_string_last_part)} caractères)")

        ##appel llm le retour est un json au format demandé
        logger.info("Appel du LLM Mistral pour génération de la fiche secteur")
        mistral_request_secteur = self.llm_service.mistral_request_secteur(dict_to_string_metadata_summary, dict_to_string_first_part, dict_to_string_last_part)
        
        # Injection de la traçabilité des sources dans le JSON
        mistral_request_secteur["data"]["traceability"] = {
            "source_pdf": filename,
            "extraction_confidence": mistral_request_secteur.get("qualimetrie", {}).get("confiance", ""),
            "chunks_used": unique_sources
        }
        

        # ajout en bdd
        id = self.bdd_service.insert_new_fiche(mistral_request_secteur["data"])
        self.bdd_service.add_qualimetrie(id, mistral_request_secteur["qualimetrie"])
        mistral_request_secteur["data"]["id"] = id  # on ajoute l'id de la fiche créée à la réponse

        fiche_secteur_json = json.dumps(mistral_request_secteur["data"], ensure_ascii=False)

        #stocker la fiche secteur dans la BDD
        
        logger.info(f"Fiche secteur créée et stockée avec succès pour: {filename}")
        print(fiche_secteur_json)
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
        embedded_fields_metadata_summary = self.embedding_service.embedding_bge_multilingual_dict(rag_constant.SOLUTION_QUERIES_METADATA_SUMMARY)
        embedded_fields_content_firstpart = self.embedding_service.embedding_bge_multilingual_dict(rag_constant.SOLUTION_QUERIES_FIRST_PART)
        embedded_fields_content_lastpart = self.embedding_service.embedding_bge_multilingual_dict(rag_constant.SOLUTION_QUERIES_LAST_PART)

        ## retrieve from db vect
        all_sources = []

        results_metadata_summary = self.retrieve_from_collection(collection, embedded_fields_metadata_summary, all_sources)
        results_first_part = self.retrieve_from_collection(collection, embedded_fields_content_firstpart, all_sources)
        results_last_part = self.retrieve_from_collection(collection, embedded_fields_content_lastpart, all_sources)

        # Dédoublonner les sources par file_name + page + chunk
        seen = set()
        unique_sources = []
        for s in all_sources:
            key = (s["file_name"], s["page"], s["chunk"])
            if key not in seen:
                seen.add(key)
                unique_sources.append(s)

        dict_to_string_metadata_summary = json.dumps(results_metadata_summary, ensure_ascii=False)
        dict_to_string_first_part = json.dumps(results_first_part, ensure_ascii=False)
        dict_to_string_last_part = json.dumps(results_last_part, ensure_ascii=False)
        logger.debug(f"Contexte RAG préparé pour le LLM (metadata: {len(dict_to_string_metadata_summary)}, first: {len(dict_to_string_first_part)}, last: {len(dict_to_string_last_part)} caractères)")

        ##appel llm le retour est un json au format demandé
        logger.info("Appel du LLM Mistral pour génération de la fiche solution")
        mistral_request_solution = self.llm_service.mistral_request_solution(dict_to_string_metadata_summary, dict_to_string_first_part, dict_to_string_last_part)
        
        # Injection de la traçabilité des sources dans le JSON
        mistral_request_solution["data"]["traceability"] = {
            "source_pdf": filename,
            "extraction_confidence": mistral_request_solution.get("qualimetrie", {}).get("confiance", ""),
            "chunks_used": unique_sources
        }
        
        # ajout en bdd
        id = self.bdd_service.insert_new_fiche(mistral_request_solution["data"])
        self.bdd_service.add_qualimetrie(id, mistral_request_solution["qualimetrie"])
        mistral_request_solution["data"]["id"] = id  # on ajoute l'id de la fiche créée à la réponse
        fiche_solution_json = json.dumps(mistral_request_solution["data"], ensure_ascii=False)

        #stocker la fiche secteur dans la BDD

        logger.info(f"Fiche solution créée et stockée avec succès pour: {filename}")
        print(fiche_solution_json)
        return fiche_solution_json

    def get_fiche_history(self, id: int):
        history = self.bdd_service.get_one_fiche_history(id)
        return history

<<<<<<< HEAD
<<<<<<< HEAD
    def update_fiche(self,id: int, data):
        updated_id = self.bdd_service.update_fiche(id, data.model_dump())
        return updated_id
=======
                if documents and len(documents) > 0:
                    docs = documents[0]
                    metas = metadatas[0] if metadatas and len(metadatas) > 0 else [{}] * len(docs)

                    # 2. Re-ranking avec FlashRank
                    reranked_docs, reranked_metas = self.rerank_service.rerank(
                        query=field,
                        documents=docs,
                        metadatas=metas,
                        top_k=rag_constant.N_RESULTS_RERANKED
                    )

                    # 3. Enrichir avec les sources
                    enriched_docs = []
                    for doc, meta in zip(reranked_docs, reranked_metas):
                        file_name = meta.get("file_name", "")
                        page = meta.get("page", "")
                        enriched_docs.append(f"[Source: {file_name}, Page: {page}] {doc}")
                        all_sources.append({"file_name": file_name, "page": page, "chunk": doc})
                    results_dict[field] = enriched_docs
                else:
                    results_dict[field] = []
            return results_dict

if __name__ == "__main__":
    #test simulé comme utilisé avec l'api
    fiches_service_instance = fiches_service()
    with open("src/main/service/ressources_pdf/a.pdf", "rb") as f:
        mock_pdf = UploadFile(file=f, filename="a.pdf")
        fiches_service_instance.process_sector(mock_pdf)
>>>>>>> d289a33 (naming : renaming files)
=======
    def update_fiche(self,id: int, data):
        updated_id = self.bdd_service.update_fiche(id, data.model_dump())
        return updated_id
>>>>>>> 60a8258 (refactor : refactoring code to job logic)

    def get_all_fiche_solution(self):
        return self.bdd_service.get_all_solutions()
    
    def get_all_fiche_sector(self):
        return self.bdd_service.get_all_sectors()

    def get_fiche_by_id(self,id: int):
        return self.bdd_service.get_fiche_by_id(id)
