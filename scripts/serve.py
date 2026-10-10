"""Docker entry point: prepare the shared store once, then serve the API."""
import os
import uvicorn
from app.config import Settings
from scripts.setup_project import setup

if __name__ == "__main__":
    setup(Settings.from_env(), os.getenv("INCLUDE_SYNTHETIC", "false").lower() == "true")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)
