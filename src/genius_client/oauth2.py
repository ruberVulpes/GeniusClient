import argparse
import os
import typing
import webbrowser
from dataclasses import dataclass, field
from urllib.parse import parse_qsl

import requests

from http.server import SimpleHTTPRequestHandler, HTTPServer

_ScopeType = typing.Literal["me", "create_annotation", "manage_annotation", "vote"]
default_redirect_url = "http://127.0.0.1"
default_redirect_port = 8080
default_redirect_uri = f"{default_redirect_url}:{default_redirect_port}"


@dataclass
class OAuthHelper:
    base_url = "https://api.genius.com/oauth"
    client_id: str | None = None
    client_secret: str | None = None
    scopes: list[_ScopeType] = field(default_factory=list)
    redirect_uri: str = field(default=default_redirect_uri)

    def __post_init__(self):
        self.client_id = self.client_id or os.environ.get("GENIUS_CLIENT_ID")
        self.client_secret = self.client_secret or os.environ.get("GENIUS_CLIENT_SECRET")
        if self.client_id is None:
            msg = "Supply client_id or set the GENIUS_CLIENT_ID environment variable"
            raise ValueError(msg)
        if self.client_secret is None:
            msg = "Supply client_secret or set the GENIUS_CLIENT_SECRET environment variable"
            raise ValueError(msg)

    def authenticate(self):
        params = {"client_id": self.client_id, "redirect_uri": self.redirect_uri, "scope": " ".join(self.scopes), "response_type": "code"}
        url = requests.Request("", f"{self.base_url}/authorize", params=params).prepare().url
        webbrowser.open(url)
        print(f"If not redirected go to {url}")

    def get_code(self):
        with HTTPServer(("", default_redirect_port), GeniusClientHttpHandler) as server:
            self.authenticate()
            while GeniusClientHttpHandler.code == "":
                server.handle_request()

    def get_token(self, code: str | None = None):
        code = code or GeniusClientHttpHandler.code
        if code is None:
            msg = "You must provide the authorization code or use the default redirect_uri"
            raise ValueError(msg)
        body = {
            "code": code,
            "client_secret": self.client_secret,
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(self.scopes),
            "response_type": "code",
        }
        response = requests.post(f"{self.base_url}/token", json=body)
        print(f"scopes={self.scopes}")
        print(f"GENIUS_ACCESS_TOKEN={response.json()['access_token']}")


class GeniusClientHttpHandler(SimpleHTTPRequestHandler):
    code = ""
    directory: str

    def do_GET(self):
        GeniusClientHttpHandler.code = dict(parse_qsl(self.path))["/?code"]
        self.directory = "templates"
        return super().do_GET()


def cli():
    parser = argparse.ArgumentParser(description="GeniusClient OAuthHelper")
    parser.add_argument("--scopes", choices=_ScopeType.__args__, nargs="*")
    parser.add_argument("--client_id", type=str, nargs="?", default=None, help="The GeniusClient Client ID")
    parser.add_argument("--client_secret", type=str, nargs="?", default=None, help="The GeniusClient Client Secret")
    args = parser.parse_args()
    oauth_helper = OAuthHelper(client_id=args.client_id, client_secret=args.client_secret, scopes=args.scopes)
    oauth_helper.get_code()
    oauth_helper.get_token()


if __name__ == "__main__":
    cli()
