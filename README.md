# GeniusClient

![PyPI - Version](https://img.shields.io/pypi/v/genius_client)
![GitHub Workflow Status (with event)](https://img.shields.io/github/actions/workflow/status/ruberVulpes/GeniusClient/tests.yml)
![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https://raw.githubusercontent.com/ruberVulpes/GeniusClient/main/pyproject.toml)
![GitHub License](https://img.shields.io/github/license/ruberVulpes/geniusclient)

A Python Client for the [Genius](https://genius.com/) API

## Installation 

```commandline
pip install genius_client
```

## Usage

```python
from genius_client import GeniusClient

genius_client = GeniusClient(access_token="My-Access-Token>")
```
The Genius Access Token can also be provided by setting a `GENIUS_ACCESS_TOKEN` environment variable.

```python
from genius_client import GeniusClient

genius_client = GeniusClient()
```

The client supports pagination for the `GET /artists/:id/songs` and the `GET /referents` endpoints.

```python
from genius_client import GeniusClient

genius_client = GeniusClient()
referents = [page for page in genius_client.paginator('referents', song_id='7076626')]
artist_songs = [page for page in genius_client.paginator('artists_songs', artist_id='1018784', per_page=50)]
```

### How to get an Access Token

This package includes a command line tool to get a Genius Access Token.
You'll first need to [create an API Client](https://genius.com/api-clients)
with an `App Website URL` of `http://127.0.0.1` and a `Redirect URI` of `http://127.0.0.1:8080`.

Usage:
```commandline
genius-client-token-helper  --scopes ... --client_id ... --client_secret ... 
```
The Client ID and Client Secret can also be provided via a `GENIUS_CLIENT_ID` and `GENIUS_CLIENT_SECRET` environment variables.

## API Models

This package provides the following models 

* Annotation
* Author
* Referent
* Artist
* Custom Performance
* Album
* Songs
  * AnnotatableSong
    * Represents the data returned by `Referent.annotatable`
  * Song
    * Represents the data returned via `GET /search` or `GET /artists/:id/songs`
  * FullSong
    * Represents the data returned via `GET /songs/:id`
* WebPage
* User
* Me

## API Method Implementation Status

* Implemented
  * `GET /annotations/:id`
  * `GET /referents`
  * `GET /songs/:id`
  * `GET /artists/:id`
  * `GET /artists/:id/songs`
  * `GET /webpages/lookup`
  * `GET /search`
  * `GET /users/:id`
  * `GET /account`
* Not Implemented
  * `POST /annotations`
  * `PUT /annotations/:id`
  * `DELETE /annotations/:id`
  * `PUT /annotations/:id/upvote`
  * `PUT /annotations/:id/downvote`
  * `PUT /annotations/:id/unvote`

## Future Work
  * Implement more endpoints
  * More test Coverage