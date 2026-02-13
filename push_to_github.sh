#!/bin/bash

# VoyageIQ - GitHub Push Automation Script
# This script handles the username override for git permission issues.

echo "🚀 VoyageIQ - GitHub Automation"
echo "--------------------------------"

# Ask for the user's GitHub username if not provided
if [ -z "$1" ]; then
    read -p "Enter your GitHub Username: " GH_USER
else
    GH_USER=$1
fi

REPO_URL="github.com/tripconsoleapp/VoyageIQ-.git"

echo "📍 Setting remote origin for: $GH_USER"
git remote set-url origin "https://${GH_USER}@${REPO_URL}"

echo "📦 Adding latest changes..."
git add .
git commit -m "VoyageIQ Mega-Logic Suite Upgrade - v2.0"

echo "⬆️ Pushing to GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo "✅ Success! Code is live on GitHub."
else
    echo "❌ Push failed. Please check your credentials/network."
fi
