import csv
import os
import logging
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError
from settings.config import settings
from tempfile import NamedTemporaryFile

logging.getLogger("azure").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) 


class BlobManager:

    @staticmethod
    def ensure_container_exists(container_name):
        try:
            blob_service_client = BlobServiceClient.from_connection_string(settings.AZURE_STORAGE_CONNECTION_STRING)
            container_client = blob_service_client.get_container_client(container_name)
            container_client.create_container()
            logger.info(f"Created container '{container_name}'.")
        except ResourceExistsError:
            logger.info(f"Container '{container_name}' already exists.")
        except Exception as e:
            logger.error(f"Error creating container: {e}")
    
    @staticmethod
    def get_blob_client(container, blob_name):
        try:
            blob_service_client = BlobServiceClient.from_connection_string(settings.AZURE_STORAGE_CONNECTION_STRING)
            return blob_service_client.get_blob_client(container=container, blob=blob_name)
        except Exception as e:
            logger.error(f"Failed to get blob client for '{blob_name}' in container '{container}': {e}")
            return None
    
    @staticmethod
    def upload_to_blob_storage(file_path, blob_name, container):
        try:
            blob_service_client = BlobServiceClient.from_connection_string(settings.AZURE_STORAGE_CONNECTION_STRING)
            blob_client = blob_service_client.get_blob_client(container, blob=blob_name)
            with open(file_path, "rb") as data:
                blob_client.upload_blob(data, overwrite=True)
            logger.info(f"Uploaded '{blob_name}' to Azure Blob Storage.")
        except Exception as e:
            logger.error(f"Failed to upload '{blob_name}': {e}")
     
    @staticmethod   
    def create_file(filename):
        with open(filename, "w") as f:
            pass  
        logger.info(f"Created empty file: {filename}")
        
    @staticmethod
    def download_from_blob_storage(blob_name, file_path, container):
        try:
            blob_service_client = BlobServiceClient.from_connection_string(settings.AZURE_STORAGE_CONNECTION_STRING)
            blob_client = blob_service_client.get_blob_client(container, blob=blob_name)
            with open(file_path, "wb") as download_file:
                download_file.write(blob_client.download_blob().readall())
            logger.info(f"Downloaded '{blob_name}' to '{file_path}'.")
            return True
        except Exception as e:
            logger.error(f"Failed to download '{blob_name}': {e}")
            # If the blob is not found, create an empty file
            if "BlobNotFound" in str(e):
                logger.warning(f"Blob '{blob_name}' not found. Creating a new file...")
                BlobManager.create_file(file_path) 
                return False
            return False
    
    @staticmethod
    def create_folder(folder_name, container):
        try:
            blob_service_client = BlobServiceClient.from_connection_string(settings.AZURE_STORAGE_CONNECTION_STRING)
            blob_client = blob_service_client.get_blob_client(container, blob=f"{folder_name}/")
            blob_client.upload_blob(b"", overwrite=True)
            logger.info(f"Created folder '{folder_name}' in container '{container}'.")
        except Exception as e:
            logger.error(f"Failed to create folder '{folder_name}': {e}")
     
    @staticmethod        
    def is_valid_ticker(exchange, ticker, container):
        blob_filename = f"{exchange.lower()}/{exchange.lower()}_tickers.csv"

        with NamedTemporaryFile(delete=False, suffix=".csv") as tmp_file:
            tmp_path = tmp_file.name

        try:
            downloaded = BlobManager.download_from_blob_storage(blob_filename, tmp_path, container=container)
            if not downloaded:
                logger.warning(f"No ticker file found for exchange '{exchange}'.")
                return False

            with open(tmp_path, newline="", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if row.get("Symbol", "").strip().upper() == ticker.upper():
                        return True
                return False

        except Exception as e:
            logger.error(f"Error validating ticker '{ticker}' in '{exchange}': {e}")
            return False
        finally:
            os.remove(tmp_path)

# Instantiate it once
blob_manager = BlobManager()
