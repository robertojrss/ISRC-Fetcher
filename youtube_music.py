"""YouTube Music: lists an artist's releases and tracks.

NOTE: YouTube Music does NOT expose ISRCs (neither the official API nor the unofficial one).
So the ISRC of each track is looked up on Spotify by artist name + title.
This is an approximate match: it can be wrong for tracks with generic names,
remixes, live versions, etc. Each result is marked "via Spotify".
"""
import re

from ytmusicapi import YTMusic


def parse_url(url):
    """https://music.youtube.com/channel/UCxxxx -> 'UCxxxx'"""
    m = re.search(r"/channel/(UC[\w-]+)", url)
    if not m:
        raise ValueError(
            "Invalid YouTube Music artist link "
            "(it must look like .../channel/UC...)."
        )
    return m.group(1)


def _sections(yt, data):
    items = []
    for key in ("albums", "singles"):
        sec = data.get(key) or {}
        results = sec.get("results", [])
        if sec.get("browseId") and sec.get("params"):
            try:
                results = yt.get_artist_albums(sec["browseId"], sec["params"])
            except Exception:
                pass
        items.extend(results)
    return items


def fetch(url, spotify_lookup, max_albums=30, log=print):
    """spotify_lookup(artist, title) -> ISRC or None."""
    channel_id = parse_url(url)
    yt = YTMusic()

    data = yt.get_artist(channel_id)
    artist_name = data["name"]

    seen, albums = set(), []
    for a in _sections(yt, data):
        bid = a.get("browseId")
        if not bid or bid in seen:
            continue
        seen.add(bid)
        albums.append(
            {"id": bid, "name": a.get("title", "?"), "date": str(a.get("year") or "0000")}
        )

    albums.sort(key=lambda a: a["date"], reverse=True)
    albums = albums[:max_albums]

    log(f"{len(albums)} release(s) found.\n")

    for album in albums:
        log(f"Downloading {album['name']}...")
        info = yt.get_album(album["id"])
        tracks = []
        for i, t in enumerate(info.get("tracks", [])):
            title = t.get("title", "?")
            isrc = spotify_lookup(artist_name, title)
            tracks.append(
                {
                    "number": t.get("trackNumber") or i + 1,
                    "name": title,
                    "isrc": f"{isrc} (via Spotify)" if isrc else "NOT FOUND",
                }
            )
        album["tracks"] = tracks

    return artist_name, albums
