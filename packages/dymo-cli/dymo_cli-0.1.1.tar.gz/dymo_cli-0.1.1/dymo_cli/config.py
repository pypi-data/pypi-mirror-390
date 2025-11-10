# Configuration loader for Dymo CLI.
import os
from typing import Dict

def load_config() -> Dict[str, str]:
    # Load configuration from environment variables or defaults.
    return {
        "DYMO_API_KEY": os.getenv("DYMO_API_KEY", ""),
        "DYMO_API_BASE": os.getenv("DYMO_API_BASE", "https://api.tpeoficial.com"),
        "TIMEOUT": os.getenv("DYMO_CLI_TIMEOUT", "10"),
    }