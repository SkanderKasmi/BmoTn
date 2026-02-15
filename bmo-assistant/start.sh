#!/bin/bash

# BMO Assistant - Quick Start Script
# This script helps you set up and deploy BMO Assistant quickly

set -e

echo "🎮 Welcome to BMO Assistant Setup!"
echo "=================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker is not installed!${NC}"
        echo "Please install Docker first: https://docs.docker.com/get-docker/"
        exit 1
    fi
    echo -e "${GREEN}✓ Docker is installed${NC}"
}

# Check if Docker Compose is installed
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}❌ Docker Compose is not installed!${NC}"
        echo "Please install Docker Compose first: https://docs.docker.com/compose/install/"
        exit 1
    fi
    echo -e "${GREEN}✓ Docker Compose is installed${NC}"
}

# Setup environment file
setup_env() {
    if [ ! -f .env ]; then
        echo -e "${YELLOW}Setting up environment file...${NC}"
        cp .env.example .env
        
        echo ""
        echo -e "${GREEN}✓ No API keys needed! Ollama is 100% FREE${NC}"
        echo ""
    else
        echo -e "${GREEN}✓ Environment file exists${NC}"
    fi
}

# Check for Google Cloud credentials
check_google_credentials() {
    if [ ! -f credentials.json ]; then
        echo -e "${YELLOW}⚠️  Google Cloud credentials not found${NC}"
        echo "Voice features require Google Cloud credentials."
        echo "Get them from: https://console.cloud.google.com/"
        echo ""
        echo -e "${YELLOW}Note: BMO will work fine without voice - just no speech recognition${NC}"
        echo ""
        read -p "Continue without voice features? (Y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]] && [[ ! -z $REPLY ]]; then
            echo "Please add credentials.json and run again"
            exit 1
        fi
    else
        echo -e "${GREEN}✓ Google Cloud credentials found${NC}"
    fi
}

# Build and start services
start_services() {
    echo ""
    echo -e "${YELLOW}Building and starting services...${NC}"
    echo "This may take a few minutes on first run..."
    echo ""
    
    docker-compose up -d --build
    
    if [ $? -eq 0 ]; then
        echo ""
        echo -e "${GREEN}✓ Services started successfully!${NC}"
    else
        echo -e "${RED}❌ Failed to start services${NC}"
        exit 1
    fi
}

# Wait for services to be ready
wait_for_services() {
    echo ""
    echo -e "${YELLOW}Waiting for services to be ready...${NC}"
    
    max_attempts=30
    attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Services are ready!${NC}"
            return 0
        fi
        
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo ""
    echo -e "${RED}❌ Services did not start in time${NC}"
    echo "Check logs with: docker-compose logs"
    exit 1
}

# Download Ollama model
download_ollama_model() {
    echo ""
    echo -e "${YELLOW}Ollama Model Setup${NC}"
    echo "=================="
    echo ""
    echo "Choose your model (affects speed and quality):"
    echo "1. llama3.2:1b  - FASTEST (Recommended) [1.3 GB]"
    echo "2. qwen2.5:0.5b - ULTRA FAST [400 MB]"
    echo "3. phi3:mini    - BEST QUALITY [2.3 GB]"
    echo "4. Skip (model already downloaded)"
    echo ""
    read -p "Enter choice (1-4): " model_choice
    
    case $model_choice in
        1)
            MODEL="llama3.2:1b"
            ;;
        2)
            MODEL="qwen2.5:0.5b"
            ;;
        3)
            MODEL="phi3:mini"
            ;;
        4)
            echo -e "${GREEN}Skipping model download${NC}"
            return 0
            ;;
        *)
            echo -e "${YELLOW}Invalid choice, using default: llama3.2:1b${NC}"
            MODEL="llama3.2:1b"
            ;;
    esac
    
    echo ""
    echo -e "${YELLOW}Downloading $MODEL...${NC}"
    echo "This may take 1-5 minutes depending on your internet speed..."
    echo ""
    
    docker exec -it bmo-ollama ollama pull $MODEL
    
    if [ $? -eq 0 ]; then
        echo ""
        echo -e "${GREEN}✓ Model downloaded successfully!${NC}"
        
        # Update .env with chosen model
        if grep -q "OLLAMA_MODEL=" .env; then
            sed -i "s/OLLAMA_MODEL=.*/OLLAMA_MODEL=$MODEL/" .env
        else
            echo "OLLAMA_MODEL=$MODEL" >> .env
        fi
        
        # Restart AI service to pick up new model
        echo ""
        echo -e "${YELLOW}Restarting AI service...${NC}"
        docker-compose restart ai-service
        sleep 3
        
        echo -e "${GREEN}✓ AI service restarted with $MODEL${NC}"
    else
        echo -e "${RED}❌ Failed to download model${NC}"
        echo "You can download it later with:"
        echo "  docker exec -it bmo-ollama ollama pull $MODEL"
    fi
}

# Show success message
show_success() {
    echo ""
    echo "=================================="
    echo -e "${GREEN}🎉 BMO Assistant is ready!${NC}"
    echo "=================================="
    echo ""
    echo "Access points:"
    echo "  • Web Interface:  http://localhost:3000"
    echo "  • API Gateway:    http://localhost:8000"
    echo "  • Health Check:   http://localhost:8000/health"
    echo ""
    echo "💰 Total Cost: $0.00 (FREE with Ollama!)"
    echo ""
    echo "Useful commands:"
    echo "  • View logs:      docker-compose logs -f"
    echo "  • Stop services:  docker-compose down"
    echo "  • Restart:        docker-compose restart"
    echo "  • List models:    docker exec -it bmo-ollama ollama list"
    echo ""
    echo "Next steps:"
    echo "1. Open http://localhost:3000 in your browser"
    echo "2. Enter your parent's name"
    echo "3. Start chatting with BMO!"
    echo ""
    echo "📚 Documentation:"
    echo "  • Model guide:     OLLAMA_SETUP.md"
    echo "  • Android APK:     frontend/mobile/ANDROID_BUILD.md"
    echo "  • Full guide:      SETUP_GUIDE.md"
    echo ""
}

# Main execution
main() {
    clear
    echo "🎮 BMO Assistant Setup"
    echo "======================"
    echo ""
    
    # Run checks
    check_docker
    check_docker_compose
    echo ""
    
    # Setup
    setup_env
    check_google_credentials
    
    # Deploy
    start_services
    wait_for_services
    download_ollama_model
    
    # Success
    show_success
}

# Run main function
main
