import os
from main import app

# This file serves as the entry point for Hugging Face Spaces
# The app is imported from main.py and run with the appropriate configuration

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)