#!/bin/bash

# Define colors for better readability (Good for ADHD focus)
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting SRE Practice: Blog API Test Set${NC}"
echo "--------------------------------------------"

# Use localhost:5000 for both Codespace and Docker tests
API_URL="http://127.0.0.1:5000"

echo -e "${GREEN}1. Health Check (Verifying Database & App Readiness):${NC}"
curl -s $API_URL/health | python3 -m json.tool
echo "--------------------------------------------"

echo -e "${GREEN}2. API Info (Root Route Check):${NC}"
curl -s $API_URL/ | python3 -m json.tool
echo "--------------------------------------------"

echo -e "${GREEN}3. Create Post (Testing Write to Persistent Volume):${NC}"
curl -s -X POST $API_URL/posts \
  -H "Content-Type: application/json" \
  -d '{"title":"SRE Persistence Test","content":"Verifying that blog.db saves to the Docker volume."}' \
  | python3 -m json.tool
echo "--------------------------------------------"

echo -e "${GREEN}4. Get All Posts (Verifying Data Retrieval):${NC}"
curl -s $API_URL/posts | python3 -m json.tool
echo "--------------------------------------------"

echo -e "${BLUE}✅ Practice Set Completed!${NC}"