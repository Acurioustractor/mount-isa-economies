#!/bin/bash
# Mount Isa Economic Observatory - Environment Validation Script
# Validates that all required environment variables are properly set

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo ""
echo "================================================================================"
echo "🔍 ENVIRONMENT VALIDATION - Mount Isa Economic Observatory"
echo "================================================================================"
echo ""

cd "$PROJECT_DIR"

# Load environment variables
if [ ! -f .env ]; then
    echo "❌ ERROR: .env file not found"
    echo "   Run: ./scripts/setup-env.sh to create it"
    exit 1
fi

# Export variables from .env
set -a
source .env
set +a

echo "✅ Found .env file"
echo ""

# Check file permissions
PERMS=$(stat -c %a .env 2>/dev/null || stat -f %A .env 2>/dev/null)
if [ "$PERMS" != "600" ]; then
    echo "⚠️  WARNING: .env has insecure permissions ($PERMS)"
    echo "   Recommended: chmod 600 .env"
    echo ""
else
    echo "✅ Secure file permissions (600)"
    echo ""
fi

# Validation results
VALID=true
ERRORS=0
WARNINGS=0

echo "================================================================================"
echo "📋 REQUIRED CREDENTIALS (for data scraping)"
echo "================================================================================"
echo ""

# Required: ABN Lookup GUID
if [ -z "$ABN_LOOKUP_GUID" ] || [ "$ABN_LOOKUP_GUID" == "your_guid_here" ]; then
    echo "❌ ABN_LOOKUP_GUID: Not set"
    echo "   Required for: Business lookups, supplier enrichment"
    echo "   Get from: https://abr.business.gov.au/Tools/WebServices"
    ERRORS=$((ERRORS+1))
    VALID=false
else
    echo "✅ ABN_LOOKUP_GUID: Set ($ABN_LOOKUP_GUID)"
fi

echo ""

echo "================================================================================"
echo "📋 OPTIONAL CREDENTIALS (for AI chat features)"
echo "================================================================================"
echo ""

# Optional: Supabase
if [ -z "$SUPABASE_URL" ] || [ "$SUPABASE_URL" == "your_supabase_project_url_here" ]; then
    echo "⚠️  SUPABASE_URL: Not set"
    echo "   Required for: AI chat interface (scripts/chat_with_data.py)"
    WARNINGS=$((WARNINGS+1))
else
    echo "✅ SUPABASE_URL: Set (${SUPABASE_URL:0:30}...)"
fi

if [ -z "$SUPABASE_SERVICE_ROLE_KEY" ] || [ "$SUPABASE_SERVICE_ROLE_KEY" == "your_supabase_service_role_key_here" ]; then
    echo "⚠️  SUPABASE_SERVICE_ROLE_KEY: Not set"
    echo "   Required for: AI chat interface"
    WARNINGS=$((WARNINGS+1))
else
    echo "✅ SUPABASE_SERVICE_ROLE_KEY: Set (${SUPABASE_SERVICE_ROLE_KEY:0:20}...)"
fi

# Optional: OpenAI
if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" == "your_openai_api_key_here" ]; then
    echo "⚠️  OPENAI_API_KEY: Not set"
    echo "   Required for: AI chat interface (scripts/chat_with_data.py)"
    WARNINGS=$((WARNINGS+1))
else
    echo "✅ OPENAI_API_KEY: Set (${OPENAI_API_KEY:0:15}...)"
fi

echo ""

# Optional: Database
echo "================================================================================"
echo "📋 DATABASE CONFIGURATION (optional - for local PostgreSQL)"
echo "================================================================================"
echo ""

if [ "$DB_PASSWORD" == "your_password_here" ]; then
    echo "⚠️  DB_PASSWORD: Using default placeholder"
    echo "   Set this if using local PostgreSQL instead of Supabase"
else
    echo "✅ DB_PASSWORD: Set"
fi

echo ""

# Summary
echo "================================================================================"
echo "📊 VALIDATION SUMMARY"
echo "================================================================================"
echo ""

if [ "$VALID" = true ]; then
    echo "✅ All required credentials are configured"
    echo ""
    echo "🚀 You can now run:"
    echo "   • python3 scrapers/comprehensive_money_flow_scraper.py"
    echo "   • python3 scrapers/abn_lookup_professional.py"
    echo "   • All data collection scripts"
else
    echo "❌ ERRORS: $ERRORS required credentials missing"
    echo ""
    echo "🔧 Fix by:"
    echo "   1. Edit .env with your actual credentials"
    echo "   2. See API_KEYS_GUIDE.md for instructions"
    echo "   3. Run this script again to validate"
fi

if [ "$WARNINGS" -gt 0 ]; then
    echo ""
    echo "⚠️  WARNINGS: $WARNINGS optional credentials not set"
    echo ""
    echo "   These are only needed for AI chat features."
    echo "   All data scraping works without them."
    echo ""
    echo "   To enable AI chat:"
    echo "   • Set SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, OPENAI_API_KEY"
    echo "   • See API_KEYS_GUIDE.md for instructions"
fi

echo ""
echo "================================================================================"
echo ""

# Exit with appropriate code
if [ "$VALID" = false ]; then
    exit 1
fi

exit 0
