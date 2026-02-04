import requests
import numpy as np
from time import sleep
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Semaphore
from typing import List, Union, Optional
from config.logging_config import get_logger

# Logger pour ce module
logger = get_logger("embedding_service")


class EmbeddingService():
    def __init__(self, config):
        self.config = config

    def _embed_single_text(self, text: str, index: int, semaphore: Semaphore, max_retries: int = 3) -> tuple:
        """
        Embed un seul texte avec gestion des erreurs et retry.
        
        Args:
            text: Le texte à embedder
            index: L'index du texte dans la liste originale (pour conserver l'ordre)
            semaphore: Semaphore pour le rate limiting
            max_retries: Nombre maximum de tentatives en cas d'échec
            
        Returns:
            Tuple (index, embedding) ou (index, None) en cas d'échec
        """
        url = self.config.url_embedding_model
        headers = {
            "Content-Type": "text/plain",
            "Authorization": f"Bearer {self.config.access_token}",
        }
        
        for attempt in range(max_retries):
            try:
                with semaphore:  # Rate limiting
                    response = requests.post(url, data=text, headers=headers, verify=False, timeout=30)
                    
                if response.status_code == 200:
                    logger.debug(f"Embedding {index} réussi")
                    return (index, response.json())
                elif response.status_code == 429:  # Rate limit exceeded
                    wait_time = (attempt + 1) * 2  # Backoff exponentiel
                    logger.warning(f"Rate limit atteint pour embedding {index}, attente de {wait_time}s...")
                    sleep(wait_time)
                else:
                    logger.warning(f"Embedding {index} échoué (tentative {attempt + 1}): status {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Erreur réseau pour embedding {index} (tentative {attempt + 1}): {e}")
                sleep(1)
        
        logger.error(f"Embedding {index} définitivement échoué après {max_retries} tentatives")
        return (index, None)

    def embedding_bge_multilingual_batch(
        self, 
        text: Union[str, List[str], List], 
        max_workers: int = 10, 
        rate_limit: int = 20,
        max_retries: int = 3
    ) -> List:
        """
        Embed une liste de textes en parallèle pour des performances optimales.
        
        Cette fonction utilise ThreadPoolExecutor pour paralléliser les appels API,
        ce qui réduit significativement le temps d'exécution pour l'embedding de
        documents PDF entiers.
        
        Args:
            text: Peut être:
                - Une string unique
                - Une liste de strings
                - Une liste d'objets avec attribut page_content (ProcessedData)
            max_workers: Nombre maximum de threads parallèles (défaut: 10)
            rate_limit: Nombre maximum de requêtes simultanées (défaut: 20)
            max_retries: Nombre de tentatives par embedding en cas d'échec (défaut: 3)
            
        Returns:
            Liste des embeddings dans le même ordre que les textes en entrée.
            Les embeddings échoués sont remplacés par None.
            
        Example:
            >>> service = EmbeddingService(config)
            >>> chunks = ["texte 1", "texte 2", "texte 3"]
            >>> embeddings = service.embedding_bge_multilingual_batch(chunks, max_workers=5)
        """
        # Normaliser l'entrée en liste de strings
        if isinstance(text, str):
            list_text = [text]
        elif isinstance(text, list) and all(isinstance(t, str) for t in text):
            list_text = text
        elif isinstance(text, list) and len(text) > 0 and hasattr(text[0], 'page_content'):
            list_text = [content.page_content for content in text]
        else:
            logger.warning("Format de texte non reconnu, tentative de conversion...")
            list_text = [str(t) for t in text] if isinstance(text, list) else [str(text)]
        
        if not list_text:
            logger.warning("Liste de textes vide, retour d'une liste vide")
            return []
        
        logger.info(f"Début du batch embedding de {len(list_text)} textes avec {max_workers} workers")
        
        # Semaphore pour contrôler le rate limiting
        semaphore = Semaphore(rate_limit)
        
        # Résultats ordonnés
        results = [None] * len(list_text)
        failed_count = 0
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Soumettre toutes les tâches
            futures = {
                executor.submit(self._embed_single_text, text, idx, semaphore, max_retries): idx 
                for idx, text in enumerate(list_text)
            }
            
            # Collecter les résultats au fur et à mesure
            completed = 0
            for future in as_completed(futures):
                completed += 1
                if completed % 10 == 0 or completed == len(list_text):
                    logger.info(f"Progression: {completed}/{len(list_text)} embeddings terminés")
                
                try:
                    index, embedding = future.result()
                    results[index] = embedding
                    if embedding is None:
                        failed_count += 1
                except Exception as e:
                    idx = futures[future]
                    logger.error(f"Exception inattendue pour embedding {idx}: {e}")
                    failed_count += 1
        
        # Rapport final
        success_count = len(list_text) - failed_count
        logger.info(f"Batch embedding terminé: {success_count}/{len(list_text)} réussis ({failed_count} échecs)")
        
        return results

    def embedding_bge_multilingual(self, text):
        #cas où on travaille avec une liste de string pour les chunks
        if isinstance(text, list) and all(isinstance(t, str) for t in text):
            list_text = text
        
        #Pour une seule question (sert pour l'embedding des champs des fiches solutions et secteurs)
        if isinstance(text, str):
            list_text = [text]
            
        else:
            #cas ou on travaille avec une liste de processed_data pour les chunks (avec page_content et metadata)
            list_text = [content.page_content for content in text]

        response_data = []
        
        url = self.config.url_embedding_model
        headers = {
            "Content-Type": "text/plain",
            "Authorization": f"Bearer {self.config.access_token}",
        }

        for s in range(len(list_text)):
            # To avoid max try api calls
            sleep(0.1)
            print(f"embedding numero {s} en cours : {list_text[s]}")
            # generate embeddings vector
            response = requests.post(url, data=list_text[s], headers=headers, verify=False)
            print(f"response status code: {response.status_code}")
            if response.status_code == 200:
                response_data.append(response.json())
                print(f"embedding numero {s} reussi")

        return response_data


    def embedding_bge_multilingual_dict(self, dict_text):
        """
        :param self: instance de EmbeddingService
        :param dict_text: constante définie dans rag_constant.py décrivant les éléments des fiches solutions et secteurs
        """
        response_data = {}  # dictionnaire pour stocker les résultats
        for field, query_text in dict_text.items():

        # On va embedder chaque valeur du dictionnaire correspondant aux champs des fiches solutions et secteurs
            embedding_response = self.embedding_bge_multilingual(query_text)
            response_data[field] = embedding_response

        return response_data