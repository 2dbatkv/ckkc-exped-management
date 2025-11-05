#!/bin/bash
# CKKC Expedition Management System - Deployment Script

set -e  # Exit on error

echo "🏔️ CKKC Expedition Management System - Deployment Script"
echo "=========================================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✓ Docker and Docker Compose are installed"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from template..."
    cp .env.example .env

    # Generate a random Flask secret key
    if command -v python3 &> /dev/null; then
        SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
        sed -i "s/changeme_generate_a_random_secret_key_here/$SECRET_KEY/" .env
        echo "✓ Generated Flask secret key"
    fi

    # Generate a random PostgreSQL password
    PG_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
    sed -i "s/changeme_in_production/$PG_PASSWORD/g" .env
    echo "✓ Generated PostgreSQL password"

    echo ""
    echo "⚠️  IMPORTANT: Review and update .env file with your settings!"
    echo "   Especially: ADMIN_PASSCODE"
    echo ""
    read -p "Press Enter to continue or Ctrl+C to exit and edit .env first..."
fi

echo "✓ Configuration file (.env) exists"
echo ""

# Check if we're updating or doing fresh install
if docker ps -a | grep -q ckkc_web; then
    echo "📦 Existing deployment detected. This will update the application."
    echo ""
    read -p "Continue with update? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Deployment cancelled."
        exit 0
    fi

    echo ""
    echo "🔄 Stopping existing containers..."
    docker-compose down

    echo "🔨 Rebuilding containers..."
    docker-compose build --no-cache

    echo "🚀 Starting updated services..."
    docker-compose up -d
else
    echo "📦 Fresh installation detected."
    echo ""

    echo "🔨 Building containers..."
    docker-compose build

    echo "🚀 Starting services..."
    docker-compose up -d
fi

echo ""
echo "⏳ Waiting for services to become healthy..."

# Wait for database
echo -n "   Waiting for database"
for i in {1..30}; do
    if docker-compose exec -T db pg_isready -U ckkc_user -d expedition_db &> /dev/null; then
        echo " ✓"
        break
    fi
    echo -n "."
    sleep 2
done

# Wait for web application
echo -n "   Waiting for web application"
for i in {1..30}; do
    if curl -s http://localhost:5001/ > /dev/null 2>&1; then
        echo " ✓"
        break
    fi
    echo -n "."
    sleep 2
done

echo ""
echo "=========================================================="
echo "✅ Deployment Complete!"
echo "=========================================================="
echo ""
echo "📍 Application URL: http://localhost:5001"
echo "🔐 Admin Dashboard: http://localhost:5001/admin"
echo "👤 Admin Passcode: Check your .env file"
echo ""
echo "📊 Service Status:"
docker-compose ps
echo ""
echo "📝 View logs:"
echo "   docker-compose logs -f web"
echo ""
echo "🛑 Stop services:"
echo "   docker-compose down"
echo ""
echo "🔄 Update application:"
echo "   git pull && ./deploy.sh"
echo ""
echo "💾 Backup database:"
echo "   docker-compose exec db pg_dump -U ckkc_user expedition_db > backup.sql"
echo ""
echo "=========================================================="
