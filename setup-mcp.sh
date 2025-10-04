#!/bin/bash
# Setup script for Render MCP connection

echo "🚀 Setting up Render MCP connection..."

# Install the Render MCP server
echo "📦 Installing Render MCP server..."
npm install -g @modelcontextprotocol/server-render

# Set up environment variables
export RENDER_API_KEY="rnd_AqV4VpcJlQvkKTR4dpSsCtKbASiT"

# Test the connection
echo "🔍 Testing Render API connection..."
npx @modelcontextprotocol/server-render --test

echo "✅ MCP setup complete!"
echo "📋 You can now use MCP to connect to Render and read logs"
