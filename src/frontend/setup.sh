#!/bin/bash

# Hotel Frontend Quick Start Script
# Run this to get everything set up quickly!

echo "🏨 Hotel Reservations Frontend - Quick Setup"
echo "=========================================="
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install from https://nodejs.org/"
    exit 1
fi

echo "✅ Node.js found: $(node --version)"
echo ""

# Navigate to frontend directory
cd "$(dirname "$0")" || exit
echo "📁 Current directory: $(pwd)"
echo ""

# Check if package.json exists
if [ ! -f "package.json" ]; then
    echo "❌ package.json not found!"
    exit 1
fi

echo "📦 Installing dependencies..."
npm install

if [ $? -ne 0 ]; then
    echo "❌ Installation failed!"
    exit 1
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "🚀 Starting development server..."
echo ""
echo "The app will open at http://localhost:3000"
echo ""
echo "Demo credentials:"
echo "  👤 Client  : client1 / password123"
echo "  👨‍💼 Staff   : staff1 / password123"
echo "  🔐 Admin   : admin / password123"
echo ""
echo "Make sure Django backend is running at http://localhost:8000"
echo ""

npm start
