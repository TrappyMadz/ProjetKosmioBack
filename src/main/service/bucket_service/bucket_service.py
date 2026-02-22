import boto3
from botocore.exceptions import ClientError
import os
from datetime import datetime
from config.logging_config import get_logger

logger = get_logger(__name__)

class BucketService:
    def __init__(self):
        # Configuration via les variables d'environnement Docker
        self.s3_client = boto3.client(
            's3',
            endpoint_url=f"http://{os.getenv('BUCKET_HOST', 'minio')}:9000",
            aws_access_key_id=os.getenv('MINIO_ROOT_USER'),
            aws_secret_access_key=os.getenv('MINIO_ROOT_PASSWORD')
        )
        self.bucket_name = "fiches-images"
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
        except:
            logger.info(f"Le bucket {self.bucket_name} n'existe pas. Création en cours...")
            self.s3_client.create_bucket(Bucket=self.bucket_name)

    def upload_image(self, file_content, file_name):
        """
        Upload une image et retourne la clé unique (file_key).
        """
        # Nom unique pour éviter d'écraser des fichiers de même nom
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_key = f"{timestamp}_{file_name}"

        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=file_content
            )
            return file_key
        except ClientError as e:
            logger.error(f"Erreur Upload MinIO: {e}")
            return None

    def delete_image(self, file_key):
        """Supprime un fichier du bucket en cas d'erreur de transaction. NE PAS UTILISER POUR UNE SUPPRESSION PROPRE"""
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=file_key)
            return True
        except Exception as e:
            logger.error(f"Impossible de supprimer le fichier orphelin {file_key} : {e}")
            return False

    def get_image_stream(self, file_key):
        """Récupère l'objet binaire depuis MinIO sous forme de stream."""
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=file_key)
            return response['Body'] # Renvoie le corps du fichier
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de l'image dans MinIO: {e}")
            return None