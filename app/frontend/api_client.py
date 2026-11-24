"""Thin wrapper around the Sopranos API. The frontend only talks HTTP, never the DB."""

import os

import requests

API_URL = os.environ.get("API_URL", "http://localhost:8000").rstrip("/")
TIMEOUT = 5


class ApiError(Exception):
    """The API answered with an error status."""

    def __init__(self, status_code: int, messages: list[str]):
        super().__init__(", ".join(messages))
        self.status_code = status_code
        self.messages = messages


class ApiUnavailable(Exception):
    """The API could not be reached at all."""


def _messages(response: requests.Response) -> list[str]:
    """Turn FastAPI's error body into a list of readable strings."""
    try:
        detail = response.json().get("detail")
    except ValueError:
        return [f"API returned {response.status_code}"]
    if isinstance(detail, str):
        return [detail]
    if isinstance(detail, list):  # 422 validation errors
        return [
            f"{(e['loc'][-1] if e.get('loc') else 'field')}: {e.get('msg', 'invalid')}"
            for e in detail
        ]
    return [f"API returned {response.status_code}"]


def _request(method: str, path: str, **kwargs):
    try:
        response = requests.request(
            method, f"{API_URL}{path}", timeout=TIMEOUT, **kwargs
        )
    except requests.RequestException as exc:
        raise ApiUnavailable(str(exc)) from exc
    if not response.ok:
        raise ApiError(response.status_code, _messages(response))
    return response


def list_characters(name: str | None = None) -> list[dict]:
    params = {"limit": 100}
    if name:
        params["name"] = name
    return _request("GET", "/characters/", params=params).json()


def get_character(character_id: int) -> dict:
    return _request("GET", f"/characters/{character_id}").json()


def create_character(data: dict) -> dict:
    return _request("POST", "/characters/", json=data).json()


def update_character(character_id: int, data: dict) -> dict:
    return _request("PUT", f"/characters/{character_id}", json=data).json()


def delete_character(character_id: int) -> None:
    _request("DELETE", f"/characters/{character_id}")
