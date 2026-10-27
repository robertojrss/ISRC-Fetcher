"""ISRC Fetcher — Spotify, Apple Music and YouTube Music.

Paste the artist link and it generates <Artist>_output.txt next to the program.
main.py (the original Spotify-only script) is reused as a module.
"""
import json
import os
import re
import sys

import main as spotify  # original main.py
import requests


def base_dir():
    if getattr(sys, "frozen", False):  # running as .exe
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


CONFIG_PATH = os.path.join(base_dir(), "config.json")


# ---------- credentials ----------

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def get_setting(cfg, key, env, prompt):
    """Environment variable > config.json > ask once and save."""
    value = os.environ.get(env) or cfg.get(key)
    if not value:
        value = input(prompt).strip()
        cfg[key] = value
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
    return value


def spotify_token(cfg):
    spotify.CLIENT_ID = get_setting(
        cfg, "spotify_client_id", "SPOTIFY_CLIENT_ID", "Spotify Client ID: "
    )
    spotify.CLIENT_SECRET = get_setting(
        cfg, "spotify_client_secret", "SPOTIFY_CLIENT_SECRET", "Spotify Client Secret: "
    )
    return spotify.get_token()


# ---------- platforms ----------

def detect_platform(url):
    u = url.lower()
    if "spotify.com" in u or u.startswith("spotify:"):
        return "spotify"
    if "music.apple.com" in u:
        return "apple"
    if "youtube.com" in u or "youtu.be" in u:
        return "youtube"
    return None


def fetch_spotify(url, cfg):
    token = spotify_token(cfg)
    artist_id, artist_name = spotify.get_artist(url, token)
    print("\nArtist:", artist_name)

    albums = spotify.get_last_three_albums(artist_id, token)
    print(f"{len(albums)} release(s) found.\n")

    for album in albums:
        print(f"Downloading {album['name']}...")
        album["tracks"] = spotify.get_tracks(album["id"], token)
    return artist_name, albums


def fetch_apple(url, cfg):
    import apple_music

    team = get_setting(cfg, "apple_team_id", "APPLE_TEAM_ID", "Apple Team ID: ")
    key = get_setting(cfg, "apple_key_id", "APPLE_KEY_ID", "Apple Key ID: ")
    p8 = get_setting(
        cfg, "apple_p8_path", "APPLE_P8_PATH", "Path to the .p8 file: "
    ).strip('"')
    token = apple_music.make_token(team, key, p8)
    name, albums = apple_music.fetch(url, token)
    print("\nArtist:", name)
    return name, albums


def fetch_youtube(url, cfg):
    import youtube_music

    token = spotify_token(cfg)  # only used to look up the ISRC by title
    cache = {}

    def lookup(artist, title):
        k = (artist.lower(), title.lower())
        if k in cache:
            return cache[k]
        isrc = None
        try:
            data = spotify.spotify_get(
                "/search",
                token,
                {"q": f'track:"{title}" artist:"{artist}"', "type": "track", "limit": 5},
            )
            for t in data.get("tracks", {}).get("items", []):
                if t["name"].strip().lower() == title.strip().lower():
                    isrc = t.get("external_ids", {}).get("isrc")
                    if isrc:
                        break
        except requests.RequestException:
            pass
        cache[k] = isrc
        return isrc

    name, albums = youtube_music.fetch(url, lookup)
    print("\nArtist:", name)
    print(
        "WARNING: YouTube Music does not provide ISRCs; the codes come from a "
        "Spotify search (approximate)."
    )
    return name, albums


# ---------- output ----------

def safe_name(text):
    text = re.sub(r'[\\/:*?"<>|]', "", text).strip().rstrip(".")
    return text or "artist"


def save_txt(artist_name, albums):
    path = os.path.join(base_dir(), f"{safe_name(artist_name)}_output.txt")

    with open(path, "w", encoding="utf-8") as f:
        f.write(f"{artist_name.upper()}\n")
        f.write("=" * 70 + "\n\n")

        for album in albums:
            f.write(f"ALBUM: {album['name']}\n")
            f.write(f"Release date: {album['date']}\n")
            f.write("-" * 70 + "\n")

            for t in album["tracks"]:
                f.write(f"{t['number']:02d}. {t['name']}\n")
                f.write(f"    ISRC: {t['isrc']}\n\n")

            f.write("\n" + "=" * 70 + "\n\n")

    return path


def run_once(cfg):
    url = input("\nPaste the artist link (Spotify / Apple Music / YouTube Music):\n\n").strip()
    if not url:
        return

    platform = detect_platform(url)
    if platform == "spotify":
        name, albums = fetch_spotify(url, cfg)
    elif platform == "apple":
        name, albums = fetch_apple(url, cfg)
    elif platform == "youtube":
        name, albums = fetch_youtube(url, cfg)
    else:
        print("Unrecognized link.")
        return

    path = save_txt(name, albums)
    print("\nDone!")
    print("File saved to:", path)


def main():
    print("=" * 60)
    print("ISRC Fetcher — Spotify | Apple Music | YouTube Music")
    print("=" * 60)

    cfg = load_config()

    while True:
        try:
            run_once(cfg)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\nError: {e}")

        again = input("\nSearch another artist? (y/n): ").strip().lower()
        if again not in ("s", "sim", "y", "yes"):
            break


if __name__ == "__main__":
    main()
