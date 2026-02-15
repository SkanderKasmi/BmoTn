#!/bin/bash
# BMO Enhanced Backend Deployment Script

echo "🤖 BMO Enhanced Backend Deployment"
echo "===================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "${BLUE}[1/5] Checking prerequisites...${NC}"

if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is required but not installed"
    exit 1
fi
echo -e "${GREEN}✓ Python3 found${NC}"

if ! command -v docker &> /dev/null; then
    echo "⚠️  Docker not found - installing/containers may fail"
fi
echo -e "${GREEN}✓ Checking docker...${NC}"

# Install AI Service
echo ""
echo -e "${BLUE}[2/5] Setting up AI Service...${NC}"
cd services/ai-service

if pip install -q -r requirements.txt; then
    echo -e "${GREEN}✓ AI Service dependencies installed${NC}"
else
    echo "❌ Failed to install AI Service dependencies"
    exit 1
fi

# Install Voice Service
echo ""
echo -e "${BLUE}[3/5] Setting up Voice Service...${NC}"
cd ../voice-service

if pip install -q -r requirements.txt; then
    echo -e "${GREEN}✓ Voice Service dependencies installed${NC}"
else
    echo "❌ Failed to install Voice Service dependencies"
    exit 1
fi

# Install Gateway
echo ""
echo -e "${BLUE}[4/5] Setting up Gateway...${NC}"
cd ../gateway

if pip install -q -r requirements.txt; then
    echo -e "${GREEN}✓ Gateway dependencies installed${NC}"
else
    echo "❌ Failed to install Gateway dependencies"
    exit 1
fi

# Docker Compose Check
echo ""
echo -e "${BLUE}[5/5] Checking Docker Compose...${NC}"

if [ -f "../../docker-compose.yml" ]; then
    echo -e "${GREEN}✓ docker-compose.yml found${NC}"
    echo ""
    echo -e "${YELLOW}To start all services:${NC}"
    echo "  cd /workspaces/BmoTn"
    echo "  docker-compose up -d"
    echo ""
    echo -e "${YELLOW}To check service health:${NC}"
    echo "  curl http://localhost:8000/health"
else
    echo "⚠️  docker-compose.yml not found in root directory"
fi

echo ""
echo -e "${GREEN}===================================="
echo "Setup Complete! 🎉"
echo "====================================${NC}"
echo ""
echo -e "${YELLOW}Documentation:${NC}"
echo "  • Backend: /BACKEND_ENHANCEMENT.md"
echo "  • Frontend Integration: /FRONTEND_INTEGRATION.md"
echo ""
echo -e "${YELLOW}Quick Start:${NC}"
echo "  1. Start services: docker-compose up -d"
echo "  2. Check health: curl http://localhost:8000/health"
echo "  3. Test chat: curl -X POST http://localhost:8000/ai/chat -H 'Content-Type: application/json' -d '{\"message\":\"أشنوة؟\",\"session_id\":\"test\"}'"
echo ""
