from pathlib import Path

import pandas as pd
import pytest

from ingestion.api_to_csv import fetch_users, save_users


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


def test_fetch_users_returns_api_payload(monkeypatch):
    expected = [{"id": 1, "name": "Ada"}]
    monkeypatch.setattr(
        "ingestion.api_to_csv.requests.get",
        lambda url, timeout: FakeResponse(expected),
    )

    assert fetch_users("https://example.test/users") == expected


def test_fetch_users_rejects_non_list_payload(monkeypatch):
    monkeypatch.setattr(
        "ingestion.api_to_csv.requests.get",
        lambda url, timeout: FakeResponse({"users": []}),
    )

    with pytest.raises(ValueError, match="JSON array"):
        fetch_users("https://example.test/users")


def test_save_users_writes_normalized_csv(tmp_path: Path):
    output = tmp_path / "nested" / "users.csv"
    rows = [{"id": 1, "name": "Ada", "address": {"city": "London"}}]

    count = save_users(rows, output)

    assert count == 1
    assert output.exists()
    frame = pd.read_csv(output)
    assert frame.loc[0, "name"] == "Ada"
    assert frame.loc[0, "address.city"] == "London"


def test_save_users_handles_empty_payload(tmp_path: Path):
    output = tmp_path / "empty.csv"

    count = save_users([], output)

    assert count == 0
    assert output.exists()
    assert count == 0
