"""Apple Music: fetches an artist's latest releases and the ISRC of each track.

Requires an Apple Developer account (to generate the Developer Token):
  - TEAM_ID, KEY_ID and the .p8 key file with MusicKit access.
"""
import re
import time

import jwt  # PyJWT (+ cryptography)
import requests

API = "https://api.music.apple.com"


def make_token(team_id, key_id, p8_path):
    with open(p8_path, "r", encoding="utf-8") as f:
        private_key = f.read()

    now = int(time.time())
    return jwt.encode(
        {"iss": team_id, "iat": now, "exp": now + 60 * 60 * 12},
        private_key,
        algorithm="ES256",
        headers={"kid": key_id},
    )


def _get(path, token, params=None):
    url = path if path.startswith("http") else API + path
    r = requests.get(
        url,
        headers={"Authorization": f"Bearer {token}"},
        params=params,
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


def _paginate(path, token, params=None):
    """Follows the API's 'next' field until there are no more pages."""
    items = []
    data = _get(path, token, params)
    while True:
        items.extend(data.get("data", []))
        nxt = data.get("next")
        if not nxt:
            break
        data = _get(nxt, token)
    return items


def parse_url(url):
    """https://music.apple.com/br/artist/name/123456789 -> ('br', '123456789')"""
    m = re.search(r"music\.apple\.com/([a-z]{2})/artist/(?:[^/]+/)?(\d+)", url)
    if not m:
        raise ValueError("Invalid Apple Music artist link.")
    return m.group(1), m.group(2)


def fetch(url, token, max_albums=30, log=print):
    storefront, artist_id = parse_url(url)

    artist = _get(f"/v1/catalog/{storefront}/artists/{artist_id}", token)
    artist_name = artist["data"][0]["attributes"]["name"]

    raw_albums = _paginate(
        f"/v1/catalog/{storefront}/artists/{artist_id}/albums",
        token,
        {"limit": 25},
    )

    albums = [
        {
            "id": a["id"],
            "name": a["attributes"]["name"],
            "date": a["attributes"].get("releaseDate", "0000"),
        }
        for a in raw_albums
    ]
    albums.sort(key=lambda a: a["date"], reverse=True)
    albums = albums[:max_albums]

    log(f"{len(albums)} release(s) found.\n")

    for album in albums:
        log(f"Downloading {album['name']}...")
        songs = _paginate(
            f"/v1/catalog/{storefront}/albums/{album['id']}/tracks",
            token,
            {"limit": 100},
        )
        album["tracks"] = [
            {
                "number": s["attributes"].get("trackNumber", i + 1),
                "name": s["attributes"]["name"],
                "isrc": s["attributes"].get("isrc", "NOT FOUND"),
            }
            for i, s in enumerate(songs)
        ]

    return artist_name, albums
