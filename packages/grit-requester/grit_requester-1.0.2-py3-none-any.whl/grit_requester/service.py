import requests
from datetime import datetime
from typing import Optional

from .domain import GritDomain
from .config import GritConfig

class GritService:
    def __init__(self, config: GritConfig):
        self.base_url = config.base_url
        self.auth_url = config.auth_url
        self.token = config.token
        self.secret = config.secret
        self.context = config.context

        self.token_header = config.token_header
        self.token_expiration_header = config.token_expiration_header

        self.access_token: Optional[str] = None
        self.token_expiration: Optional[datetime] = None

        self._auth_lock = False

        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "context": self.context,
            }
        )

        self.session.hooks["response"] = [self._handle_response]

    def domain(self, domain: str) -> GritDomain:
        return GritDomain(self, domain)

    def auth(self):
        if self._auth_lock:
            return

        self._auth_lock = True
        try:
            response = requests.post(
                self.auth_url, json={"token": self.token, "secret": self.secret}
            )
            response.raise_for_status()

            refreshed_token = response.headers.get(self.token_header)
            refreshed_valid_until = response.headers.get(self.token_expiration_header)

            if refreshed_token and refreshed_valid_until:
                self.access_token = refreshed_token
                self.token_expiration = datetime.fromisoformat(refreshed_valid_until)
            else:
                data = response.json()
                self.access_token = data["token"]
                self.token_expiration = datetime.fromisoformat(data["valid_until"])

            self.session.headers.update(
                {"Authorization": f"Bearer {self.access_token}"}
            )
        finally:
            self._auth_lock = False

    def is_token_valid(self) -> bool:
        return (
            bool(self.access_token)
            and bool(self.token_expiration)
            and datetime.now() < self.token_expiration
        )

    def _handle_response(self, r: requests.Response, *args, **kwargs):
        refreshed_token = r.headers.get(self.token_header)
        refreshed_valid_until = r.headers.get(self.token_expiration_header)

        if refreshed_token and refreshed_valid_until:
            parts = refreshed_token.split()
            if len(parts) == 2:
                self.access_token = parts[1]
                self.token_expiration = datetime.fromisoformat(refreshed_valid_until)
                self.session.headers.update(
                    {"Authorization": f"Bearer {self.access_token}"}
                )

        if r.status_code == 401 and not getattr(r.request, "_retry", False):
            r.request._retry = True
            self.auth()
            r.request.headers["Authorization"] = f"Bearer {self.access_token}"
            return self.session.send(r.request)

        return r

    def request(
        self,
        method: str,
        url: str,
        *,
        params: Optional[dict] = None,
        json: Optional[dict] = None,
        **kwargs,
    ) -> requests.Response:
        if not self.is_token_valid():
            self.auth()

        full_url = f"{self.base_url}/{url.lstrip('/')}"

        response = self.session.request(
            method, full_url, params=params, json=json, **kwargs
        )

        response.raise_for_status()
        return response
