#!/usr/bin/env bash
# Setup script for PE Predictor backend
set -e

echo "=== PE Predictor Backend Setup ==="

# 1. Create virtualenv
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Created virtual environment"
fi
source venv/bin/activate

# 2. Install dependencies
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "✓ Python dependencies installed"

# 3. Download DejaVu fonts (Cyrillic support for PDF)
mkdir -p assets/fonts
FONT_URL="https://github.com/dejavu-fonts/dejavu-fonts/releases/download/version_2_37/dejavu-fonts-ttf-2.37.zip"
if [ ! -f "assets/fonts/DejaVuSans.ttf" ]; then
    echo "Downloading DejaVu fonts..."
    curl -sL "$FONT_URL" -o /tmp/dejavu.zip
    unzip -j -q /tmp/dejavu.zip "*/DejaVuSans.ttf" "*/DejaVuSans-Bold.ttf" -d assets/fonts/
    rm /tmp/dejavu.zip
    echo "✓ Fonts downloaded"
else
    echo "✓ Fonts already present"
fi

# 4. Train XGBoost model on synthetic data
if [ ! -f "assets/pe_model.pkl" ]; then
    echo "Training XGBoost model on synthetic data..."
    python scripts/train_model.py
else
    echo "✓ ML model already exists"
fi

# 5. Initialize database
python -c "
from app import create_app
app = create_app()
print('✓ Database initialized')
"

echo ""
echo "=== Setup complete ==="
echo "Run the server:  venv/bin/python app.py"
echo "API base URL:    http://localhost:8000/api"
echo "Note: port 5000 is taken by macOS AirPlay. Server runs on 8000."
