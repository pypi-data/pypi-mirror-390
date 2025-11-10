from dymoapi import DymoAPI
from typing import Dict, Any

client = None # Will be initialized later

def set_client(api_key: str):
    global client
    client = DymoAPI({
        "api_key": api_key
    })

def validate_email(value: str) -> Dict[str, Any]:
    return client.is_valid_email(value).get("response", {})

def validate_phone(value: str) -> Dict[str, Any]:
    return client.is_valid_phone(value).get("response", {})

def validate_ip(value: str) -> Dict[str, Any]:
    return client.is_valid_ip(value).get("response", {})

def validate_generic(value: str) -> Dict[str, Any]:
    return client.is_valid_data_raw(value)