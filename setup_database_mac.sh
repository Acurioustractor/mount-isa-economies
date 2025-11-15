#!/bin/bash
# PostgreSQL Setup Script for Mac
# Sets up unified Mount Isa database with both service map and economic observatory

echo "=================================================="
echo "Mount Isa Platform - Database Setup (Mac)"
echo "=================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if PostgreSQL is installed
echo "Checking for PostgreSQL..."
if command -v psql &> /dev/null; then
    echo -e "${GREEN}✓ PostgreSQL is installed${NC}"
    psql --version
else
    echo -e "${YELLOW}⚠ PostgreSQL not found. Installing...${NC}"
    echo "Running: brew install postgresql@14 postgis"
    brew install postgresql@14 postgis

    # Start PostgreSQL service
    echo "Starting PostgreSQL service..."
    brew services start postgresql@14

    # Wait for PostgreSQL to start
    echo "Waiting for PostgreSQL to start..."
    sleep 5
fi

# Check if PostGIS is available
echo ""
echo "Checking for PostGIS..."
if brew list postgis &> /dev/null; then
    echo -e "${GREEN}✓ PostGIS is installed${NC}"
else
    echo -e "${YELLOW}Installing PostGIS...${NC}"
    brew install postgis
fi

# Create database
echo ""
echo "Creating database: mount_isa_platform"

# Drop if exists (optional - comment out in production)
# psql postgres -c "DROP DATABASE IF EXISTS mount_isa_platform;"

# Create database
if psql postgres -c "CREATE DATABASE mount_isa_platform;" 2>/dev/null; then
    echo -e "${GREEN}✓ Database created${NC}"
else
    echo -e "${YELLOW}⚠ Database already exists (this is OK)${NC}"
fi

# Enable PostGIS extension
echo ""
echo "Enabling PostGIS extension..."
psql mount_isa_platform -c "CREATE EXTENSION IF NOT EXISTS postgis;" &>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ PostGIS enabled${NC}"
else
    echo -e "${RED}✗ Could not enable PostGIS${NC}"
fi

# Load Economic Observatory schema
echo ""
echo "Loading Economic Observatory schema..."
if [ -f "mount-isa-observatory/models/schema.sql" ]; then
    psql mount_isa_platform -f mount-isa-observatory/models/schema.sql
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Economic Observatory schema loaded${NC}"
    else
        echo -e "${RED}✗ Error loading schema${NC}"
    fi
else
    echo -e "${RED}✗ Schema file not found${NC}"
    echo "Expected: mount-isa-observatory/models/schema.sql"
fi

# Create service map integration tables
echo ""
echo "Creating service map integration tables..."

psql mount_isa_platform << 'EOF'

-- Service Providers Table (from service map)
CREATE TABLE IF NOT EXISTS service_providers (
    provider_id SERIAL PRIMARY KEY,
    provider_name VARCHAR(500) NOT NULL,
    service_type VARCHAR(200),
    service_category VARCHAR(200),
    location VARCHAR(500),
    postcode VARCHAR(10),
    phone VARCHAR(50),
    email VARCHAR(200),
    website VARCHAR(500),
    abn VARCHAR(11),
    description TEXT,
    is_indigenous_owned BOOLEAN DEFAULT FALSE,
    is_local BOOLEAN,
    source VARCHAR(100), -- 'service_map', 'ndis', 'healthdirect', etc.
    confidence_score DECIMAL(3,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_provider_abn ON service_providers(abn);
CREATE INDEX idx_provider_category ON service_providers(service_category);
CREATE INDEX idx_provider_local ON service_providers(is_local);

-- Community Interviews Table
CREATE TABLE IF NOT EXISTS community_interviews (
    interview_id SERIAL PRIMARY KEY,
    interview_date DATE,
    respondent_type VARCHAR(100), -- 'resident', 'elder', 'business_owner', etc.
    service_gaps TEXT[], -- Array of identified gaps
    positive_feedback TEXT,
    concerns TEXT,
    suggestions TEXT,
    sentiment_score DECIMAL(3,2), -- -1 to 1
    ai_analysis JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Service-Economic Flow Link Table
CREATE TABLE IF NOT EXISTS service_economic_links (
    link_id SERIAL PRIMARY KEY,
    provider_id INTEGER REFERENCES service_providers(provider_id),
    entity_id INTEGER REFERENCES entities(entity_id),
    service_category VARCHAR(200),
    anzsic_code VARCHAR(10),
    program_type VARCHAR(50), -- 'MBS', 'PBS', 'NDIS', etc.
    annual_funding DECIMAL(15,2),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Community Investment Opportunities Table
CREATE TABLE IF NOT EXISTS investment_opportunities (
    opportunity_id SERIAL PRIMARY KEY,
    opportunity_title VARCHAR(500) NOT NULL,
    service_category VARCHAR(200),
    gap_identified_from VARCHAR(100), -- 'community_interview', 'economic_analysis', 'service_map'
    current_leakage DECIMAL(15,2), -- Annual $ leaking externally
    local_provider_count INTEGER,
    estimated_investment_needed DECIMAL(15,2),
    estimated_jobs_created INTEGER,
    estimated_local_retention DECIMAL(15,2),
    priority_score DECIMAL(5,2),
    status VARCHAR(50) DEFAULT 'identified', -- 'identified', 'under_review', 'funded', 'active'
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Service Categories Mapping
CREATE TABLE IF NOT EXISTS service_category_mapping (
    mapping_id SERIAL PRIMARY KEY,
    service_category VARCHAR(200) NOT NULL,
    anzsic_code VARCHAR(10),
    anzsic_title VARCHAR(500),
    program_types TEXT[], -- ['MBS', 'PBS', 'NDIS']
    notes TEXT
);

-- Insert common mappings
INSERT INTO service_category_mapping (service_category, anzsic_code, anzsic_title, program_types) VALUES
    ('Health Services', '8511', 'General Practice Medical Services', ARRAY['MBS', 'PBS']),
    ('Allied Health', '8512', 'Specialist Medical Services', ARRAY['MBS']),
    ('Disability Services', '8790', 'Other Social Assistance Services', ARRAY['NDIS', 'DSS']),
    ('Mental Health', '8512', 'Specialist Medical Services', ARRAY['MBS']),
    ('Aged Care', '8600', 'Aged Care Services', ARRAY['MBS', 'DSS']),
    ('Child Care', '8710', 'Child Care Services', ARRAY['DSS']),
    ('Legal Services', '6931', 'Legal Services', NULL),
    ('Housing Services', '8790', 'Other Social Assistance Services', ARRAY['DSS'])
ON CONFLICT DO NOTHING;

EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Service map integration tables created${NC}"
else
    echo -e "${RED}✗ Error creating integration tables${NC}"
fi

# Check database status
echo ""
echo "=================================================="
echo "Database Setup Summary"
echo "=================================================="
echo ""

echo "Database name: mount_isa_platform"
echo "Connection string: postgresql://localhost/mount_isa_platform"
echo ""

echo "Tables created:"
psql mount_isa_platform -c "\dt" | grep -E "(entities|service_providers|fact_economic_flows|community_interviews|investment_opportunities)"

echo ""
echo "=================================================="
echo -e "${GREEN}✓ Setup Complete!${NC}"
echo "=================================================="
echo ""
echo "Next steps:"
echo "1. Update your .env file:"
echo "   DB_HOST=localhost"
echo "   DB_PORT=5432"
echo "   DB_NAME=mount_isa_platform"
echo "   DB_USER=$(whoami)"
echo "   DB_PASSWORD="
echo ""
echo "2. Test connection:"
echo "   psql mount_isa_platform -c 'SELECT COUNT(*) FROM entities;'"
echo ""
echo "3. Import your service map data:"
echo "   python import_service_map_data.py"
echo ""
