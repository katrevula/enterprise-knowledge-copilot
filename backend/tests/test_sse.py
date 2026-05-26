import json

from app.main import exclude_message, sse


def test_sse_formats_named_event() -> None:
    payload = {"state": "ok"}
    encoded = sse("status", payload)

    assert encoded.startswith("event: status\n")
    assert encoded.endswith("\n\n")
    assert json.loads(encoded.split("data: ", 1)[1]) == payload


def test_exclude_message_removes_current_prompt_from_history() -> None:
    history = [
        {"id": "previous", "role": "assistant", "content": "Earlier answer"},
        {"id": "current", "role": "user", "content": "Current question"},
    ]

    filtered = exclude_message(history, "current")

    assert filtered == [history[0]]
