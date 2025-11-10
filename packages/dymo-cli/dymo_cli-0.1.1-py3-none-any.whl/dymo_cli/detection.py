# Auto-detection utilities for input types.
import re
from typing import Literal

Type = Literal["email", "phone", "ip", "other"]

_email_re = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
_ipv4_re = re.compile(r"^(?:\d{1,3}\.){3}\d{1,3}$")
_ipv6_re = re.compile(
    r"^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$|"
    r"^(([0-9a-fA-F]{1,4}:){1,7}:)$|"
    r"^(:([0-9a-fA-F]{1,4}:){1,7})$|"
    r"^(([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4})$|"
    r"^(([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2})$|" 
    r"^(([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3})$|" 
    r"^(([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4})$|" 
    r"^(([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5})$|" 
    r"^([0-9a-fA-F]{1,4}:)((:[0-9a-fA-F]{1,4}){1,6})$|" 
    r"^::([0-9a-fA-F]{1,4}:){0,5}[0-9a-fA-F]{1,4}$"
)
_phone_re = re.compile(r"^\+?[0-9][0-9\-\s()]{4,}$")

def detect_type(value: str) -> Type:
    # Detect whether the given value is an email, phone, ip, or other.
    v = value.strip()
    if not v: return "other"
    if _email_re.match(v): return "email"
    if _ipv4_re.match(v):
        parts = v.split(".")
        if all(0 <= int(p) <= 255 for p in parts): return "ip"
    if _ipv6_re.match(v): return "ip"
    if _phone_re.match(v): return "phone"
    return "other"