#!/bin/bash
# Mount Isa Economic Observatory - Environment Setup Script
# World-class environment variable management
# Run this once to set up your local environment

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo ""
echo "================================================================================"
echo "🔐 MOUNT ISA ECONOMIC OBSERVATORY - ENVIRONMENT SETUP"
echo "================================================================================"
echo ""

cd "$PROJECT_DIR"

# Check if .env exists
if [ -f .env ]; then
    echo "✅ .env file exists"
    echo ""
    read -p "⚠️  Do you want to overwrite it? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Cancelled - keeping existing .env"
        echo ""
        echo "To update specific values, edit .env directly or use .env.local for overrides"
        exit 0
    fi
fi

# Copy from example
if [ ! -f .env.example ]; then
    echo "❌ ERROR: .env.example not found"
    exit 1
fi

cp .env.example .env
echo "✅ Created .env from .env.example"
echo ""

# Set file permissions (owner read/write only)
chmod 600 .env
echo "✅ Set secure permissions (600) on .env"
echo ""

# Display what needs to be configured
echo "📝 CONFIGURATION REQUIRED"
echo "================================================================================"
echo ""
echo "Your .env file has been created with placeholder values."
echo "You need to add your actual credentials:"
echo ""
echo "✅ CONFIRMED - Already set:"
echo "   • ABN_LOOKUP_GUID (e3df2bb0-a40b-40f9-b771-0cef7e9d667b)"
echo ""
echo "❓ OPTIONAL - Find or create if you want AI features:"
echo "   • SUPABASE_URL (from https://app.supabase.com/)"
echo "   • SUPABASE_SERVICE_ROLE_KEY"
echo "   • OPENAI_API_KEY (from https://platform.openai.com/)"
echo ""
echo "📖 For detailed instructions, see: API_KEYS_GUIDE.md"
echo ""

# Open editor
if command -v nano &> /dev/null; then
    read -p "Open .env in editor now? (Y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        nano .env
    fi
elif command -v vim &> /dev/null; then
    read -p "Open .env in vim now? (Y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        vim .env
    fi
else
    echo "💡 Edit your .env file with: nano .env"
fi

echo ""
echo "================================================================================"
echo "✅ SETUP COMPLETE"
echo "================================================================================"
echo ""
echo "Next steps:"
echo "  1. Edit .env with your actual credentials (see API_KEYS_GUIDE.md)"
echo "  2. Run: ./scripts/validate-env.sh to check your configuration"
echo "  3. Optional: Install direnv for auto-loading (https://direnv.net/)"
echo ""
