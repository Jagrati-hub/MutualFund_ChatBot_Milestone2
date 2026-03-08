#!/bin/bash
# Quick start script for running the Groww Mutual Fund FAQ Assistant locally

echo "=========================================="
echo "Groww Mutual Fund FAQ Assistant"
echo "Local Setup & Run"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python --version
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install -r phases/phase-0-foundation/requirements.txt -q
echo "✓ Dependencies installed"
echo ""

# Verify .env file
echo "Verifying .env configuration..."
if [ -f "phases/phase-0-foundation/.env" ]; then
    echo "✓ .env file found"
    echo "  - GEMINI_API_KEY_1: $(grep GEMINI_API_KEY_1 phases/phase-0-foundation/.env | cut -d'=' -f2 | cut -c1-20)..."
    echo "  - GEMINI_API_KEY_2: $(grep GEMINI_API_KEY_2 phases/phase-0-foundation/.env | cut -d'=' -f2 | cut -c1-20)..."
    echo "  - GEMINI_API_KEY_3: $(grep GEMINI_API_KEY_3 phases/phase-0-foundation/.env | cut -d'=' -f2 | cut -c1-20)..."
    echo "  - GROQ_API_KEY: $(grep GROQ_API_KEY phases/phase-0-foundation/.env | cut -d'=' -f2 | cut -c1-20)..."
else
    echo "✗ .env file not found!"
    exit 1
fi
echo ""

# Run tests
echo "Running tests..."
python -m pytest testing/test_category_query_consistency.py -v --tb=short -q
if [ $? -eq 0 ]; then
    echo "✓ All tests passed"
else
    echo "✗ Tests failed"
    exit 1
fi
echo ""

# Start the app
echo "=========================================="
echo "Starting Streamlit app..."
echo "=========================================="
echo ""
echo "The app will open at: http://localhost:8501"
echo "Press Ctrl+C to stop the server"
echo ""

streamlit run phases/phase-5-frontend/app.py
