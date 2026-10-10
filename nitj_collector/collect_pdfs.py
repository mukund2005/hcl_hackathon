"""Index the reviewed PDFs collected by Mukund using the final shared store."""
from app.config import Settings
from scripts.setup_project import setup

if __name__ == "__main__":
    print(setup(Settings.from_env()))
