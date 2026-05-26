import json

from app.main import sse


def test_sse_formats_named_event() -> None:
    payload = {"state": "ok"}
    encoded = sse("status", payload)

    assert encoded.startswith("event: status\n")
    assert encoded.endswith("\n\n")
    assert json.loads(encoded.split("data: ", 1)[1]) == payload

