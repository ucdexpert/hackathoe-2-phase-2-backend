# Deployment Guide: Todo App Backend to Hugging Face Spaces

Follow these steps to deploy your backend to Hugging Face Spaces:

## Step 1: Prepare Your Repository

1. Commit all the changes to your backend directory:
   ```bash
   cd backend
   git add .
   git commit -m "Add files for Hugging Face deployment"
   git push origin main  # or your default branch
   ```

## Step 2: Create Hugging Face Space

1. Go to https://huggingface.co/spaces
2. Click "Create new Space"
3. Fill in the form:
   - Name: Choose a name for your space (e.g., "todo-backend")
   - License: Choose an appropriate license
   - SDK: Select "Docker"
   - Hardware: Choose the hardware tier you need (the free tier should work for testing)
   - Visibility: Public or Private as desired

## Step 3: Configure Repository Access

You have two options:

### Option A: Link to Existing Repository
1. Select "From Hub" tab
2. Enter your repository name (e.g., "Uzair001/todo-backend") if you pushed to Hugging Face Hub
3. Click "Duplicate"

### Option B: Use Git Integration
1. Select "From Git" tab
2. Enter the URL of your Git repository (GitHub, GitLab, etc.)
3. Click "Import"

## Step 4: Configure Environment Variables

Once your Space is created:

1. Go to your Space page
2. Click on "Files" tab
3. Click on "Settings" icon (gear icon)
4. Go to "Secrets" section
5. Add the following environment variables:
   - `DATABASE_URL`: Your PostgreSQL database connection string
   - `SECRET_KEY`: A random secret key for JWT tokens
   - `ALGORITHM`: Set to "HS256" (default)
   - `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration in minutes (default: 30)
   - Any other variables from `.env.example`

## Step 5: Monitor Deployment

1. Go to the "Logs" tab of your Space
2. Watch the build logs to ensure the Docker image builds successfully
3. Once built, the "Embed this Space" section will show the URL of your deployed backend

## Step 6: Test Your Deployment

1. Visit the URL provided in the "Embed this Space" section
2. Append "/docs" to access the FastAPI documentation (e.g., `https://uzair001-todo-backend.hf.space/docs`)
3. Test your API endpoints

## Troubleshooting

If you encounter issues:

1. Check the "Logs" tab for error messages
2. Ensure all required environment variables are set in the "Secrets" section
3. Verify that your database URL is correct and accessible
4. Make sure your database allows connections from external sources

## Notes

- The application will be served at the URL provided by Hugging Face
- The Dockerfile is configured to listen on the port specified by the PORT environment variable
- The application uses the startup event to create database tables automatically
- CORS is configured to allow all origins (you may want to restrict this in production)