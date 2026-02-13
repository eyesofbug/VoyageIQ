#!/bin/bash

# VoyageIQ - Ultimate GitHub Push Script
# This version handles conflicts and permission overrides.

echo "🚀 VoyageIQ - Final Phase: GitHub Upload"
echo "----------------------------------------"

# 1. Get Details
read -p "Enter your GitHub Username: " GH_USER
read -p "Enter your Repository Name [VoyageIQ]: " REPO_NAME
REPO_NAME=${REPO_NAME:-"VoyageIQ"}

# 2. Fix Remote URL
echo "📍 Setting target to: github.com/${GH_USER}/${REPO_NAME}.git"
git remote set-url origin "https://${GH_USER}@github.com/${GH_USER}/${REPO_NAME}.git"

# 3. Add & Commit everything
echo "📦 Packing all 16 files..."
git add .
git commit -m "Complete VoyageIQ Project - Final Version" --allow-empty

# 4. The Force Push (The "Nuclear Option" for new repos)
echo "⬆️ Pushing to GitHub (Overwriting remote conflicts)..."
echo "⚠️ IMPORTANT: When it asks for Password, PASTE your 'Personal Access Token'."
echo "----------------------------------------"

git push -u origin main --force

if [ $? -eq 0 ]; then
    echo "✅ SUCCESS! Your project is live at: https://github.com/${GH_USER}/${REPO_NAME}"
    echo "   (Refresh your browser to see all 16 files)"
else
    echo "❌ Error: Authentication failed or Repository doesn't exist."
    echo "   Make sure you created a repo named '$REPO_NAME' on GitHub first!"
fi
