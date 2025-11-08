"""
Configuration management for Alprina CLI.
"""

import yaml
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

console = Console()

ALPRINA_DIR = Path.home() / ".alprina"
CONFIG_FILE = ALPRINA_DIR / "config.json"

DEFAULT_CONFIG = {
    "version": "0.1.0",
    "backend_url": "https://api.alprina.ai",
    "timeout": 30,
    "max_retries": 3,
    "log_level": "INFO",
    "theme": "dark",
    "memory": {
        "enabled": True,
        "api_key": "",  # Set via environment variable MEM0_API_KEY
        "user_id": "default"
    }
}


def load_config() -> dict:
    """Load configuration from file."""
    if not CONFIG_FILE.exists():
        return DEFAULT_CONFIG.copy()

    try:
        with open(CONFIG_FILE, "r") as f:
            import json
            config = json.load(f)
        return {**DEFAULT_CONFIG, **config}
    except Exception as e:
        console.print(f"[yellow]Warning: Could not load config: {e}[/yellow]")
        return DEFAULT_CONFIG.copy()


def save_config(config: dict):
    """Save configuration to file."""
    ALPRINA_DIR.mkdir(exist_ok=True)

    import json
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def init_config_command():
    """Initialize default configuration."""
    if CONFIG_FILE.exists():
        from rich.prompt import Confirm
        if not Confirm.ask("Config file already exists. Overwrite?", default=False):
            return

    save_config(DEFAULT_CONFIG)

    console.print(Panel(
        f"[green]✓ Configuration initialized[/green]\n\n"
        f"Location: {CONFIG_FILE}\n\n"
        f"Edit this file to customize Alprina settings.",
        title="Config Initialized"
    ))
