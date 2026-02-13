#!/bin/bash

# VoyageIQ - GitHub Push Automation Script
# This script handles the username and repository override.

echo "🚀 VoyageIQ - GitHub Automation"
echo "--------------------------------"

# Ask for the user's GitHub username
read -p "Enter your GitHub Username (e.g., eyesofbug): " GH_USER

# Ask for the repository name (Default to VoyageIQ-)
read -p "Enter your Repository Name [VoyageIQ-]: " REPO_NAME
REPO_NAME=${REPO_NAME:-"VoyageIQ-"}

echo "📍 Setting remote origin to: github.com/${GH_USER}/${REPO_NAME}.git"
git remote set-url origin "https://${GH_USER}@github.com/${GH_USER}/${REPO_NAME}.git"

echo "📦 Syncing latest changes..."
git add .
git commit -m "VoyageIQ Mega-Logic Suite & Real Data - Final Sync"

echo "⬆️ Pushing to GitHub..."
echo "⚠️ IMPORTANT: When it asks for your Password, PASTE your GitHub 'Personal Access Token' instead."
echo "   (GitHub no longer accepts normal passwords for terminal pushes)"
echo "--------------------------------"

git push -u origin main

if [ $? -eq 0 ]; then
    echo "✅ Success! All 16 files are now live on https://github.com/${GH_USER}/${REPO_NAME}"
else
    echo "❌ Push failed. Ensure the repository exists on GitHub.com first!"
fi
