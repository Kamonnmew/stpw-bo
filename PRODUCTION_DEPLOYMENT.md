# Production Deployment Guide

## 🚀 Azure Production Environment Setup

### 1. Create Azure App Service
```bash
# Create Azure App Service for production
az webapp create \
  --resource-group YOUR_RESOURCE_GROUP \
  --plan YOUR_APP_SERVICE_PLAN \
  --name image-search-auto-prod \
  --runtime "PYTHON|3.11"
```

### 2. Configure Environment Variables in Azure
In Azure Portal > App Service > Configuration > Application Settings, add:

```
AZURE_SEARCH_SERVICE_ENDPOINT=https://your-production-search.search.windows.net
AZURE_SEARCH_ADMIN_KEY=your_production_search_key
AZURE_OPENAI_ENDPOINT=https://your-production-openai.openai.azure.com/
AZURE_OPENAI_API_KEY=your_production_openai_key
AZURE_OPENAI_API_VERSION=2024-06-01
AZURE_OPENAI_EMBEDDING_DEPLOYED_MODEL=text-embedding-ada-002
AZURE_AI_VISION_API_KEY=your_production_vision_key
AZURE_AI_VISION_ENDPOINT=https://your-production-vision.cognitiveservices.azure.com/
AZURE_AI_VISION_MODEL_VERSION=2024-02-01
BLOB_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=your_production_storage;AccountKey=your_production_storage_key;EndpointSuffix=core.windows.net
BLOB_CONTAINER_NAME=production-file-storage
COGNITIVE_SERVICES_ENDPOINT=https://your-production-cognitive.cognitiveservices.azure.com/
COGNITIVE_SERVICES_API_KEY=your_production_cognitive_key
FUNCTION_CUSTOM_SKILL_ENDPOINT=https://your-production-function.azurewebsites.net/api/getimageembeddings?code=your_function_key
```

### 3. Setup GitHub Deployment
1. In Azure Portal > App Service > Deployment Center
2. Download Publish Profile
3. Add to GitHub Secrets as: `AZUREAPPSERVICE_PUBLISHPROFILE_PROD`

### 4. Deploy
```bash
# Trigger deployment by pushing to production branch
git push origin production

# Or trigger manually in GitHub Actions
```

### 5. Verify Deployment
- Health check: https://image-search-auto-prod.azurewebsites.net/health
- API test: https://image-search-auto-prod.azurewebsites.net/home

## 🔒 Security Notes
- Environment variables are stored securely in Azure App Service
- No secrets are committed to git repository
- Production configuration is managed separately from development
