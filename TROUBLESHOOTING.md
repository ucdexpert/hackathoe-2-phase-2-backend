# Troubleshooting Guide: Todo App Backend on Hugging Face Spaces

## Common Issues and Solutions

### 1. Database Connection Error
**Problem**: Application fails to connect to the database
**Symptoms**: Error messages about database connection failure in the logs
**Solution**:
- Verify that your DATABASE_URL is correctly formatted
- Ensure the database is accessible from external sources
- Check that the database credentials are correct
- If using a free database service like Neon, make sure the connection limits haven't been exceeded

### 2. Missing Environment Variables
**Problem**: Application crashes due to missing configuration
**Symptoms**: Error messages about missing environment variables
**Solution**:
- Double-check that all required environment variables are set in the Space Secrets
- Refer to .env.example for the complete list of required variables
- Ensure variable names match exactly (case-sensitive)

### 3. Build Failure
**Problem**: Docker build fails
**Symptoms**: Error messages during the build phase in the logs
**Solution**:
- Check that all dependencies in requirements.txt are available
- Verify that the Dockerfile syntax is correct
- Look for any platform-specific dependencies that might not work in the Hugging Face environment

### 4. Application Startup Failure
**Problem**: Container builds successfully but application doesn't start
**Symptoms**: Application crashes shortly after startup
**Solution**:
- Check the runtime logs for specific error messages
- Verify that the application binds to the PORT environment variable
- Ensure all required services (like database) are available before the application starts

### 5. Port Binding Issues
**Problem**: Application fails to bind to the specified port
**Symptoms**: Address already in use or permission denied errors
**Solution**:
- The Dockerfile is configured to use the PORT environment variable provided by Hugging Face
- Make sure the application code respects the PORT environment variable
- Our app.py and Dockerfile are already configured correctly for this

## Recommended Database Setup

For testing purposes, you can use a free PostgreSQL service:

1. **Neon**: Sign up at https://neon.tech/
   - Create a new project
   - Get the connection string from the Project Settings
   - Use this as your DATABASE_URL

2. **Supabase**: Sign up at https://supabase.io/
   - Create a new project
   - Get the connection string from Project Settings > Database
   - Use this as your DATABASE_URL

## Health Check Endpoints

Once deployed, you can check the status of your backend:
- Root endpoint: `https://<your-space-url>/`
- API docs: `https://<your-space-url>/docs`
- Health check (if implemented): `https://<your-space-url>/health`

## Performance Considerations

- Free Hugging Face Spaces have limited resources and may sleep when inactive
- Cold starts may take longer as the container needs to initialize
- For production use, consider upgrading to a paid hardware option

## Security Considerations

- Restrict CORS settings in production (currently set to allow all origins for development)
- Use strong, unique values for SECRET_KEY
- Regularly rotate database credentials
- Monitor access logs if possible

## Monitoring Deployment Status

1. Check the "Build Logs" tab for compilation issues
2. Check the "Runtime Logs" tab for runtime issues
3. Use the "Files" tab to verify all necessary files are present
4. Test endpoints using the "Embed" preview or directly via the Space URL

## Quick Fixes

If your deployment is failing, check these quick fixes:

1. Is DATABASE_URL set correctly in Secrets?
2. Is SECRET_KEY set in Secrets?
3. Does your database accept external connections?
4. Are all dependencies in requirements.txt compatible?

## Contact Support

If you continue to experience issues:
1. Review the Hugging Face documentation: https://huggingface.co/docs/hub/spaces
2. Check the community forums
3. Reach out to Hugging Face support if needed