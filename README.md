# AutoDITag

A Tool to automatically rename and tag mp3 files

Meant to be used to create playlist files and corresponding tagged mp3 files, that can be used in [DanceInterpreter](https://github.com/klassenserver7b/danceinterpreter-rs)

## Installation and Usage

Requires Python 3.6+, mutagen and argparse

### Pip
```sh
pip install auto-di-tag
auto-di-tag -f PATH_TO_DESCRIPTOR_FILE -d PATH_TO_MUSICFOLDER -n PLAYLISTNAME
```

### Manual
```sh
git clone https://github.com/klassenserver7b/AutoDITag.git
cd AutoDITag
pip install -r requirements.txt
python3 auto_di_tag.py -f PATH_TO_DESCRIPTOR_FILE -d PATH_TO_MUSICFOLDER -n PLAYLISTNAME
```

### How to create a descriptorfile
[see Examples](examples/README.md)

## Spotify Album Art (Optional)

AutoDITag can fetch high-quality album art from Spotify and embed it in your MP3 files.

### Quick Setup

1. **Get Spotify API Credentials (Free):**
   - Go to https://developer.spotify.com/dashboard
   - Log in with your Spotify account (free account works)
   - Click "Create app"
   - Fill in:
     - **App name:** AutoDITag (or anything you like)
     - **App description:** Personal music tagging tool
     - **Redirect URI:** http://localhost (required but not used)
     - **API:** Check "Web API"
   - Click "Settings" to view your **Client ID** and **Client Secret**

2. **Configure AutoDITag:**

   **Option A: Command Line Arguments**
   ```sh
   auto-di-tag -f tänze.txt -d ./Tanzmusik -n "Schulball 2024" \
     --spotify-client-id YOUR_CLIENT_ID \
     --spotify-client-secret YOUR_CLIENT_SECRET \
     --use-spotify-art
   ```

   **Option B: Environment Variables**
   ```sh
   export SPOTIFY_CLIENT_ID="your_client_id"
   export SPOTIFY_CLIENT_SECRET="your_client_secret"
   
   auto-di-tag -f tänze.txt -d ./Tanzmusik -n "Schulball 2024" --use-spotify-art
   ```

   **Option C: Config File**
   
   Create `~/.config/autoditag/spotify.conf`:
   ```json
   {
     "client_id": "your_client_id",
     "client_secret": "your_client_secret"
   }
   ```
   
   Then run:
   ```sh
   auto-di-tag -f tänze.txt -d ./Tanzmusik -n "Schulball 2024" --use-spotify-art
   ```

### How It Works

When you use `--use-spotify-art`:
- AutoDITag searches Spotify for each track by title and artist
- Downloads the highest quality album cover art available
- Embeds the cover art directly into the MP3 file's ID3 tags
- Falls back gracefully if a track isn't found on Spotify

### Security & Privacy

- 🔒 **Your credentials are personal** - each user creates their own Spotify app
- 🔒 **No user data accessed** - only searches public track information
- 🔒 **Stored locally** - config file uses 0600 permissions (only you can read)
- 🔒 **Free to use** - Spotify's API is free for this use case

### FAQ

**Q: Do I need Spotify Premium?**  
A: No, a free Spotify account works perfectly.

**Q: Does this cost money?**  
A: No, Spotify's API is completely free for searching tracks and downloading album art.

**Q: What if I don't want to use Spotify?**  
A: That's fine! AutoDITag works without it. Just omit the `--use-spotify-art` flag.

**Q: What if a song isn't found on Spotify?**  
A: AutoDITag will display a message and continue processing the rest of your playlist.

**Q: Can I share my credentials?**  
A: While technically possible, it's better for each person to create their own free app (takes 2 minutes).

## License
This Project is Licensed under the [MIT License](LICENSE).
Therefore there is NO WARRANTY for anything regarding this code

## Help Menu

```
usage: AutoDITag [-h] [-i SPOTIFY_CLIENT_ID] [-p SPOTIFY_CLIENT_SECRET] 
                 -f FILE -d DIR -n NAME [-s USE_SPOTIFY_ART]

Automatically rename and tag your dance playlist

options:
  -h, --help            show this help message and exit
  -i, --spotify-client-id CLIENT_ID
                        Spotify Client ID for album art
  -p, --spotify-client-secret CLIENT_SECRET
                        Spotify Client Secret for album art
  -f FILE, --file FILE  Your txt file containing the playlist
  -d DIR, --dir DIR     The directory of the mp3 files to process
  -n NAME, --name NAME  The name of the Playlist. eg: Schulball 08.05.2024
  -s, --use-spotify-art
                        Fetch album art from Spotify instead of embedded art

see https://github.com/klassenserver7b/AutoDITag
```

## Examples

### Basic usage (without Spotify):
```sh
auto-di-tag -f ./tänze.txt -d ./Tanzmusik -n "Schulball 08.05.2024"
```

### With Spotify album art:
```sh
auto-di-tag -f ./tänze.txt -d ./Tanzmusik -n "Schulball 08.05.2024" \
  --spotify-client-id YOUR_ID \
  --spotify-client-secret YOUR_SECRET \
  --use-spotify-art
```

### Using environment variables:
```sh
export SPOTIFY_CLIENT_ID="your_id"
export SPOTIFY_CLIENT_SECRET="your_secret"

auto-di-tag -f ./tänze.txt -d ./Tanzmusik -n "Schulball 08.05.2024" -s
```
