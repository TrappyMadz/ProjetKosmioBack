import requests


class LlmService():
    def __init__(self, config):
        self.config = config

    #juste pour faire une requete mixtral simple
    def mistral_request(self, content):
        url = self.config.url_model_llm
        payload = {
            "max_tokens": 512,
            "messages": [
                {
                    "content": content,
                    "role": "user"
                }
            ],
            "model": self.config.model_llm,
            "temperature": 0,
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.access_token}",
        }

        response = requests.post(url, json=payload, headers=headers, verify=False)
        if response.status_code == 200:
            # Handle response
            response_data = response.json()
            # Parse JSON response
            choices = response_data["choices"]
            for choice in choices:
                text = choice["message"]["content"]
                # Process text and finish_reason
                print(text)
        else:
            print("Error:", response.status_code)

    #TODO
    def rag_nlp_completion(self, retrieved_sentences):
        url = self.config.url_model_llm

        messages = [
            #preprompt
            {"role": "system",
             "content": (
                    #préparer le preprompt en donnant les consignes ainsi que le modèle de sortie
                )
            },

            {
                "role": "user",
                "content": f"""Informations fournies : {retrieved_sentences} \

        """
            }
        ]

        payload = {
            "model": self.config.model_llm,
            "temperature": 0,
            "max_tokens": 2000,
            "messages": messages
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.access_token}",
        }

        response = requests.post(url, json=payload, headers=headers, verify = False)
        if response.status_code == 200:
            response_data = response.json()
            return response_data["choices"][0]["message"]["content"]
        else:
            print("Erreur:", response.status_code)
            return None
