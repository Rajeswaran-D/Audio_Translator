import os
import sys

# Ensure backend can be imported
sys.path.append(os.getcwd())

from backend.main import app
import uvicorn

if __name__ == "__main__":
    # This shim allows the user to still run 'python main.py' from root
    # while using the new backend architecture.
    uvicorn.run(app, host="0.0.0.0", port=8000)