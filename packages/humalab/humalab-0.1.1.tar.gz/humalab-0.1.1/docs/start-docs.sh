#!/bin/bash

# HumaLab SDK Documentation Startup Script

echo "Starting HumaLab SDK Documentation..."
echo ""

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    echo ""
fi

# Start development server
echo "🚀 Starting development server..."
echo "📖 Documentation will be available at: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

npm run dev
