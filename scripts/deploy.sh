#!/bin/bash

# Glory Bot Panel - Deployment Script

echo "🚀 Starting deployment of Glory Bot Panel..."

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install git first."
    exit 1
fi

# Create directory structure
echo "📁 Creating directory structure..."
mkdir -p glory-bot-panel/{frontend,backend,bot,database,scripts,config}

# Copy files (simulated - in real scenario, files would be copied)
echo "📋 Copying files..."

# Initialize git
echo "🔧 Initializing git repository..."
cd glory-bot-panel
git init
git add .
git commit -m "Initial commit - Glory Bot Panel"

# Instructions for GitHub
echo ""
echo "📢 GitHub Instructions:"
echo "1. Go to: https://github.com/new"
echo "2. Create repository named: glory-bot-panel"
echo "3. Run these commands:"
echo ""
echo "git remote add origin https://github.com/YOUR_USERNAME/glory-bot-panel.git"
echo "git branch -M main"
echo "git push -u origin main"
echo ""

# Instructions for Vercel
echo "📢 Vercel Instructions:"
echo "1. Go to: https://vercel.com/new"
echo "2. Import from GitHub"
echo "3. Select glory-bot-panel repository"
echo "4. Deploy!"

echo ""
echo "✅ Deployment script completed!"
echo "📞 For help, contact support"
