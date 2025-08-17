from concurrent.futures import ThreadPoolExecutor
from werkzeug.utils import secure_filename
from flask import Flask, jsonify, request
from flask_cors import CORS
from http_status_codes import HTTP_200_OK
from ImageSearch import ImageSearchAPI
import os

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not available in production

app = Flask(__name__)
CORS(app)
executor = ThreadPoolExecutor()


@app.route('/health', methods=['GET'])
def health_check():
    return {"status": "healthy", "message": "API is running"}, HTTP_200_OK


@app.route('/debug/env', methods=['GET'])
def debug_env():
    import os
    env_vars = {
        "AZURE_SEARCH_SERVICE_ENDPOINT": os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT", "NOT_SET"),
        "AZURE_SEARCH_ADMIN_KEY": "***" if os.getenv("AZURE_SEARCH_ADMIN_KEY") else "NOT_SET",
        "BLOB_CONNECTION_STRING": os.getenv("BLOB_CONNECTION_STRING", "NOT_SET")[:50] + "..." if os.getenv("BLOB_CONNECTION_STRING") else "NOT_SET",
        "BLOB_CONTAINER_NAME": os.getenv("BLOB_CONTAINER_NAME", "NOT_SET"),
        "AZURE_AI_VISION_ENDPOINT": os.getenv("AZURE_AI_VISION_ENDPOINT", "NOT_SET"),
        "AZURE_AI_VISION_API_KEY": "***" if os.getenv("AZURE_AI_VISION_API_KEY") else "NOT_SET",
    }
    return env_vars, HTTP_200_OK


@app.route('/home', methods=['GET'])
def home():
    return "This is a SQL Search API", HTTP_200_OK


@app.route('/debug/storage-url', methods=['GET'])
def debug_storage_url():
    """Debug storage URL generation"""
    try:
        connection_string = os.getenv("BLOB_CONNECTION_STRING", "")
        container_name = os.getenv("BLOB_CONTAINER_NAME", "file-test-storage")
        
        # Extract storage account name from connection string
        storage_account = "filestoragepath"  # default
        if "AccountName=" in connection_string:
            try:
                storage_account = connection_string.split("AccountName=")[1].split(";")[0]
            except:
                pass
        
        sample_url = f'https://{storage_account}.blob.core.windows.net/{container_name}/sample.jpg'
        
        return {
            "storage_account": storage_account,
            "container_name": container_name,
            "sample_url": sample_url,
            "connection_string_has_account": "AccountName=" in connection_string
        }, HTTP_200_OK
        
    except Exception as e:
        return {"error": f"Debug failed: {str(e)}"}, 500


@app.route('/debug/search-direct', methods=['GET'])
def debug_search_direct():
    """Debug Azure Search Service directly"""
    try:
        from azure.search.documents import SearchClient
        from azure.core.credentials import AzureKeyCredential
        
        # Get Azure Search configuration
        endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
        key = os.getenv("AZURE_SEARCH_ADMIN_KEY")
        index_name = "product-type-code-part"
        
        # Create search client
        search_client = SearchClient(endpoint, index_name, AzureKeyCredential(key))
        
        # Try to search for everything
        results = search_client.search("*", top=5)
        
        # Convert results to list
        result_list = []
        for result in results:
            result_dict = {}
            for key, value in result.items():
                if key.startswith('@'):
                    continue  # Skip metadata
                result_dict[key] = str(value)
            result_list.append(result_dict)
        
        return {
            "status": "success",
            "endpoint": endpoint,
            "index": index_name,
            "result_count": len(result_list),
            "results": result_list[:2]  # Show first 2 results
        }, HTTP_200_OK
        
    except Exception as e:
        import traceback
        return {
            "error": f"Direct search failed: {str(e)}",
            "traceback": traceback.format_exc()
        }, 500


@app.route('/debug/ai-vision-test', methods=['GET'])
def debug_ai_vision_test():
    """Test Azure AI Vision with a sample image URL"""
    try:
        from ImageSearch import ImageSearchAPI
        
        # Use a simple public image for testing
        sample_image_url = "https://via.placeholder.com/300x200.jpg"
        
        # Initialize ImageSearchAPI
        api = ImageSearchAPI(indexName="product-type-code-part", topK=3)
        
        # Test embedding generation
        embeddings = api.generate_embeddings(sample_image_url)
        
        return {
            "status": "success",
            "image_url": sample_image_url,
            "embeddings_generated": embeddings is not None,
            "embeddings_length": len(embeddings) if embeddings else 0,
            "ai_vision_endpoint": os.getenv("AZURE_AI_VISION_ENDPOINT"),
            "sample_embeddings": embeddings[:3] if embeddings else None
        }, HTTP_200_OK
        
    except Exception as e:
        import traceback
        return {
            "error": f"AI Vision test failed: {str(e)}",
            "traceback": traceback.format_exc()
        }, 500


@app.route('/test/blob', methods=['GET'])
def test_blob_connection():
    """Test blob connection without ImageSearchAPI"""
    try:
        import os
        from azure.storage.blob import BlobServiceClient
        
        connection_string = os.getenv("BLOB_CONNECTION_STRING")
        container_name = os.getenv("BLOB_CONTAINER_NAME")
        
        if not connection_string:
            return {"error": "BLOB_CONNECTION_STRING not set"}, 400
            
        if "AccountName=" not in connection_string:
            return {"error": "Connection string missing AccountName"}, 400
            
        if "AccountKey=" not in connection_string:
            return {"error": "Connection string missing AccountKey"}, 400
        
        # Test connection
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service_client.get_container_client(container_name)
        
        # Try to list blobs (compatible with older versions)
        try:
            blob_list = container_client.list_blobs()
            blobs = list(blob_list)[:5]  # Get first 5 manually
        except Exception as list_error:
            # If listing fails, just try to get container properties
            try:
                container_client.get_container_properties()
                blobs = []  # Container exists but can't list blobs
            except Exception as prop_error:
                raise Exception(f"Container access failed: {str(prop_error)}")
        
        return {
            "status": "success",
            "container": container_name,
            "blob_count": len(blobs),
            "connection_string_format": "valid"
        }, HTTP_200_OK
        
    except Exception as e:
        return {"error": f"Blob connection test failed: {str(e)}"}, 500


@app.route('/test/search-init', methods=['GET'])
def test_search_init():
    """Test ImageSearchAPI initialization"""
    try:
        from ImageSearch import ImageSearchAPI
        
        # Try to initialize with real index name
        api = ImageSearchAPI(indexName="product-type-code-part", topK=5)
        
        return {
            "status": "success",
            "message": "ImageSearchAPI initialized successfully",
            "index": "product-type-code-part"
        }, HTTP_200_OK
        
    except Exception as e:
        return {"error": f"ImageSearchAPI initialization failed: {str(e)}"}, 500


@app.route('/search', methods=['POST'])
def search():
    try:
        indexName = request.form.get('indexName')

        topK_str = request.form.get('topK')
        if topK_str is not None and topK_str.isdigit():
            topK = int(topK_str)
        else:
            return jsonify({"error": "Invalid topK parameter. It must be a valid integer."}), 400
            
        files = request.files.getlist('files')  # Get list of files
        image_search_api = ImageSearchAPI(indexName=indexName, topK=topK)
        formatted_results_all = []
        
        # Get storage account name from environment
        connection_string = os.getenv("BLOB_CONNECTION_STRING", "")
        container_name = os.getenv("BLOB_CONTAINER_NAME", "file-test-storage")
        
        # Extract storage account name from connection string
        storage_account = "filestoragepath"  # default
        if "AccountName=" in connection_string:
            try:
                storage_account = connection_string.split("AccountName=")[1].split(";")[0]
            except:
                pass
        
        for file in files:
            try:
                filename = f'https://{storage_account}.blob.core.windows.net/{container_name}/' + str(
                    secure_filename(file.filename))
                with ThreadPoolExecutor() as executor:
                    future = executor.submit(image_search_api.search_image_file, file)
                    results = future.result()

                # Check if results is None (failed to get embeddings or search)
                if results is None:
                    formatted_results_all.append({"error": f"Failed to process file {file.filename}: No results returned"})
                    continue

                # Format search results for each file
                formatted_results = []
                for result in results:
                    if indexName == "product-type-code-part" or indexName == "product-type-code-used" or \
                            indexName == "product-type-code-packaging" or indexName == "product-pro-type-code-part" or \
                            indexName == "product-pro-type-code-used" or indexName == "product-pro-type-code-packaging":
                        # Handle both dev and production index naming patterns
                        title_parts = str(result['title']).split("-")
                        
                        # Ensure we have at least 2 parts, otherwise use defaults
                        product_type = title_parts[0] if len(title_parts) > 0 else "Unknown"
                        product_code = title_parts[1] if len(title_parts) > 1 else "Unknown"
                        
                        formatted_result = {
                            "modelName": indexName,
                            "originalFile": filename,
                            "productType": product_type,
                            "productCode": product_code,
                            "similarFile": result['imageUrl'],
                            "confidence_score": result.get('confidence_score', 0),
                            "similarity_percentage": result.get('similarity_percentage', 0)
                        }
                        formatted_results.append(formatted_result)
                    elif indexName == "product-carmodelclean":
                        # Handle car model clean index
                        title_parts = str(result['title']).split("-")
                        model_cars = title_parts[0] if len(title_parts) > 0 else "Unknown"
                        
                        formatted_result = {
                            "modelName": indexName,
                            "originalFile": filename,
                            "modelCars": model_cars,
                            "similarFile": result['imageUrl'],
                            "similarity_percentage": result.get('similarity_percentage', 0)
                        }
                        formatted_results.append(formatted_result)
                    elif indexName == "product-carmodel-type-code-used":
                        # Handle car model type code used index with dot separator
                        title_parts = str(result['title']).split(".")
                        
                        # Ensure we have at least 3 parts, otherwise use defaults
                        model_cars = title_parts[0] if len(title_parts) > 0 else "Unknown"
                        product_type = title_parts[1] if len(title_parts) > 1 else "Unknown"  
                        product_code = title_parts[2] if len(title_parts) > 2 else "Unknown"
                        
                        formatted_result = {
                            "modelName": indexName,
                            "originalFile": filename,
                            "modelCars": model_cars,
                            "productType": product_type,
                            "productCode": product_code,
                            "similarFile": result['imageUrl'],
                            "similarity_percentage": result.get('similarity_percentage', 0)
                        }
                        formatted_results.append(formatted_result)
                    else:
                        # Default handler for unknown index patterns
                        formatted_result = {
                            "modelName": indexName,
                            "originalFile": filename,
                            "title": str(result.get('title', 'Unknown')),
                            "similarFile": result['imageUrl'],
                            "similarity_percentage": result.get('similarity_percentage', 0),
                            "confidence_score": result.get('confidence_score', 0),
                            "note": "Using default format - unknown index pattern"
                        }
                        formatted_results.append(formatted_result)

                formatted_results_all.append(formatted_results)

            except KeyError:
                # Handle missing file or indexName
                return jsonify({"error": "Missing file or indexName parameter"}), 400

            except Exception as e:
                # Handle other exceptions for individual files with detailed logging
                import traceback
                error_details = {
                    "error": f"ML service error: An error occurred while processing file {file.filename}: {str(e)}",
                    "file": file.filename,
                    "index": indexName,
                    "error_type": type(e).__name__,
                    "traceback": traceback.format_exc()
                }
                
                # Log the error for debugging
                print(f"ERROR processing {file.filename}: {error_details}")
                
                formatted_results_all.append(error_details)

        return jsonify(formatted_results_all)

    except KeyError:
        # Handle missing indexName or topK
        return jsonify({"error": "Missing indexName or topK parameter"}), 400

    except Exception as e:
        # Handle other exceptions for the entire request
        error_message = "An error occurred while processing the request: {}".format(str(e))
        return jsonify({"error": error_message}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
