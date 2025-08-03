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


class ImageSearchAPI:
    def __init__(self, indexName: str = None, topK: int = None):
        load_dotenv()
        self.topK = topK
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
        url = f"{self.aiVisionEndpoint}/computervision/retrieval:vectorizeImage"
        params = {"api-version": self.aiVisionModelVersion}
        headers = {"Content-Type": "application/json", "Ocp-Apim-Subscription-Key": self.aiVisionApiKey}
        data = {"url": image_url}
        response = requests.post(url, params=params, headers=headers, json=data)
        if response.status_code == 200:
            embeddings = response.json()["vector"]
            return embeddings
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None

    def search_with_embeddings(self, embeddings):
        vector_query = RawVectorQuery(vector=embeddings, k=self.topK, fields="imageVector")
        results = self.search_client.search(search_text=None, vector_queries=[vector_query],
                                            select=["title", "imageUrl"])
        return results

    def search_image_file(self, file_storage=None):
        # Save the file to a temporary location
        try:
            if file_storage:
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
                blob_client.upload_blob(image_data, overwrite=True)
                image_url = blob_client.url

        # Generate embeddings and search
                embeddings = self.generate_embeddings(image_url)
                if embeddings:
                    results = self.search_with_embeddings(embeddings)
                    return results
                else:
                    return None
            else:
                return None
        except Exception as e:
            print(f"An error occurred while processing the request: {str(e)}")
            return None
