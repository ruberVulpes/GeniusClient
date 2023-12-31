from __future__ import annotations

import os
import typing as t
from urllib.parse import urljoin

import requests

import genius_client.models as m

_SortType = t.Literal["title", "popularity"]
_TextFormatType = t.Literal["dom", "plain", "html"]
_PaginatedMethodType = t.Literal["artists_songs", "referents"]


class GeniusClient(requests.Session):
    base_url = "https://api.genius.com"

    def __init__(self, access_token: str | None = None, per_page: int = 10):
        super().__init__()
        self.per_page = per_page
        self.access_token = access_token or os.environ.get("GENIUS_ACCESS_TOKEN")
        if self.access_token is None:
            msg = "Supply access_token or set the GENIUS_ACCESS_TOKEN environment variable"
            raise ValueError(msg)
        self.headers.update({"Authorization": f"Bearer {self.access_token}"})

    def genius_request(self, method: str, url: str, params: dict, **kwargs) -> dict:
        response = self.request(method, urljoin(self.base_url, url), params=params, **kwargs)
        if response.ok:
            return response.json()["response"]
        msg = {"response": response.json()["response"], "method": method, "url": url, "params": params, "kwargs": kwargs}
        raise RuntimeError(msg)

    def genius_get(self, url, params: dict) -> dict:
        response = self.genius_request("GET", url=url, params=params, allow_redirects=True)
        return response

    def paginated_get(self, url: str, params: dict) -> dict:
        params.setdefault("page", 1)
        params.setdefault("text_format", "plain")
        return self.genius_get(url, params=params)

    def annotations(self, annotations_id: str | int, text_format: _TextFormatType = "plain") -> m.Annotation:
        """https://docs.genius.com/#annotations-h2"""
        path = f"/annotations/{annotations_id}"
        response = self.genius_get(path, params={"text_format": text_format})
        return m.Annotation.model_validate(response["annotation"])

    def referents(self, song_id: str = "", web_page_id: str = "", **kwargs) -> tuple[str | None, list[m.Referent]]:
        """https://docs.genius.com/#/referents-h2"""
        if not bool(song_id) ^ bool(web_page_id):
            msg = "You may pass only one of song_id and web_page_id, not both"
            raise ValueError(msg)
        if song_id:
            kwargs["song_id"] = song_id
        if web_page_id:
            kwargs["web_page_id"] = web_page_id
        response = self.paginated_get("/referents", params=kwargs)
        # This method supports pagination but doesn't return next_page
        next_page = kwargs.get("page", 1) + 1 if response["referents"] else None
        return next_page, [m.Referent.model_validate(r) for r in response["referents"]]

    def albums(self, album_id:str) -> m.FullAlbum:
        path = f"/albums/{album_id}"
        response = self.genius_get(path, params={})
        return m.FullAlbum.model_validate(response['album'])


    def songs(self, song_id: str, text_format: _TextFormatType = "plain") -> m.FullSong:
        """https://docs.genius.com/#/songs-h2"""
        path = f"/songs/{song_id}"
        response = self.genius_get(path, params={"text_format": text_format})
        return m.FullSong.model_validate(response["song"])

    def artists(self, artist_id: str, text_format: _TextFormatType = "plain") -> m.Artist:
        """https://docs.genius.com/#/artists-h2"""
        path = f"/artists/{artist_id}"
        response = self.genius_get(path, params={"text_format": text_format})
        return m.Artist.model_validate(response["artist"])

    def artists_songs(self, artist_id: str, sort: _SortType = "popularity", **kwargs) -> tuple[str | None, list[m.Song]]:
        """https://docs.genius.com/#/artists-h2"""
        path = f"/artists/{artist_id}/songs"
        response = self.paginated_get(path, params={"sort": sort, **kwargs})
        return response.get("next_page"), [m.Song.model_validate(song) for song in response["songs"]]

    def web_pages(self, raw_annotatable_url: str = "", canonical_url: str = "", og_url: str = "") -> m.WebPage:
        """https://docs.genius.com/#/web_pages-h2"""
        params = {"raw_annotatable_url": raw_annotatable_url, "canonical_url": canonical_url, "og_url": og_url}
        params = {k: v for k, v in params.items() if v}
        if not params:
            msg = "One or more urls must be provided"
            raise ValueError(msg)
        return m.WebPage.model_validate(self.genius_get("/web_pages/lookup", params=params)["web_page"])

    def search(self, q: str) -> list[dict]:
        """https://docs.genius.com/#/search-h2"""
        response = self.genius_get("/search", params={"q": q})
        return [hit["result"] for hit in response["hits"]]

    def user(self, user_id: str, text_format: _TextFormatType = "plain") -> m.User:
        path = f"/users/{user_id}"
        return m.User.model_validate(self.genius_get(path, params={"text_format": text_format})["user"])

    def account(self, text_format: _TextFormatType = "plain") -> m.Me:
        """https://docs.genius.com/#/account-h2"""
        return m.Me.model_validate(self.genius_get("/account", params={"text_format": text_format})["user"])

    def paginator(self, method: _PaginatedMethodType, **kwargs) -> t.Iterable[m.Song | m.Referent]:
        """A Paginator for /artists/:id/songs and /referents"""
        next_page, results = getattr(self, method)(**kwargs)
        yield results
        while next_page:
            kwargs["page"] = next_page
            next_page, results = getattr(self, method)(**kwargs)
            if results:
                yield results

    def __str__(self):
        return self.__class__.__name__

    def __hash__(self):
        return hash(self.base_url + self.access_token)


