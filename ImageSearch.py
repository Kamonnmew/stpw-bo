from werkzeug.utils import secure_filename
import requests
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient, SearchIndexerClient
from azure.search.documents.models import (
    RawVectorQuery,
)
from azure.search.documents.indexes.models import (

    ExhaustiveKnnParameters,
    ExhaustiveKnnVectorSearchAlgorithmConfiguration,
    FieldMapping,
    HnswParameters,
    HnswVectorSearchAlgorithmConfiguration,
    InputFieldMappingEntry,
    OutputFieldMappingEntry,
    SimpleField,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SearchIndexer,
    SearchIndexerDataContainer,
    SearchIndexerDataSourceConnection,
    SearchIndexerSkillset,
    VectorSearch,
    VectorSearchAlgorithmKind,
    VectorSearchProfile,
    WebApiSkill
)
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import os
import logging
import time
from requests.exceptions import RequestException, Timeout, ConnectionError


class ImageSearchAPI:
    def __init__(self, indexName: str = None, topK: int = None):
        load_dotenv()
        self.topK = topK
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Azure Search configurations
        self.service_endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
        self.indexName = indexName
        self.search_key = os.getenv("AZURE_SEARCH_ADMIN_KEY")
        self.search_client = SearchClient(self.service_endpoint, self.indexName, AzureKeyCredential(self.search_key))

        # Azure AI Vision configurations
        self.aiVisionEndpoint = os.getenv("AZURE_AI_VISION_ENDPOINT")
        self.aiVisionApiKey = os.getenv("AZURE_AI_VISION_API_KEY")
        self.aiVisionModelVersion = os.getenv("AZURE_AI_VISION_MODEL_VERSION", "2024-02-01")

        # Blob storage configurations
        self.blob_connection_string = os.getenv("BLOB_CONNECTION_STRING")
        self.container_name = os.getenv("BLOB_CONTAINER_NAME")
        blob_service_client = BlobServiceClient.from_connection_string(self.blob_connection_string)
        self.container_client = blob_service_client.get_container_client(self.container_name)

    def generate_embeddings(self, image_url):
        # Remove trailing slash if exists
        endpoint = self.aiVisionEndpoint.rstrip('/')
        # Use the correct Azure AI Vision vectorize endpoint
        url = f"{endpoint}/computervision/retrieval:vectorizeImage"
        params = {
            "api-version": self.aiVisionModelVersion,
            "model-version": "2023-04-15"  # Use multilingual model
        }
        headers = {"Content-Type": "application/json", "Ocp-Apim-Subscription-Key": self.aiVisionApiKey}
        data = {"url": image_url}
        
        # Start timing for performance monitoring
        start_time = time.time()
        
        self.logger.info(f"Calling Azure AI Vision Vectorize API: {url}")
        self.logger.info(f"API Version: {self.aiVisionModelVersion}, Model Version: 2023-04-15")
        
        try:
            # Add timeout to prevent hanging
            response = requests.post(url, params=params, headers=headers, json=data, timeout=30)
            
            # Calculate response time
            response_time = time.time() - start_time
            self.logger.info(f"API Response Time: {response_time:.2f} seconds")
            
            self.logger.info(f"Response Status: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                if "vector" in response_data:
                    embeddings = response_data["vector"]
                    self.logger.info(f"Successfully generated embeddings with {len(embeddings)} dimensions")
                    return embeddings
                else:
                    self.logger.error("Error: No 'vector' field in response")
                    return None
            else:
                self.logger.error(f"API Error {response.status_code}: {response.text}")
                return None
                
        except Timeout:
            self.logger.error("Request timeout - Azure AI Vision API took too long to respond")
            return None
        except ConnectionError:
            self.logger.error("Connection error - Unable to connect to Azure AI Vision API")
            return None
        except RequestException as e:
            self.logger.error(f"Request failed: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error in generate_embeddings: {str(e)}")
            return None

    def search_with_embeddings(self, embeddings):
        try:
            start_time = time.time()
            
            vector_query = RawVectorQuery(vector=embeddings, k=self.topK, fields="imageVector")
            results = self.search_client.search(
                search_text=None, 
                vector_queries=[vector_query],
                select=["title", "imageUrl"]  # Remove @search.score from select
            )
            
            search_time = time.time() - start_time
            self.logger.info(f"Vector Search Time: {search_time:.2f} seconds")
            
            # Process results and get confidence scores
            processed_results = []
            for result in results:
                # Get confidence score from result object (not from select)
                confidence_score = result.get("@search.score", 0)
                
                result_with_confidence = {
                    "title": result.get("title"),
                    "imageUrl": result.get("imageUrl"),
                    "confidence_score": round(confidence_score, 4),
                    "similarity_percentage": round(confidence_score * 100, 2)
                }
                processed_results.append(result_with_confidence)
            
            self.logger.info(f"Found {len(processed_results)} results")
            return processed_results
            
        except Exception as e:
            self.logger.error(f"Error in search_with_embeddings: {str(e)}")
            return []

    def search_image_file(self, file_storage=None):
        # Save the file to a temporary location
        try:
            if not file_storage:
                self.logger.warning("No file provided for search")
                return None
                
            start_time = time.time()
            self.logger.info(f"Starting image search for file: {file_storage.filename}")
            
            filename = secure_filename(file_storage.filename)
            temp_dir = "/tmp"  # Update the directory path as needed
            os.makedirs(temp_dir, exist_ok=True)  # Ensure the directory exists

            temp_path = os.path.join(temp_dir, filename)
            file_storage.save(temp_path)

            with open(temp_path, "rb") as image_file:
                image_data = image_file.read()
                
            # Upload image to Blob Storage
            blob_name = os.path.basename(temp_path)
            blob_client = self.container_client.get_blob_client(blob_name)
            
            try:
                blob_client.upload_blob(image_data, overwrite=True, timeout=30)
                image_url = blob_client.url
                self.logger.info(f"Image uploaded to blob storage: {blob_name}")
            except Exception as e:
                self.logger.error(f"Failed to upload to blob storage: {str(e)}")
                return None

            # Generate embeddings and search
            embeddings = self.generate_embeddings(image_url)
            if embeddings:
                results = self.search_with_embeddings(embeddings)
                
                total_time = time.time() - start_time
                self.logger.info(f"Total search process time: {total_time:.2f} seconds")
                
                # Clean up temporary file
                try:
                    os.remove(temp_path)
                    self.logger.debug(f"Cleaned up temporary file: {temp_path}")
                except:
                    pass
                    
                return results
            else:
                self.logger.error("Failed to generate embeddings")
                return None
                
        except Exception as e:
            self.logger.error(f"An error occurred while processing the request: {str(e)}")
            return None
