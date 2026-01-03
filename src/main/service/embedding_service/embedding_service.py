import requests
import numpy as np
from time import sleep


class EmbeddingService():
    def __init__(self, config):
        self.config = config

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


    def embedding_bge_multilingual_batch(self, dict_text):
        """
        Docstring for embedding_bge_multilingual_batch
        
        :param self: instance of EmbeddingService
        :param dict_text: constante définie dans rag_constant.py décrivant les éléments des fiches solutions et secteurs
        """
        response_data = {}  # dictionnaire pour stocker les résultats
        for field, query_text in dict_text.items():

        # On va embedder chaque valeur du dictionnaire correspondant aux champs des fiches solutions et secteurs
            embedding_response = self.embedding_bge_multilingual(query_text)
            response_data[field] = embedding_response

        return response_data