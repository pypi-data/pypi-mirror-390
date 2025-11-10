import pytest
from dymo_cli.detection import detect_type

@pytest.mark.parametrize(
    "value,expected",
    [
        ("user@example.com", "email"),
        ("+34123456789", "phone"),
        ("192.168.0.1", "ip"),
        ("not-a-type", "other"),
        ("", "other")
    ],
)
def test_detect_type(value, expected):
    assert detect_type(value) == expected