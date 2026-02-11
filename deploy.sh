#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${BLUE}🏦 Cymball Bank - Servicio al Cliente IA - Cloud Run Deployment${NC}"
echo "================================================"

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${RED}❌ Error: .env file not found!${NC}"
    echo "Please create a .env file with your GOOGLE_API_KEY"
    exit 1
fi

# Load environment variables from .env file
echo -e "${YELLOW}📄 Loading environment variables from .env...${NC}"
export $(cat .env | grep -v '^#' | grep -v '^$' | xargs)

# Validate required environment variables
if [ -z "$GOOGLE_API_KEY" ] && [ -z "$GOOGLE_GENAI_USE_VERTEXAI" ]; then
    echo -e "${RED}❌ Error: GOOGLE_API_KEY or GOOGLE_GENAI_USE_VERTEXAI not found in .env file!${NC}"
    echo "Please add your API configuration to the .env file"
    exit 1
fi

# Build environment variables string for Cloud Run (read all from .env)
# Using a more robust approach that handles special characters
ENV_VARS=""
echo -e "${YELLOW}   Reading environment variables:${NC}"
while IFS= read -r line || [[ -n "$line" ]]; do
    # Skip empty lines and comments
    if [[ -n "$line" && ! "$line" =~ ^[[:space:]]*# ]]; then
        # Extract key (everything before first =)
        key="${line%%=*}"
        # Extract value (everything after first =)
        value="${line#*=}"
        # Remove surrounding quotes if present
        value="${value%\"}"
        value="${value#\"}"
        value="${value%\'}"
        value="${value#\'}"
        if [[ -n "$key" && -n "$value" ]]; then
            echo -e "${BLUE}   - $key${NC}"
            if [[ -z "$ENV_VARS" ]]; then
                ENV_VARS="${key}=${value}"
            else
                ENV_VARS="${ENV_VARS},${key}=${value}"
            fi
        fi
    fi
done < .env

echo ""
echo -e "${GREEN}✅ Environment variables loaded successfully${NC}"
if [ ! -z "$GOOGLE_API_KEY" ]; then
    echo -e "${BLUE}   API Key: ${GOOGLE_API_KEY:0:8}...${GOOGLE_API_KEY: -8}${NC}"
fi
if [ ! -z "$GOOGLE_GENAI_USE_VERTEXAI" ]; then
    echo -e "${BLUE}   Using Vertex AI: $GOOGLE_GENAI_USE_VERTEXAI${NC}"
fi
if [ ! -z "$GOOGLE_CLOUD_PROJECT" ]; then
    echo -e "${BLUE}   GCP Project: $GOOGLE_CLOUD_PROJECT${NC}"
fi
if [ ! -z "$GOOGLE_CLOUD_LOCATION" ]; then
    echo -e "${BLUE}   GCP Location: $GOOGLE_CLOUD_LOCATION${NC}"
fi

# Check if gcloud is installed and authenticated
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ Error: gcloud CLI not found!${NC}"
    echo "Please install Google Cloud CLI: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if user is authenticated
ACTIVE_ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -n 1)
if [ -z "$ACTIVE_ACCOUNT" ]; then
    echo -e "${YELLOW}🔐 Please authenticate with Google Cloud...${NC}"
    gcloud auth login
    ACTIVE_ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -n 1)
fi

echo -e "${GREEN}✅ Authenticated as: $ACTIVE_ACCOUNT${NC}"

# Set project (prompt user if needed)
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT_ID" ]; then
    echo -e "${YELLOW}📝 No default project set. Please set your project ID:${NC}"
    read -p "Enter your Google Cloud Project ID: " PROJECT_ID
    gcloud config set project $PROJECT_ID
fi

echo -e "${GREEN}📦 Project: $PROJECT_ID${NC}"

# Enable required APIs
echo -e "${YELLOW}🔧 Enabling required APIs...${NC}"
gcloud services enable run.googleapis.com cloudbuild.googleapis.com --quiet

# Verify Vertex AI requirements if using Vertex AI
if [ ! -z "$GOOGLE_GENAI_USE_VERTEXAI" ] && [ "$GOOGLE_GENAI_USE_VERTEXAI" == "true" ]; then
    if [ -z "$GOOGLE_CLOUD_PROJECT" ]; then
        echo -e "${RED}❌ Error: GOOGLE_CLOUD_PROJECT is required when using Vertex AI!${NC}"
        exit 1
    fi
    if [ -z "$GOOGLE_CLOUD_LOCATION" ]; then
        echo -e "${YELLOW}⚠️ Warning: GOOGLE_CLOUD_LOCATION not set, defaulting to us-central1${NC}"
    fi
fi

# Debug: Show ENV_VARS being passed (with values masked)
echo -e "${YELLOW}📋 Environment variables to be passed to Cloud Run:${NC}"
echo "$ENV_VARS" | tr ',' '\n' | while read -r pair; do
    key="${pair%%=*}"
    echo -e "${BLUE}   ✓ $key${NC}"
done
echo ""

# Deploy to Cloud Run
echo -e "${BLUE}🚀 Deploying Cymball Bank Agent to Cloud Run...${NC}"
echo -e "${BLUE}   Region: us-central1${NC}"
echo -e "${BLUE}   Service: cymball-agent${NC}"
echo -e "${BLUE}   Memory: 2Gi${NC}"
echo -e "${BLUE}   CPU: 2${NC}"
echo ""

gcloud run deploy cymball-agent \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "$ENV_VARS" \
  --set-build-env-vars GOOGLE_BUILD_NO_CACHE=true \
  --memory 2Gi \
  --cpu 2 \
  --timeout 3600 \
  --max-instances 10 \
  --port 8080 \
  --quiet

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${PURPLE}🎉 Deployment successful!${NC}"
    echo "================================================"
    echo -e "${BLUE}Your Cymball Bank Agent is now available at:${NC}"
    SERVICE_URL=$(gcloud run services describe cymball-agent --region us-central1 --format="value(status.url)")
    echo -e "${BLUE}🔗 $SERVICE_URL${NC}"
    echo ""
    echo -e "${YELLOW}📱 Features available:${NC}"
    echo "   • Real-time text chat in Spanish"
    echo "   • Voice interaction with Leda voice"
    echo "   • 4 Customer Scenarios:"
    echo "       📞 Collections (Early delinquency)"
    echo "       🎁 Benefits (Points & Deferred Payment)"
    echo "       🔓 Security (Travel unblock)"
    echo "       🔒 Claims (Unrecognized charges)"
    echo "   • Cymball Bank blue-themed UI"
    echo "   • Real-time tool call visibility"
    echo ""
    echo -e "${BLUE}💡 You can now share this URL with others!${NC}"
else
    echo -e "${RED}❌ Deployment failed!${NC}"
    echo "Please check the error messages above and try again."
    exit 1
fi
