#!/bin/bash

echo "🚀 Phone-PC Sync Emulator Installation"
echo "======================================"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "✅ Python $PYTHON_VERSION detected"

# Create virtual environment if possible
if command -v python3 -m venv &> /dev/null; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "✅ Virtual environment created and activated"
else
    echo "⚠️  Virtual environment not available, using system Python"
fi

# Install dependencies
echo "📥 Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install some dependencies"
    echo "You may need to install them manually:"
    echo "  pip3 install PyQt6 requests cryptography json5 python-dateutil pillow qrcode"
fi

echo ""
echo "🎉 Installation completed!"
echo ""
echo "To run the application:"
echo "  python3 main.py"
echo ""
echo "To run the demo:"
echo "  python3 demo.py"
echo ""
echo "To run with launcher:"
echo "  python3 run.py"