#!/bin/bash
# Publishing Script for paegents Python SDK v2.0.0

echo "======================================================================"
echo "Publishing paegents v2.0.0 to PyPI"
echo "======================================================================"
echo ""

# Check if we're in the right directory
if [ ! -f "setup.py" ]; then
    echo "❌ Error: Must run from packages/agent-sdk/python directory"
    exit 1
fi

# Check if dist files exist
if [ ! -d "dist" ] || [ ! -f "dist/paegents-2.0.0.tar.gz" ]; then
    echo "❌ Error: Distribution files not found. Run 'python3 -m build' first"
    exit 1
fi

echo "📦 Package files ready:"
ls -lh dist/
echo ""

# Validate packages
echo "🔍 Validating packages..."
twine check dist/*
if [ $? -ne 0 ]; then
    echo "❌ Package validation failed"
    exit 1
fi
echo "✅ Packages validated"
echo ""

# Option 1: Upload with username/password prompt
echo "Choose authentication method:"
echo "  1) Username & Password (interactive)"
echo "  2) API Token (provide token as argument)"
echo "  3) Cancel"
read -p "Enter choice (1-3): " choice

case $choice in
    1)
        echo ""
        echo "🔐 You'll be prompted for PyPI username and password..."
        twine upload dist/*
        ;;
    2)
        read -p "Enter your PyPI API token: " token
        if [ -z "$token" ]; then
            echo "❌ No token provided"
            exit 1
        fi
        echo ""
        echo "📤 Uploading with API token..."
        twine upload -u __token__ -p "$token" dist/*
        ;;
    3)
        echo "Cancelled"
        exit 0
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

# Check upload status
if [ $? -eq 0 ]; then
    echo ""
    echo "======================================================================"
    echo "✅ SUCCESS! paegents v2.0.0 published to PyPI"
    echo "======================================================================"
    echo ""
    echo "📍 View at: https://pypi.org/project/paegents/2.0.0/"
    echo ""
    echo "📥 Users can now install with:"
    echo "   pip install paegents==2.0.0"
    echo ""
else
    echo ""
    echo "❌ Upload failed. Check errors above."
    exit 1
fi
