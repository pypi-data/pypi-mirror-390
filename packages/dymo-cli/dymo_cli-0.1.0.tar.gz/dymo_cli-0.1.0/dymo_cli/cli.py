import sys
import os, json
from pathlib import Path
from typing import Dict, Any

from .detection import detect_type
from .api import set_client, validate_email, validate_phone, validate_ip, validate_generic
from .ui import interactive_input, render_result_card, render_error, render_json_toggle

CONFIG_FILE = Path.home() / ".dymorc"

def load_config() -> dict:
    if CONFIG_FILE.exists():
        try: return json.loads(CONFIG_FILE.read_text())
        except Exception: return {}
    return {}

def save_config(cfg: dict):
    CONFIG_FILE.write_text(json.dumps(cfg))

CFG = load_config()

def ask_for_api_key() -> str:
    while True:
        print("Get your free API Key at https://tpe.li/new-api-key")
        key = interactive_input("Enter your DYMO API key (must start with 'dm_')").strip()
        if key.startswith("dm_"): return key
        print("Invalid API key. It must start with 'dm_'.")

def get_api_key(cfg: dict) -> str:
    key = cfg.get("DYMO_API_KEY")
    if key and key.startswith("dm_"): return key
    key = ask_for_api_key()
    cfg["DYMO_API_KEY"] = key
    save_config(cfg)
    return key

def run_once(value: str) -> Dict[str, Any]:
    t = detect_type(value)
    if t == "email": return validate_email(value)
    if t == "phone": return validate_phone(value)
    if t == "ip": return validate_ip(value)
    return validate_generic(value)

def print_welcome() -> None:
    print("=== Dymo CLI ===")
    print("Interactive validation tool for email, phone, and IP.")

def main(argv=None) -> int:
    argv = argv or sys.argv[1:]

    key = get_api_key(CFG)
    os.environ["DYMO_API_KEY"] = key
    set_client(key)

    print_welcome()
    try:
        if argv:
            value = " ".join(argv)
            result = run_once(value)
            if result.get("error"): render_error(result.get("message", "Unknown error."))
            else: render_result_card(result, detect_type(value))
            return 0

        while True:
            try: value = interactive_input()
            except KeyboardInterrupt:
                print("\nGoodbye.")
                return 0
            if not value.strip(): continue
            result = run_once(value)
            if result.get("error"):
                render_error(result.get("message", "Unknown error."))
                continue
            render_result_card(result, detect_type(value))
            print("[r] Re-run, [j] JSON, [q] Quit.")
            cmd = input("Choose: ").strip().lower()
            if cmd == "j":
                render_json_toggle(result)
            if cmd == "q":
                print("Bye.")
                return 0
    except Exception as e:
        render_error(str(e))
        return 1

if __name__ == "__main__": raise SystemExit(main())