"""
Main entry point for the WellActually CLI.
Delegates to Core-CLI for all command handling.
"""

from wellactually.cores.cli import app

if __name__ == "__main__":
    app()
