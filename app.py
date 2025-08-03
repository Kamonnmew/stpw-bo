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
        "BLOB_CONNECTION_STRING": "***" if os.getenv("BLOB_CONNECTION_STRING") else "NOT_SET",
        "BLOB_CONTAINER_NAME": os.getenv("BLOB_CONTAINER_NAME", "NOT_SET"),
        "AZURE_AI_VISION_ENDPOINT": os.getenv("AZURE_AI_VISION_ENDPOINT", "NOT_SET"),
    }
    return env_vars, HTTP_200_OK


@app.route('/home', methods=['GET'])
def home():
    return "This is a SQL Search API", HTTP_200_OK


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
        for file in files:
            try:
                filename = 'https://filestoragepath.blob.core.windows.net/file-test-storage/' + str(
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
                    if indexName == "product-pro-type-code-part" or indexName == "product-pro-type-code-used" or \
                            indexName == "product-pro-type-code-packaging":
                        product_type = str(result['title']).split("-")[0]
                        product_code = str(result['title']).split("-")[1]
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
                        # Change the pattern for other_index
                        model_cars = str(result['title']).split("-")[0]
                        formatted_result = {
                            "modelName": indexName,
                            "originalFile": filename,
                            "modelCars": model_cars,
                            "similarFile": result['imageUrl'],
                            "similarity_percentage": result.get('similarity_percentage', 0)
                        }
                        formatted_results.append(formatted_result)
                    elif indexName == "product-carmodel-type-code-used":
                        # Change the pattern for other_index
                        model_cars = str(result['title']).split(".")[0]
                        product_type = str(result['title']).split(".")[1]
                        product_code = str(result['title']).split(".")[2]
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

                formatted_results_all.append(formatted_results)

            except KeyError:
                # Handle missing file or indexName
                return jsonify({"error": "Missing file or indexName parameter"}), 400

            except Exception as e:
                # Handle other exceptions for individual files
                error_message = "An error occurred while processing file {}: {}".format(file.filename, str(e))
                formatted_results_all.append({"error": error_message})

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
