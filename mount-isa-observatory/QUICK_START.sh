#!/bin/bash
# Mount Isa Economic Observatory - QUICK START
# Run this script to set up EVERYTHING

set -e  # Exit on error

echo "=============================================================="
echo "🏛️  MOUNT ISA ECONOMIC OBSERVATORY - QUICK START"
echo "     Justice-Centered Economic Intelligence"
echo "=============================================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print section headers
section() {
    echo ""
    echo -e "${BLUE}▶ $1${NC}"
    echo "--------------------------------------------------------------"
}

# Function to print success
success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function to print warning
warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "QUICK_START.sh" ]; then
    echo "Error: Please run this from mount-isa-observatory directory"
    exit 1
fi

# ============================================================
# 1. Install PostgreSQL (if needed)
# ============================================================
section "1. Database Setup"

if command -v psql &> /dev/null; then
    success "PostgreSQL already installed"
    psql --version
else
    warning "PostgreSQL not found. Installing..."

    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        brew install postgresql@14 postgis
        brew services start postgresql@14
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        sudo apt-get update
        sudo apt-get install -y postgresql postgresql-contrib postgis
        sudo systemctl start postgresql
    fi

    success "PostgreSQL installed"
fi

# ============================================================
# 2. Create Database
# ============================================================
section "2. Creating Database"

DB_NAME="mount_isa_platform"

# Drop if exists (optional - comment out in production)
dropdb $DB_NAME 2>/dev/null || true

# Create fresh database
createdb $DB_NAME
success "Database '$DB_NAME' created"

# Load schema
echo "Loading schema..."
psql $DB_NAME -f database/schema_v2_scalable.sql &>/dev/null
success "Schema loaded successfully"

# Verify tables
TABLE_COUNT=$(psql $DB_NAME -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';")
success "Created $TABLE_COUNT tables"

# ============================================================
# 3. Install Python Dependencies
# ============================================================
section "3. Python Dependencies"

echo "Installing core dependencies..."
python3 -m pip install -r requirements-core.txt --quiet
success "Core dependencies installed"

echo "Installing additional packages..."
python3 -m pip install schedule beautifulsoup4 lxml --quiet
success "Additional packages installed"

# ============================================================
# 4. Configure Environment
# ============================================================
section "4. Configuration"

if [ ! -f ".env" ]; then
    cp .env.example .env
    success ".env file created"

    # Auto-configure database settings
    sed -i.bak "s/DB_NAME=.*/DB_NAME=$DB_NAME/" .env
    sed -i.bak "s/DB_USER=.*/DB_USER=$(whoami)/" .env
    sed -i.bak "s/DB_PASSWORD=.*/DB_PASSWORD=/" .env
    rm .env.bak

    warning "Remember to add your ABN_LOOKUP_GUID to .env when you receive it"
else
    success ".env file already exists"
fi

# ============================================================
# 5. Run Initial Data Fetch
# ============================================================
section "5. Initial Data Ingestion"

echo "Fetching sample data..."
python3 ingestion/qld_gov/fetch_procurement_direct.py
success "Sample procurement data fetched"

echo "Testing ingestion..."
python3 test_ingestion.py
success "Test ingestion complete"

# ============================================================
# 6. Open Dashboard
# ============================================================
section "6. Launching Dashboard"

# Start a simple HTTP server for the map
echo "Starting web server for interactive map..."
echo ""
echo -e "${GREEN}🌐 Dashboard will open in your browser at:${NC}"
echo -e "${GREEN}   http://localhost:8000/visualization/map_dashboard.html${NC}"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Open browser
if [[ "$OSTYPE" == "darwin"* ]]; then
    open "http://localhost:8000/visualization/map_dashboard.html" &
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    xdg-open "http://localhost:8000/visualization/map_dashboard.html" &
fi

# Start server
python3 -m http.server 8000

# ============================================================
# DONE
# ============================================================
