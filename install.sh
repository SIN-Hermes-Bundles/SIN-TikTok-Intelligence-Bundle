#!/bin/bash
# SIN-TikTok-Intelligence-Bundle Installer
# One-command setup for TikTok Shop Intelligence

set -euo pipefail

REPO_URL="https://github.com/SIN-Hermes-Bundles/SIN-TikTok-Intelligence-Bundle"
INSTALL_DIR="$HOME/.hermes/bundles/tiktok-intelligence"

echo "=== SIN TikTok Intelligence Bundle Installer ==="

# 1. Create directories
mkdir -p "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR/config"
mkdir -p "$INSTALL_DIR/reports"

# 2. Clone or update
if [ -d "$INSTALL_DIR/.git" ]; then
    echo "Updating existing installation..."
    cd "$INSTALL_DIR"
    git pull origin main
else
    echo "Cloning repository..."
    git clone --depth 1 "$REPO_URL" "$INSTALL_DIR"
fi

# 3. Install dependencies
echo "Installing Python dependencies..."
cd "$INSTALL_DIR"
pip3 install -r requirements.txt

# 4. Setup config templates
echo "Setting up config templates..."
cp config/simptok.json "$INSTALL_DIR/config/simptok.json" 2>/dev/null || true
cp config/echotik.json "$INSTALL_DIR/config/echotik.json" 2>/dev/null || true

# 5. Verify
echo "Verifying installation..."
python3 -c "
from src.clients.simptok_client import SimpTokClient
from src.clients.echotik_client import EchoTikClient
from src.clients.scrapling_fallback import ScraplingFallback
from src.fusion.trend_engine import TrendEngine
from src.fusion.report_generator import ReportGenerator
print('All imports OK')
" || echo "Warning: Some imports failed"

# 6. Install skills
SKILL_DIR="$HOME/.hermes/skills/survey"
mkdir -p "$SKILL_DIR"
cp -r skills/* "$SKILL_DIR/" 2>/dev/null || true

echo ""
echo "=== Installation Complete ==="
echo "Location: $INSTALL_DIR"
echo ""
echo "Next steps:"
echo "1. Add API keys to config:"
echo "   $INSTALL_DIR/config/simptok.json"
echo "   $INSTALL_DIR/config/echotik.json"
echo ""
echo "2. Get free API keys:"
echo "   - SimpTok: https://simptok.com (no credit card)"
echo "   - EchoTik: https://echotik.live (free plan)"
echo ""
echo "3. Run your first report:"
echo "   cd $INSTALL_DIR && python3 -m src.cli --action weekly-report --format summary"
echo ""
echo "4. Use Hermes Skills:"
echo "   - 'finde tiktok trends'"
echo "   - 'recherchiere produkt'"
echo "   - 'competitor grid'"
