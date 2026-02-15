#!/bin/bash

# BMO Assistant - Quick Fix Script
# Fixes missing files and restarts services

echo "🔧 BMO Quick Fix"
echo "================"
echo ""

# Stop any running services
echo "Stopping services..."
docker-compose down

# Create missing files if needed
echo "Checking files..."

# Create .env if missing
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "OLLAMA_MODEL=llama3.2:1b" >> .env
fi

echo ""
echo "✅ Files ready!"
echo ""

# Restart services
echo "Starting services..."
docker-compose up -d --build

echo ""
echo "⏳ Waiting for services to start..."
sleep 10

echo ""
echo "🎮 BMO Assistant Status"
echo "======================="
echo ""

# Check if services are running
if docker ps | grep -q bmo-ollama; then
    echo "✅ Ollama: Running"
else
    echo "❌ Ollama: Not running"
fi

if docker ps | grep -q bmo-ai; then
    echo "✅ AI Service: Running"
else
    echo "❌ AI Service: Not running"
fi

if docker ps | grep -q bmo-gateway; then
    echo "✅ Gateway: Running"
else
    echo "❌ Gateway: Not running"
fi

if docker ps | grep -q bmo-web; then
    echo "✅ Web: Running"
else
    echo "❌ Web: Not running"
fi

echo ""
echo "📥 Download AI Model"
echo "===================="
echo ""
echo "Choose a model:"
echo "1. llama3.2:1b  (RECOMMENDED - Fast & Good)"
echo "2. qwen2.5:0.5b (Ultra Fast)"
echo "3. phi3:mini    (Best Quality)"
echo ""
read -p "Enter choice (1-3): " choice

case $choice in
    1)
        MODEL="llama3.2:1b"
        ;;
    2)
        MODEL="qwen2.5:0.5b"
        ;;
    3)
        MODEL="phi3:mini"
        ;;
    *)
        MODEL="llama3.2:1b"
        ;;
esac

echo ""
echo "Downloading $MODEL..."
docker exec -it bmo-ollama ollama pull $MODEL

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Model downloaded!"
    
    # Update .env
    if grep -q "OLLAMA_MODEL=" .env; then
        sed -i "s/OLLAMA_MODEL=.*/OLLAMA_MODEL=$MODEL/" .env
    else
        echo "OLLAMA_MODEL=$MODEL" >> .env
    fi
    
    # Restart AI service
    docker-compose restart ai-service
    echo "✅ AI service restarted"
else
    echo ""
    echo "❌ Model download failed"
fi

echo ""
echo "================================"
echo "🎉 BMO is Ready!"
echo "================================"
echo ""
echo "Access BMO:"
echo "  • Web: http://localhost:3000"
echo "  • API: http://localhost:8000"
echo ""
echo "View logs:"
echo "  docker-compose logs -f"
echo ""
