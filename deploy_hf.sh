#!/bin/bash
# Script to prepare backend for Hugging Face deployment

echo "Preparing backend for Hugging Face Spaces deployment..."

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "Git is not installed. Please install git first."
    exit 1
fi

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit for Hugging Face deployment"
fi

# Create a new branch for the Hugging Face deployment
git checkout -b hf-deploy || git checkout hf-deploy

echo "Files prepared for Hugging Face deployment."
echo ""
echo "To deploy to Hugging Face Spaces:"
echo "1. Go to https://huggingface.co/spaces"
echo "2. Click 'Create new Space'"
echo "3. Select 'Docker' SDK"
echo "4. Choose 'Public' or 'Private' as appropriate"
echo "5. Connect to your Git repository"
echo "6. Add your environment variables in the Space settings"
echo "7. The Dockerfile will automatically build and deploy your app"
echo ""
echo "Make sure to add these environment variables in your Hugging Face Space settings:"
echo "- DATABASE_URL: PostgreSQL database connection string"
echo "- SECRET_KEY: JWT secret key"
echo "- Any other variables from .env.example"