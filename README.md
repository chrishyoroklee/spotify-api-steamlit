# Spotify Metadata Explorer

A Streamlit web app that fetches and exports metadata from Spotify tracks, albums, artists, and playlists. Built to work with Spotify's Development Mode restrictions (post-November 2024).

## Features

✅ **Track Metadata** - Get detailed information about any Spotify track  
✅ **Album Metadata** - Fetch album details including full tracklist  
✅ **Artist Metadata** - Retrieve artist info, genres, followers, and popularity  
✅ **Playlist Metadata** - Export all tracks from user-created playlists  
✅ **User Profile** - View your Spotify account information  
✅ **CSV Export** - Download all data as CSV files

## What's NOT Available

⚠️ Due to Spotify's API restrictions (as of November 2024), the following are **not accessible** in Development Mode:
- Audio Features (danceability, energy, tempo, etc.)
- Audio Analysis
- Recommendations
- Related Artists
- Featured/Algorithmic Playlists

To access these features, you need [Extended Quota Mode](https://developer.spotify.com/documentation/web-api/concepts/quota-modes), which requires a registered business with 250k+ monthly active users.

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Create a Spotify App

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Click "Create app"
3. Fill in the app details:
   - **App name:** Spotify Metadata Explorer
   - **App description:** Personal metadata fetcher
   - **Redirect URI:** `http://localhost:8501`
4. Click "Save"
5. Copy your **Client ID** and **Client Secret**

### 3. Add Yourself to User Allowlist (for Streamlit Web App)

If using the Streamlit web app with OAuth, you need to allowlist yourself:

1. In your Spotify app dashboard, click **Settings**
2. Go to **User Management** tab
3. Click **Add new user**
4. Enter your name and the **email address associated with your Spotify account**
5. Click **Add User**

**Note:** The standalone Python script (`spotify_metadata.py`) uses Client Credentials flow and doesn't require user allowlisting.

## Usage

### Option 1: Streamlit Web App

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

1. Enter your **Client ID** and **Client Secret** in the sidebar
2. Click **"Click here to login with Spotify"**
3. Authorize the app with your Spotify account
4. Use the tabs to fetch different types of metadata:
   - 🎵 **Track** - Paste a Spotify track URL
   - 💿 **Album** - Paste a Spotify album URL
   - 🎤 **Artist** - Paste a Spotify artist URL
   - 📋 **Playlist** - Paste a Spotify playlist URL
   - 👤 **Profile** - View your account info
5. Download data as CSV files

### Option 2: Standalone Python Script

Use `spotify_metadata.py` for programmatic access without Streamlit:

```python
from spotify_metadata import SpotifyMetadataFetcher

# Initialize
fetcher = SpotifyMetadataFetcher(
    client_id="your_client_id", 
    client_secret="your_client_secret"
)

# Get track metadata
track = fetcher.get_track("https://open.spotify.com/track/...")
print(f"{track['name']} by {track['artists']}")
fetcher.save_to_csv(track, "track.csv")

# Get album metadata (includes all tracks)
album = fetcher.get_album("https://open.spotify.com/album/...")
fetcher.save_to_csv(album, "album.csv")

# Get artist metadata
artist = fetcher.get_artist("https://open.spotify.com/artist/...")
print(f"{artist['name']}: {artist['followers']:,} followers")

# Get playlist metadata (includes all tracks)
playlist = fetcher.get_playlist("https://open.spotify.com/playlist/...")
fetcher.save_to_csv(playlist, "playlist.csv")
```

Run the included examples:
```bash
# Edit spotify_metadata.py to add your credentials, then:
python spotify_metadata.py
```

## Example URLs

- **Track:** `https://open.spotify.com/track/7C0LbWtZgDYjmaSuz10AeD`
- **Album:** `https://open.spotify.com/album/1A2GTWGtFfWp7KSQTwWOyo`
- **Artist:** `https://open.spotify.com/artist/06HL4z0CvFAxyc27GXpf02`
- **Playlist:** `https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M`

## Deployment

To deploy the Streamlit app on Streamlit Cloud:

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Deploy your app
4. Update the `REDIRECT_URI` in `app.py` to your deployed URL (e.g., `https://your-app.streamlit.app`)
5. Add the new redirect URI to your Spotify app settings

For the standalone Python script, simply copy `spotify_metadata.py` and use it in your own projects.

## Troubleshooting

### 403 Forbidden Error
- Make sure you've added yourself to the User Management allowlist in your Spotify app settings
- Verify your Client ID and Client Secret are correct
- Check that the Redirect URI in your code matches exactly what's in your Spotify app settings

### "Invalid Credentials" Error
- Double-check your Client ID and Client Secret
- Make sure there are no extra spaces when copying

### Can't Access Playlists
- **Streamlit app:** Make sure you've authorized with the correct scopes
- **Python script:** Some playlists may require OAuth (user authentication) instead of Client Credentials
- Only user-created playlists work in Development Mode (not Spotify's algorithmic playlists)

## Why This Exists

This app was created as a response to Spotify's November 2024 API changes, which restricted access to audio features and other endpoints for individual developers. While we can't access the more advanced audio analysis features anymore, this tool still provides valuable metadata extraction capabilities for personal use.

## License

MIT License - Feel free to use and modify as needed.

## Contributing

This is a personal project, but feel free to fork and adapt it for your own use!