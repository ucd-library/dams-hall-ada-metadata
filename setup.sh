#!/bin/bash

echo "Setting up Photo Album Collection Template..."
echo "=========================================="

# Check if Python 3 is available
if command -v python3 &> /dev/null; then
    echo "✓ Python 3 found"
else
    echo "✗ Python 3 not found. Please install Python 3.7+"
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "Setup complete! Next steps:"
echo "1. Update metadata.csv with your collection info"
echo "2. Place TIFF files in images/ folder"
echo "3. Run: python3 create_directory_structure.py"
echo "4. Run: python3 create_metadata.py"
echo "5. Run: python3 mint_collection_ark.py"
echo "6. Run: python3 mint_single_ark.py"
echo ""
echo "To activate the virtual environment in the future:"
echo "source venv/bin/activate"
