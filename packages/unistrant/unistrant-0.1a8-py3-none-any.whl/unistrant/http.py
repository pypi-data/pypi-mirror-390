from abc import ABC, abstractmethod
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import requests


class Authentication(ABC):
    @abstractmethod
    def get_requests_kwargs(self) -> Mapping[str, Any]:
        pass


class CertificateAuthentication(Authentication):
    def __init__(self, certificate: Path, key: Path):
        super().__init__()
        self.certificate = certificate
        self.key = key

    def get_requests_kwargs(self) -> Mapping[str, Any]:
        return {
            "cert": (self.certificate, self.key),
        }


class HttpProtocol:
    def __init__(self, authentication: Authentication | None = None):
        requests_kwargs: dict[str, Any] = {
            "headers": {
                "User-Agent": "Unistrant",
            },
            "timeout": (10, 10),
        }
        if authentication:
            requests_kwargs |= authentication.get_requests_kwargs()
        self.requests_kwargs: Mapping[str, Any] = requests_kwargs

    def get(self, url: str) -> bytes:
        response = requests.get(url, **self.requests_kwargs)
        response.raise_for_status()
        return response.content

    def post(self, url: str, payload: bytes) -> None:
        response = requests.post(url, data=payload, **self.requests_kwargs)
        response.raise_for_status()
