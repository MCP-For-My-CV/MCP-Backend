# Deployment Fixes for Render

We've made several changes to fix the deployment issues on Render:

## 1. Memory Optimization

- Added `OPENAI_EMBEDDINGS_ONLY=true` environment variable
- Modified `models.py` to skip loading HuggingFace and Ollama models when this is set
- This significantly reduces memory usage, as HuggingFace models were causing the "Out of memory" error

## 2. Port Configuration

- Updated Dockerfile to use port 10000 instead of 8000
- Set `PORT=10000` in both Dockerfile and render.yaml
- Expose port 10000 in the Dockerfile

## 3. Render Configuration

- Created render.yaml for Blueprint deployments
- Added proper health check path
- Configured environment variables

## 4. Error Handling

- Improved error handling in rag_core.py for missing embedding models
- Added better error messages and graceful fallbacks

## Redeployment Instructions

1. Push these changes to your GitHub repository
2. On Render dashboard, you can either:
   - Manually trigger a redeploy of your existing service
   - Create a new service using the Blueprint option (recommended)

3. When creating a new service, make sure to:
   - Set `OPENAI_API_KEY` to your OpenAI API key
   - Set `OPENAI_EMBEDDINGS_ONLY` to `true`
   - Set `PORT` to `10000`

4. Monitor the logs during deployment to ensure everything is working correctly

## Testing Locally Before Deploying

You can test these changes locally to verify they work:

```bash
# Set environment variables
$env:OPENAI_EMBEDDINGS_ONLY="true"
$env:PORT="10000"

# Run the REST API server
python rest_api.py
```

This will simulate the Render environment locally.

## Troubleshooting

If you continue to experience issues:
- Check the Render logs for specific error messages
- Consider upgrading to a paid plan with more memory if needed
- Ensure your OpenAI API key has sufficient quota
