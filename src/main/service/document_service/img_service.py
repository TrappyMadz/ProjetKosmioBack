import requests
import base64
import mimetypes
from model.extract_data import Extractdata
from model.process_data import ProcessData
from service.document_service.base_service import BaseService

#peut servir pour les images intégrées dans les pdf aussi
class ImgService(BaseService):
    def __init__(self, file, config):
        self.file = file
        self.config = config

    def extract_data(self):
        # To define the good format before encoding
        mime_type, _ = mimetypes.guess_type(self.file.filename)

        # read file
        image_data = self.file.read()
        encoded_image = f"data:{mime_type};base64,{base64.b64encode(image_data).decode('utf-8')}"

        # Return service
        img_service = Extractdata(encoded_image, 'IMG_SERVICE', self.file.filename)
        return img_service
    
    def proceed_data(self, extract_data):
        metadata = {'file_name': extract_data.file_name}

        encoded_image = extract_data.extract_data

        url = self.config.url_model_vlm

        payload = {
        "max_tokens": self.config.max_token_vlm,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """Tu est un assistant qui écris les images que tu reçois. \
                        Décris les images de manière neutre, si les images contiennent du texte, donne tout le texte. \
                        Tu interprète le plus possible l'image\
                        Ne traduit pas le texte dans l'image. \
                        
                        """
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": encoded_image
                        }
                    }
                ]
            }
        ],
        "model": self.config.model_vlm,
        "temperature": self.config.temperature_vlm,
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
                return [ProcessData(text, metadata)]
        else:
            print("Error:", response.status_code)