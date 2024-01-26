import os
from base64 import b64encode
from typing import TYPE_CHECKING, Any, Dict
from requests.auth import HTTPBasicAuth

class TerariumAuth:
    username: str
    password: str

    def __init__(self) -> None:
        username = os.environ.get("AUTH_USERNAME", None)
        password = os.environ.get("AUTH_PASSWORD", None)
        if username and password:
            self.username = username
            self.password = password
        else:
            raise ValueError("Authentication details not provided")

    def auth_header(self) -> dict[str, str]:
        token = b64encode(f"{self.username}:{self.password}".encode('utf-8')).decode("ascii")
        return {"Authorization": f"Basic {token}"}

    def requests_auth(self) -> HTTPBasicAuth:
        return HTTPBasicAuth(self.username, self.password)


def get_auth() -> TerariumAuth|None:
    try:
        return TerariumAuth()
    except ValueError:
        return None
