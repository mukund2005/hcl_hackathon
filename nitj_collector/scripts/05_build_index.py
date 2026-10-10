"""Compatibility entry point: build the final persisted collection, never a separate one."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from app.config import Settings
from scripts.setup_project import setup

if __name__ == "__main__":
    print(setup(Settings.from_env()))
