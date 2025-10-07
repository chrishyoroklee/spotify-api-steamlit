import streamlit as st
import pandas as pd
import base64
from requests import post, get
import json
import re
from urllib.parse import urlencode

# OAuth Configuration
REDIRECT_URI = "http://localhost:8501"
SCOPE = "user-read-private user-read-email playlist-read-private playlist-read-collaborative user-top-read user-library-read"

# Function to get authorization URL
def get_auth_url(client_id):
    params = {
        'client_id': client_id,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'scope': SCOPE,
        'show_dialog': True
    }
    auth_url = f"https://accounts.spotify.com/authorize?{urlencode(params)}"
    return auth_url

# Function to get token from authorization code
def get_token_from_code(client_id, client_secret, code):
    try:
        auth_string = client_id + ":" + client_secret
        auth_bytes = auth_string.encode("utf-8")
        auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")
        
        url = "https://accounts.spotify.com/api/token"
        headers = {
            "Authorization": "Basic " + auth_base64,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI
        }
        
        result = post(url, headers=headers, data=data)
        result.raise_for_status()
        json_result = result.json()
        return json_result.get("access_token")
    except Exception as e:
        st.error(f"Error getting token: {e}")
        return None

def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

# Extract track, album, artist, or playlist ID from Spotify link
def extract_id(spotify_link, type="track"):
    patterns = {
        "track": r"open\.spotify\.com\/track\/([a-zA-Z0-9]+)",
        "album": r"open\.spotify\.com\/album\/([a-zA-Z0-9]+)",
        "artist": r"open\.spotify\.com\/artist\/([a-zA-Z0-9]+)",
        "playlist": r"open\.spotify\.com\/playlist\/([a-zA-Z0-9]+)"
    }
    match = re.search(patterns.get(type, patterns["track"]), spotify_link)
    if match:
        return match.group(1)
    else:
        st.error(f"Invalid Spotify {type} link.")
        return None

# Function to get track details
def get_track_details(token, track_id):
    url = f"https://api.spotify.com/v1/tracks/{track_id}"
    headers = get_auth_header(token)
    try:
        result = get(url, headers=headers)
        result.raise_for_status()
        return result.json()
    except Exception as e:
        st.error(f"Error fetching track: {e}")
        return None

# Function to get album details
def get_album_details(token, album_id):
    url = f"https://api.spotify.com/v1/albums/{album_id}"
    headers = get_auth_header(token)
    try:
        result = get(url, headers=headers)
        result.raise_for_status()
        return result.json()
    except Exception as e:
        st.error(f"Error fetching album: {e}")
        return None

# Function to get artist details
def get_artist_details(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}"
    headers = get_auth_header(token)
    try:
        result = get(url, headers=headers)
        result.raise_for_status()
        return result.json()
    except Exception as e:
        st.error(f"Error fetching artist: {e}")
        return None

# Function to get playlist details
def get_playlist_details(token, playlist_id):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}"
    headers = get_auth_header(token)
    try:
        result = get(url, headers=headers)
        result.raise_for_status()
        return result.json()
    except Exception as e:
        st.error(f"Error fetching playlist: {e}")
        return None

# Function to get user profile
def get_user_profile(token):
    url = "https://api.spotify.com/v1/me"
    headers = get_auth_header(token)
    try:
        result = get(url, headers=headers)
        result.raise_for_status()
        return result.json()
    except Exception as e:
        st.error(f"Error fetching user profile: {e}")
        return None

# Initialize session state
if 'token' not in st.session_state:
    st.session_state.token = None

# Streamlit UI
st.title("🎵 Spotify Metadata Explorer")
st.markdown("Extract track, album, artist, and playlist metadata from Spotify")

# Sidebar
with st.sidebar:
    st.header("Spotify API Credentials")
    st.markdown("[Get your credentials](https://developer.spotify.com/dashboard)")
    st.info("⚠️ Add this Redirect URI in your app settings:\n\n`http://localhost:8501`")
    
    client_id = st.text_input("Client ID")
    client_secret = st.text_input("Client Secret", type="password")
    
    st.divider()
    
    query_params = st.query_params
    
    if client_id and client_secret:
        if 'code' in query_params and not st.session_state.token:
            code = query_params['code']
            token = get_token_from_code(client_id, client_secret, code)
            if token:
                st.session_state.token = token
                st.success("✅ Authenticated!")
                st.query_params.clear()
                st.rerun()
        
        if not st.session_state.token:
            auth_url = get_auth_url(client_id)
            st.markdown("### 🔐 Login Required")
            st.markdown(f"[**Click here to login with Spotify**]({auth_url})")
        else:
            st.success("✅ Authenticated")
            
            # Show user profile
            user = get_user_profile(st.session_state.token)
            if user:
                st.markdown(f"**Logged in as:** {user.get('display_name', 'User')}")
                if user.get('images'):
                    st.image(user['images'][0]['url'], width=100)
            
            if st.button("🚪 Logout"):
                st.session_state.token = None
                st.rerun()

# Main content
if st.session_state.token:
    tabs = st.tabs(["🎵 Track", "💿 Album", "🎤 Artist", "📋 Playlist", "👤 Profile"])
    
    # TRACK TAB
    with tabs[0]:
        st.subheader("Get Track Metadata")
        track_link = st.text_input("Enter Spotify track link", placeholder="https://open.spotify.com/track/...")
        
        if st.button("Get Track Info", type="primary", key="track_btn"):
            if track_link:
                track_id = extract_id(track_link, type="track")
                if track_id:
                    with st.spinner("Fetching track..."):
                        track = get_track_details(st.session_state.token, track_id)
                    
                    if track:
                        col1, col2 = st.columns([1, 2])
                        with col1:
                            if track.get('album', {}).get('images'):
                                st.image(track['album']['images'][0]['url'])
                        with col2:
                            st.markdown(f"### {track['name']}")
                            st.markdown(f"**Artist(s):** {', '.join([a['name'] for a in track['artists']])}")
                            st.markdown(f"**Album:** {track['album']['name']}")
                            st.markdown(f"**Duration:** {track['duration_ms'] // 1000 // 60}:{(track['duration_ms'] // 1000) % 60:02d}")
                            st.markdown(f"**Popularity:** {track['popularity']}/100")
                            st.markdown(f"**Explicit:** {'Yes' if track['explicit'] else 'No'}")
                            st.markdown(f"**Release Date:** {track['album']['release_date']}")
                        
                        # Create DataFrame
                        track_data = {
                            'Track Name': track['name'],
                            'Artists': ', '.join([a['name'] for a in track['artists']]),
                            'Album': track['album']['name'],
                            'Duration (s)': track['duration_ms'] // 1000,
                            'Popularity': track['popularity'],
                            'Explicit': track['explicit'],
                            'Release Date': track['album']['release_date'],
                            'Track Number': track['track_number'],
                            'Spotify URL': track['external_urls']['spotify']
                        }
                        df = pd.DataFrame([track_data])
                        st.dataframe(df, use_container_width=True)
                        
                        csv = df.to_csv(index=False).encode('utf-8')
                        st.download_button("📥 Download CSV", csv, "track_metadata.csv", "text/csv")
    
    # ALBUM TAB
    with tabs[1]:
        st.subheader("Get Album Metadata")
        album_link = st.text_input("Enter Spotify album link", placeholder="https://open.spotify.com/album/...")
        
        if st.button("Get Album Info", type="primary", key="album_btn"):
            if album_link:
                album_id = extract_id(album_link, type="album")
                if album_id:
                    with st.spinner("Fetching album..."):
                        album = get_album_details(st.session_state.token, album_id)
                    
                    if album:
                        col1, col2 = st.columns([1, 2])
                        with col1:
                            if album.get('images'):
                                st.image(album['images'][0]['url'])
                        with col2:
                            st.markdown(f"### {album['name']}")
                            st.markdown(f"**Artist(s):** {', '.join([a['name'] for a in album['artists']])}")
                            st.markdown(f"**Release Date:** {album['release_date']}")
                            st.markdown(f"**Total Tracks:** {album['total_tracks']}")
                            st.markdown(f"**Popularity:** {album['popularity']}/100")
                            st.markdown(f"**Label:** {album.get('label', 'N/A')}")
                            st.markdown(f"**Genres:** {', '.join(album.get('genres', ['N/A']))}")
                        
                        st.markdown("### Track List")
                        tracks_data = []
                        for track in album['tracks']['items']:
                            tracks_data.append({
                                'Track #': track['track_number'],
                                'Name': track['name'],
                                'Artists': ', '.join([a['name'] for a in track['artists']]),
                                'Duration (s)': track['duration_ms'] // 1000,
                                'Explicit': track['explicit']
                            })
                        df = pd.DataFrame(tracks_data)
                        st.dataframe(df, use_container_width=True)
                        
                        csv = df.to_csv(index=False).encode('utf-8')
                        st.download_button("📥 Download CSV", csv, "album_tracks.csv", "text/csv")
    
    # ARTIST TAB
    with tabs[2]:
        st.subheader("Get Artist Metadata")
        artist_link = st.text_input("Enter Spotify artist link", placeholder="https://open.spotify.com/artist/...")
        
        if st.button("Get Artist Info", type="primary", key="artist_btn"):
            if artist_link:
                artist_id = extract_id(artist_link, type="artist")
                if artist_id:
                    with st.spinner("Fetching artist..."):
                        artist = get_artist_details(st.session_state.token, artist_id)
                    
                    if artist:
                        col1, col2 = st.columns([1, 2])
                        with col1:
                            if artist.get('images'):
                                st.image(artist['images'][0]['url'])
                        with col2:
                            st.markdown(f"### {artist['name']}")
                            st.markdown(f"**Followers:** {artist['followers']['total']:,}")
                            st.markdown(f"**Popularity:** {artist['popularity']}/100")
                            st.markdown(f"**Genres:** {', '.join(artist.get('genres', ['N/A']))}")
                        
                        artist_data = {
                            'Name': artist['name'],
                            'Followers': artist['followers']['total'],
                            'Popularity': artist['popularity'],
                            'Genres': ', '.join(artist.get('genres', [])),
                            'Spotify URL': artist['external_urls']['spotify']
                        }
                        df = pd.DataFrame([artist_data])
                        st.dataframe(df, use_container_width=True)
                        
                        csv = df.to_csv(index=False).encode('utf-8')
                        st.download_button("📥 Download CSV", csv, "artist_metadata.csv", "text/csv")
    
    # PLAYLIST TAB
    with tabs[3]:
        st.subheader("Get Playlist Metadata")
        playlist_link = st.text_input("Enter Spotify playlist link", placeholder="https://open.spotify.com/playlist/...")
        
        if st.button("Get Playlist Info", type="primary", key="playlist_btn"):
            if playlist_link:
                playlist_id = extract_id(playlist_link, type="playlist")
                if playlist_id:
                    with st.spinner("Fetching playlist..."):
                        playlist = get_playlist_details(st.session_state.token, playlist_id)
                    
                    if playlist:
                        col1, col2 = st.columns([1, 2])
                        with col1:
                            if playlist.get('images'):
                                st.image(playlist['images'][0]['url'])
                        with col2:
                            st.markdown(f"### {playlist['name']}")
                            st.markdown(f"**Owner:** {playlist['owner']['display_name']}")
                            st.markdown(f"**Total Tracks:** {playlist['tracks']['total']}")
                            st.markdown(f"**Followers:** {playlist['followers']['total']:,}")
                            st.markdown(f"**Public:** {'Yes' if playlist['public'] else 'No'}")
                            if playlist.get('description'):
                                st.markdown(f"**Description:** {playlist['description']}")
                        
                        st.markdown("### Track List")
                        tracks_data = []
                        for item in playlist['tracks']['items']:
                            if item['track']:
                                track = item['track']
                                tracks_data.append({
                                    'Name': track['name'],
                                    'Artists': ', '.join([a['name'] for a in track['artists']]),
                                    'Album': track['album']['name'],
                                    'Duration (s)': track['duration_ms'] // 1000,
                                    'Popularity': track['popularity'],
                                    'Added At': item['added_at']
                                })
                        
                        if tracks_data:
                            df = pd.DataFrame(tracks_data)
                            st.dataframe(df, use_container_width=True)
                            
                            csv = df.to_csv(index=False).encode('utf-8')
                            st.download_button("📥 Download CSV", csv, "playlist_tracks.csv", "text/csv")
    
    # PROFILE TAB
    with tabs[4]:
        st.subheader("Your Spotify Profile")
        
        if st.button("Get My Profile", type="primary", key="profile_btn"):
            with st.spinner("Fetching profile..."):
                user = get_user_profile(st.session_state.token)
            
            if user:
                col1, col2 = st.columns([1, 2])
                with col1:
                    if user.get('images'):
                        st.image(user['images'][0]['url'])
                with col2:
                    st.markdown(f"### {user.get('display_name', 'User')}")
                    st.markdown(f"**Email:** {user.get('email', 'N/A')}")
                    st.markdown(f"**Country:** {user.get('country', 'N/A')}")
                    st.markdown(f"**Followers:** {user.get('followers', {}).get('total', 0):,}")
                    st.markdown(f"**Product:** {user.get('product', 'N/A').title()}")
                    st.markdown(f"**User ID:** {user['id']}")
                
                user_data = {
                    'Display Name': user.get('display_name', ''),
                    'Email': user.get('email', ''),
                    'Country': user.get('country', ''),
                    'Followers': user.get('followers', {}).get('total', 0),
                    'Product': user.get('product', ''),
                    'Spotify URL': user['external_urls']['spotify']
                }
                df = pd.DataFrame([user_data])
                st.dataframe(df, use_container_width=True)
                
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download CSV", csv, "my_profile.csv", "text/csv")

else:
    st.info("👈 Please enter your credentials and login with Spotify in the sidebar to get started")
    
    st.markdown("### 📋 What This App Can Fetch:")
    st.markdown("""
    - ✅ **Track Info:** Name, artists, album, duration, popularity
    - ✅ **Album Info:** Release date, tracks, images, label
    - ✅ **Artist Info:** Name, genres, followers, popularity
    - ✅ **Playlist Info:** User-created playlists and their tracks
    - ✅ **User Profile:** Your Spotify account information
    
    ⚠️ **Note:** Audio features (danceability, energy, etc.) are NOT available in Development Mode.
    """)