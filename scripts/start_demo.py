"""Create a local environment and run the demo app without manual PowerShell steps."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
import webbrowser
import socket
from pathlib import Path
from urllib.request import urlopen
from urllib.parse import urlsplit


def available_port(preferred):
    with socket.socket() as probe:
        try:
            probe.bind(("127.0.0.1",preferred))
        except OSError:
            probe.bind(("127.0.0.1",0))
        return probe.getsockname()[1]


def stop_stale_demo_processes(root: Path) -> None:
    try:
        import psutil
    except ImportError:
        return

    root_str = str(root.resolve()).lower()
    for proc in psutil.process_iter(["pid", "name", "cmdline", "cwd"]):
        try:
            cmdline = proc.info.get("cmdline") or []
            if not cmdline:
                continue
            command = " ".join(cmdline).lower()
            cwd = (proc.info.get("cwd") or "").lower()
            if ("uvicorn" in command and "app.main:app" in command and root_str in cwd) or (
                "streamlit" in command and "ui.py" in command and root_str in cwd
            ):
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except psutil.TimeoutExpired:
                    proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue


def get_project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def get_python_executable(root: Path) -> Path:
    venv_dir = root / ".venv"
    if os.name == "nt":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def build_demo_env(root: Path) -> dict[str, str]:
    env = os.environ.copy()
    env["HF_HOME"] = str((root / "runtime" / "models").resolve())
    env["ADMIN_TOKEN"] = "choose-a-local-demo-token"
    env["MOCK_LLM"] = "true"
    env.setdefault("DATA_DIR", str(root / "runtime" / "nitj"))
    env["API_URL"] = "http://127.0.0.1:8000"
    return env


def ensure_venv(root: Path) -> Path:
    python_executable = get_python_executable(root)
    if not python_executable.exists():
        subprocess.run([sys.executable, "-m", "venv", str(root / ".venv")], check=True)

    check_code = (
        "import importlib; "
        "mods=['fastapi','streamlit','uvicorn','chromadb','sentence_transformers','langgraph','pypdf','multipart','tzdata','psutil']; "
        "import sys; "
        "sys.exit(0 if all(importlib.util.find_spec(m) for m in mods) else 1)"
    )
    result = subprocess.run([str(python_executable), "-c", check_code], capture_output=True, text=True)
    if result.returncode != 0:
        subprocess.run(
            [str(python_executable), "-m", "pip", "install", "-r", str(root / "requirements.txt")],
            check=True,
            cwd=root,
        )
    return python_executable


def wait_for_url(url: str, timeout_seconds: int = 45) -> None:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        try:
            with urlopen(url, timeout=3) as response:
                if response.status < 500:
                    return
        except Exception:
            time.sleep(1)
    raise TimeoutError(f"{url} did not become ready within {timeout_seconds} seconds")


def run_backend(root: Path, env: dict[str, str], *, skip_seed: bool = False) -> subprocess.Popen:
    python_executable = get_python_executable(root)
    if not skip_seed:
        subprocess.run(
            [str(python_executable), "-m", "scripts.setup_project"] +
            (["--include-synthetic"] if env.get("INCLUDE_SYNTHETIC") == "true" else []),
            cwd=root,
            env=env,
            check=True,
        )

    process = subprocess.Popen(
        [str(python_executable), "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(urlsplit(env["API_URL"]).port)],
        cwd=root,
        env=env,
    )
    try:
        wait_for_url(env["API_URL"] + "/health")
    except Exception:
        process.terminate()
        process.wait()
        raise
    return process


def run_streamlit(root: Path, env: dict[str, str], *, open_browser: bool = True) -> subprocess.Popen:
    process = subprocess.Popen(
        [
            str(get_python_executable(root)),
            "-m",
            "streamlit",
            "run",
            "ui.py",
            "--browser.gatherUsageStats",
            "false",
            "--server.address",
            "127.0.0.1",
            "--server.port",
            env.get("UI_PORT","8501"),
        ],
        cwd=root,
        env=env,
    )
    ui_url = "http://127.0.0.1:" + env.get("UI_PORT","8501")
    try:
        wait_for_url(ui_url)
    except Exception:
        process.terminate()
        process.wait()
        raise
    if open_browser:
        if os.name == "nt":
            os.startfile(ui_url)
        else:
            webbrowser.open(ui_url)
    return process


def main() -> None:
    parser = argparse.ArgumentParser(description="Start the demo backend and Streamlit UI.")
    parser.add_argument("--skip-seed", action="store_true", help="Skip reseeding demo data.")
    parser.add_argument("--no-browser", action="store_true", help="Do not open the browser automatically.")
    parser.add_argument("--real-llm", action="store_true", help="Use the configured local Ollama model instead of the explicit mock.")
    parser.add_argument("--include-synthetic", action="store_true", help="Add two fictional policies for conflict/placement demonstration.")
    args = parser.parse_args()

    root = get_project_root()
    stop_stale_demo_processes(root)
    python_executable = ensure_venv(root)
    env = build_demo_env(root)
    env["MOCK_LLM"] = "false" if args.real_llm else "true"
    env["INCLUDE_SYNTHETIC"] = "true" if args.include_synthetic else "false"
    if args.include_synthetic and "DATA_DIR" not in os.environ:
        env["DATA_DIR"] = str(root / "runtime" / "nitj-demo")
    env["API_URL"] = "http://127.0.0.1:" + str(available_port(8000))
    env["UI_PORT"] = str(available_port(8501))

    print(f"Using Python: {python_executable}")
    backend = run_backend(root, env, skip_seed=args.skip_seed)
    streamlit_env = env.copy()
    streamlit_env["API_URL"] = env["API_URL"]
    streamlit = None
    try:
        streamlit = run_streamlit(root, streamlit_env, open_browser=not args.no_browser)
        print("Backend ready: " + env["API_URL"])
        print("Streamlit ready: http://127.0.0.1:" + env["UI_PORT"])
        backend.wait()
    except KeyboardInterrupt:
        print("Demo stopped.")
    finally:
        for process in (backend, streamlit):
            if process is not None and process.poll() is None:
                process.terminate()
                process.wait()


if __name__ == "__main__":
    main()
