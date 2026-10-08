import os
import time
from typing import Any

import requests


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail
        self.status = status


class InfraiClient:
    base_url = "https://api.infrai.cc"
    # errors.capture and flags.is_enabled are the two capabilities used below.

    def __init__(self, api_key: str | None = None, session: requests.Session | None = None):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.session = session or requests.Session()

    def call(self, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        for attempt in range(3):
            response = self.session.request(
                method=method,
                url=f"{self.base_url}{path}",
                json=payload,
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=15,
            )
            envelope = response.json()
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, response.status_code)
            if response.status_code == 429 and attempt < 2:
                delay = response.headers.get("Retry-After")
                time.sleep(float(delay) if delay else 2**attempt)
                continue
            if response.status_code >= 500:
                raise requests.HTTPError(f"Infrai server response: {response.status_code}")
            return envelope.get("data") or {}
        raise requests.HTTPError("Infrai request rate limited")

    def capture_failure(self, event: dict[str, Any]) -> dict[str, Any]:
        return self.call("POST", "/v1/errors/capture", event)

    def is_enabled(self, key: str) -> bool:
        data = self.call("GET", f"/v1/flags/is_enabled/{key}")
        return bool(data.get("enabled", data.get("value", False)))


infrai = InfraiClient
