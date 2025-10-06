#!/bin/bash

# Newsletter API v4 - Deploy to GitHub Script

echo "🚀 Newsletter API v4 - GitHub Deployment"
echo "========================================"

# Check if we're in the right directory
if [ ! -f "app_v4/api.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📦 Initializing git repository..."
    git init
fi

# Add all files
echo "📁 Adding files to git..."
git add .

# Commit changes
echo "💾 Committing v4 platform..."
git commit -m "Add Newsletter API v4 - Complete platform with video support

Features:
- 5 main API endpoints (home, top-stories, 4 themes)
- YouTube video integration and scoring
- RSS, Google, and web scraping data collection
- Flexible, configurable scoring system
- Modern responsive web interface
- Background workers for data processing
- Production-ready Render deployment config

Ready for deployment to Render with API keys!"

echo ""
echo "✅ Code committed successfully!"
echo ""
echo "🔗 Next steps:"
echo "1. Create a new repository on GitHub (if you haven't already)"
echo "2. Add your GitHub repository as remote:"
echo "   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git"
echo "3. Push to GitHub:"
echo "   git push -u origin main"
echo ""
echo "📖 Then follow the DEPLOYMENT_GUIDE.md for Render deployment instructions"
echo ""
echo "🎯 Your v4 platform includes:"
echo "   • Complete API with video support"
echo "   • Flexible scoring system"
echo "   • Modern web interface"
echo "   • Background workers"
echo "   • Render deployment configuration"
