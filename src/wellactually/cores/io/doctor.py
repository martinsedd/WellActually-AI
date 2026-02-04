"""
Pre-flight system checks: GPU, Ollama, and C-compiler availability.
"""

import platform
import subprocess

import httpx


def check_gpu() -> tuple[bool, str]:
    """
    Check for GPU availability (NVIDIA/AMD/Apple Silicon).

    Returns:
        (success, message) tuple
    """
    system = platform.system()

    # NVIDIA GPU check
    try:
        result = subprocess.run(["nvidia-smi"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return True, "NVIDIA GPU detected"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # AMD GPU check (Linux)
    if system == "Linux":
        try:
            result = subprocess.run(["rocm-smi"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return True, "AMD GPU detected"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

    # Apple Silicon check (macOS)
    if system == "Darwin":
        try:
            result = subprocess.run(
                ["sysctl", "-n", "machdep.cpu.brand_string"], capture_output=True, text=True, timeout=5
            )
            if "Apple" in result.stdout:
                return True, "Apple Silicon detected"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

    return False, "No supported GPU detected. WellActually requires NVIDIA, AMD, or Apple Silicon GPU."


def check_compiler() -> tuple[bool, str]:
    """
    Check for C compiler availability (needed for Tree-sitter).

    Returns:
        (success, message) tuple
    """
    compilers = ["gcc", "clang", "cc"]

    for compiler in compilers:
        try:
            result = subprocess.run([compiler, "--version"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return True, f"C compiler found: {compiler}"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue

    return False, "No C compiler found. Install gcc or clang for Tree-sitter support."


async def check_ollama() -> tuple[bool, str]:
    """
    Check Ollama API availability and try to ping it.

    Returns:
        (success, message) tuple
    """
    ollama_url = "http://localhost:11434/api/tags"

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(ollama_url)
            if response.status_code == 200:
                return True, "Ollama is running and accessible"
            else:
                return False, f"Ollama responded with status {response.status_code}"
    except httpx.ConnectError:
        return False, "Cannot connect to Ollama. Is it running (http://localhost:11434)"
    except httpx.TimeoutException:
        return False, "Ollama connection timed out"
    except Exception as e:
        return False, f"Ollama check failed: {str(e)}"
