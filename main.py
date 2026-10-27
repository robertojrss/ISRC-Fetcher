import requests
import re

CLIENT_ID = "your_id"
CLIENT_SECRET = "your_secret"

TOKEN_URL = "https://accounts.spotify.com/api/token"
API = "https://api.spotify.com/v1"


def get_token():

    r = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET
        }
    )

    r.raise_for_status()

    return r.json()["access_token"]


def spotify_get(url, token, params=None):

    if not url.startswith("http"):
        url = API + url

    r = requests.get(
        url,
        headers={
            "Authorization": f"Bearer {token}"
        },
        params=params
    )

    r.raise_for_status()

    return r.json()


def artist_id(url):

    m = re.search(r"/artist/([A-Za-z0-9]+)", url)

    if not m:
        raise Exception("Invalid URL.")

    return m.group(1)


def get_artist(url, token):

    id = artist_id(url)

    data = spotify_get(
        f"/artists/{id}",
        token
    )

    return id, data["name"]


def get_last_three_albums(artist_id, token):

    albums = []
    offset = 0
    limit = 10

    while True:

        data = spotify_get(
            f"/artists/{artist_id}/albums",
            token,
            {
                "include_groups": "album,single",
                "limit": limit,
                "offset": offset
            }
        )

        for album in data["items"]:

            albums.append({
                "id": album["id"],
                "name": album["name"],
                "date": album["release_date"]
            })

        if data.get("next") is None:
            break

        offset += limit

    albums.sort(
        key=lambda x: x["date"],
        reverse=True
    )

    return albums[:30]

def get_tracks(album_id, token):

    tracks = []
    offset = 0
    limit = 50

    while True:

        data = spotify_get(
            f"/albums/{album_id}/tracks",
            token,
            {
                "limit": limit,
                "offset": offset
            }
        )

        for track in data["items"]:

            details = spotify_get(
                f"/tracks/{track['id']}",
                token
            )

            isrc = details.get(
                "external_ids",
                {}
            ).get(
                "isrc",
                "NOT FOUND"
            )

            tracks.append({
                "number": track["track_number"],
                "name": track["name"],
                "isrc": isrc
            })

        if data.get("next") is None:
            break

        offset += limit

    return tracks


def save_txt(artist_name, albums, token):

    with open("output.txt", "w", encoding="utf-8") as f:

        f.write(f"{artist_name.upper()}\n")
        f.write("=" * 70)
        f.write("\n\n")

        for album in albums:

            print(f"Downloading {album['name']}...")

            f.write(f"ALBUM: {album['name']}\n")
            f.write(f"Release date: {album['date']}\n")
            f.write("-" * 70)
            f.write("\n")

            tracks = get_tracks(
                album["id"],
                token
            )

            for track in tracks:

                f.write(
                    f"{track['number']:02d}. {track['name']}\n"
                )

                f.write(
                    f"    ISRC: {track['isrc']}\n\n"
                )

            f.write("\n")
            f.write("=" * 70)
            f.write("\n\n")


def main():

    print("=" * 60)
    print("Spotify ISRC Fetcher")
    print("=" * 60)

    url = input("\nPaste the artist link:\n\n")

    token = get_token()

    artist_id_value, artist_name = get_artist(
        url,
        token
    )

    print("\nArtist:", artist_name)

    albums = get_last_three_albums(
        artist_id_value,
        token
    )

    print(f"{len(albums)} release(s) found.\n")

    save_txt(
        artist_name,
        albums,
        token
    )

    print("\nDone!")
    print("File saved as output.txt")


if __name__ == "__main__":
    main()
