import requests
import numpy as np
from time import sleep

class EmbeddingService():
    def __init__(self, config):
        self.config = config

    def embedding_bge_multilingual(self, text):
        if isinstance(text, list) and all(isinstance(t, str) for t in text):
            list_text = text
        else:
            list_text = [content.page_content for content in text]

        response_data = []
        url = self.config.url_embedding_model
        headers = {
            "Content-Type": "text/plain",
            "Authorization": f"Bearer {self.config.access_token}",
        }

        for s in range(len(list_text)):
            # To avoid max try api calls
            sleep(0.25)
            print(f"embedding numero {s} en cours : {list_text[s]}")
            # generate embeddings vector
            response = requests.post(url, data=list_text[s], headers=headers, verify=False)
            if response.status_code == 200:
                response_data.append(response.json())
                print(f"embedding numero {s} reussi")

        return response_data