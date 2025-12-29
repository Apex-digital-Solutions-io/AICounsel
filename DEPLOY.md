# Deploying AI Counsel to Google Cloud Run

This guide covers deploying AI Counsel to Google Cloud Run.

## Prerequisites

1. [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) installed
2. A Google Cloud project with billing enabled
3. Docker installed (for local testing)
4. Your Anthropic API key

## Quick Deploy

### Option 1: Using gcloud CLI (Recommended)

```bash
# Set your project
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable run.googleapis.com containerregistry.googleapis.com cloudbuild.googleapis.com secretmanager.googleapis.com

# Store your API key in Secret Manager
echo -n "your-anthropic-api-key" | gcloud secrets create anthropic-api-key --data-file=-

# Grant Cloud Run access to the secret
gcloud secrets add-iam-policy-binding anthropic-api-key \
  --member="serviceAccount:YOUR_PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# Build and deploy
gcloud run deploy ai-counsel \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-secrets="ANTHROPIC_API_KEY=anthropic-api-key:latest" \
  --memory 1Gi \
  --cpu 1 \
  --timeout 300 \
  --min-instances 0 \
  --max-instances 10
```

### Option 2: Using Cloud Build

```bash
# Set your project
gcloud config set project YOUR_PROJECT_ID

# Store your API key in Secret Manager first (see above)

# Submit the build
gcloud builds submit \
  --config cloudbuild.yaml \
  --substitutions=_REGION=us-central1,_ANTHROPIC_API_KEY=projects/YOUR_PROJECT_ID/secrets/anthropic-api-key/versions/latest
```

### Option 3: Manual Docker Build

```bash
# Build the image
docker build -t gcr.io/YOUR_PROJECT_ID/ai-counsel .

# Push to Container Registry
docker push gcr.io/YOUR_PROJECT_ID/ai-counsel

# Deploy to Cloud Run
gcloud run deploy ai-counsel \
  --image gcr.io/YOUR_PROJECT_ID/ai-counsel \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --set-secrets="ANTHROPIC_API_KEY=anthropic-api-key:latest" \
  --memory 1Gi
```

## Configuration Options

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key | Yes |
| `PORT` | Server port (auto-set by Cloud Run) | No |
| `DEFAULT_LEAD_MODEL` | Model for orchestrator (default: claude-sonnet-4-20250514) | No |
| `DEFAULT_AGENT_MODEL` | Model for agents (default: claude-sonnet-4-20250514) | No |

### Resource Recommendations

| Workload | CPU | Memory | Max Instances |
|----------|-----|--------|---------------|
| Light (personal use) | 1 | 512Mi | 3 |
| Medium (team use) | 1 | 1Gi | 10 |
| Heavy (production) | 2 | 2Gi | 50 |

## Using Secret Manager (Recommended)

Never hardcode your API key. Use Secret Manager:

```bash
# Create the secret
echo -n "sk-ant-xxxxx" | gcloud secrets create anthropic-api-key --data-file=-

# Update an existing secret
echo -n "sk-ant-new-key" | gcloud secrets versions add anthropic-api-key --data-file=-

# Deploy with secret
gcloud run deploy ai-counsel \
  --set-secrets="ANTHROPIC_API_KEY=anthropic-api-key:latest" \
  ...
```

## Custom Domain

To use a custom domain:

```bash
# Map your domain
gcloud run domain-mappings create \
  --service ai-counsel \
  --domain counsel.yourdomain.com \
  --region us-central1

# Follow the DNS verification instructions
```

## Monitoring

View logs:
```bash
gcloud run logs read ai-counsel --region us-central1
```

Stream logs:
```bash
gcloud run logs tail ai-counsel --region us-central1
```

## Local Testing

Test the Docker image locally before deploying:

```bash
# Build
docker build -t ai-counsel .

# Run
docker run -p 8080:8080 -e ANTHROPIC_API_KEY=your-key ai-counsel

# Test
curl http://localhost:8080/health
```

## Troubleshooting

### Container fails to start
- Check logs: `gcloud run logs read ai-counsel`
- Verify API key is set correctly
- Ensure sufficient memory (at least 512Mi)

### WebSocket connection issues
- Cloud Run supports WebSockets natively
- Ensure timeout is set high enough (300s recommended)
- Check that `--cpu-throttling=false` if using CPU-intensive operations

### Cold start latency
- Set `--min-instances 1` for always-warm instances
- Enable startup CPU boost: already configured in service.yaml

## Costs

Cloud Run pricing is based on:
- CPU and memory allocation while handling requests
- Number of requests
- Networking (egress)

With `min-instances: 0`, you only pay when the service is handling requests.

Estimate: ~$5-20/month for light personal use.
