ISRC Fetcher

Find the ISRCs of the 30 most recent releases from any artist on Spotify, Apple Music or YouTube Music.

Features

- Fetches artist data from an artist link (Spotify, Apple Music or YouTube Music)
- Detects the platform automatically from the link you paste
- Lists the 30 most recent releases (albums + singles)
- Extracts the ISRC of every track from each release
- Generates an organized text file named after the artist (e.g. Artist Name_output.txt)
- Two ways to use it: a double-click .exe for Windows, or the Python scripts

Platform support

- Spotify: full support, ISRCs come straight from the Spotify Web API.
- Apple Music: full support, ISRCs come straight from the Apple Music API. Requires an Apple Developer account.
- YouTube Music: YouTube does not provide ISRCs. Releases and tracks are listed from YouTube Music, and each ISRC is looked up on Spotify by artist + track title. This is an approximate match and can be wrong for remixes, live versions or generic titles. These results are marked "(via Spotify)" in the output.

Easy way (no Python needed)

1. Download ISRC-Fetcher.exe from the Releases page (or from the "Build EXE" action under the Actions tab).
2. Double-click it. A command prompt window opens.
3. Paste the artist link and press Enter.
4. On the first run for each platform it asks for your credentials once and saves them in a config.json next to the .exe.
5. When it finishes, the file Artist Name_output.txt appears in the same folder as the .exe.
6. Type s to search another artist, or n to close.

Notes:
- Windows may show a "Windows protected your PC" warning because the .exe is not code-signed. Click "More info" > "Run anyway" if you trust the source, or build it yourself (see below).
- config.json contains your private keys. Do not share it.

Requirements (for the Python way)

- Python 3.8+
- A Spotify for Developers account with an app created (to get a Client ID and Client Secret). Needed for Spotify and for YouTube Music lookups.
- For Apple Music only: an Apple Developer account with a MusicKit key (Team ID, Key ID and the .p8 file)

Installation

git clone https://github.com/robertojrss/Spotify-ISRC-Fetcher.git
cd Spotify-ISRC-Fetcher
pip install -r requirements.txt

Configuration

You can skip this step: the program asks for anything missing and saves it in config.json. Or set your credentials as environment variables before running (avoid hardcoding them):

Linux / macOS:
export SPOTIFY_CLIENT_ID="your_client_id"
export SPOTIFY_CLIENT_SECRET="your_client_secret"
export APPLE_TEAM_ID="your_team_id"
export APPLE_KEY_ID="your_key_id"
export APPLE_P8_PATH="/path/to/AuthKey_XXXX.p8"

Windows (PowerShell):
$env:SPOTIFY_CLIENT_ID="your_client_id"
$env:SPOTIFY_CLIENT_SECRET="your_client_secret"
$env:APPLE_TEAM_ID="your_team_id"
$env:APPLE_KEY_ID="your_key_id"
$env:APPLE_P8_PATH="C:\path\to\AuthKey_XXXX.p8"

You can also copy config.example.json to config.json and fill it in.

Usage

python isrc_fetcher.py

Paste an artist link when prompted, for example:
https://open.spotify.com/artist/1234567890abcdef
https://music.apple.com/us/artist/artist-name/1234567890
https://music.youtube.com/channel/UCxxxxxxxxxxxxxxxxxxxxxx

The script generates a file called Artist Name_output.txt with all releases and ISRCs found.

The original Spotify-only script is still included. To use it, put your Client ID and Client Secret at the top of main.py and run:

python main.py

It generates output.txt.

Build the .exe yourself

On Windows with Python installed, double-click build_exe.bat. The executable is created at dist\ISRC-Fetcher.exe.

No Windows or no Python? Push the project to GitHub and run the "Build EXE" workflow (Actions tab > Build EXE > Run workflow). Download the .exe from the finished run.

Example output

ARTIST NAME
======================================================================

ALBUM: Album Name
Release date: 2026-05-10
----------------------------------------------------------------------
01. Track Name
    ISRC: US1234567890

02. Another Track
    ISRC: US1234567891

======================================================================

Built with

- Python
- Spotify Web API
- Apple Music API
- ytmusicapi
- requests
- PyInstaller

License

This project is licensed under the MIT License. See the LICENSE file for details.
