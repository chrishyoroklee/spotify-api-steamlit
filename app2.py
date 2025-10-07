import streamlit as st
import pandas as pd
import base64
from requests import post, get
import json
import re

# Function to get the token
def get_token(client_id, client_secret):
    try:
        auth_string = client_id + ":" + client_secret
        auth_bytes = auth_string.encode("utf-8")
        auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")
        url = "https://accounts.spotify.com/api/token"
        headers = {
            "Authorization": "Basic " + auth_base64,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {"grant_type": "client_credentials"}
        result = post(url, headers=headers, data=data)
        result.raise_for_status()
        json_result = json.loads(result.content)
        token = json_result.get("access_token")
        return token
    except Exception as e:
        st.error(f"Error getting token: {e}")
        return None

# Function to get the authorization header
def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

# Function to get audio features for a single track
def get_audio_features(token, track_id):
    url = f"https://api.spotify.com/v1/audio-features/{track_id}"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    try:
        result.raise_for_status()
        json_result = result.json()
        return json_result
    except Exception as e:
        st.error(f"Error while fetching audio features: {e}")
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
        st.error(f"Error fetching track details: {e}")
        return None

# Extract track or playlist ID from the Spotify link
def extract_id(spotify_link, type="track"):
    if type == "track":
        match = re.search(r"open\.spotify\.com\/track\/([a-zA-Z0-9]+)", spotify_link)
    elif type == "playlist":
        match = re.search(r"open\.spotify\.com\/playlist\/([a-zA-Z0-9]+)", spotify_link)
    if match:
        return match.group(1)
    else:
        st.error(f"Invalid Spotify {type} link. Please make sure it's a valid URL.")
        return None

# Function to get playlist tracks
def get_playlist_tracks(token, playlist_id):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = {"Authorization": f"Bearer {token}"}
    all_tracks = []
    
    with st.spinner("Fetching playlist tracks..."):
        while url:
            try:
                response = get(url, headers=headers, params={"limit": 100})
                response.raise_for_status()
                playlist_data = response.json()
                all_tracks.extend(playlist_data.get("items", []))
                url = playlist_data.get("next")
            except Exception as e:
                st.error(f"Error fetching playlist tracks: {e}")
                return None
    
    return all_tracks

# Function to get audio features for multiple tracks (batched)
def get_audio_features_for_tracks(token, track_ids):
    all_features = []
    batch_size = 100
    
    with st.spinner(f"Fetching audio features for {len(track_ids)} tracks..."):
        for i in range(0, len(track_ids), batch_size):
            batch = track_ids[i:i + batch_size]
            url = "https://api.spotify.com/v1/audio-features"
            headers = {"Authorization": f"Bearer {token}"}
            params = {"ids": ",".join(batch)}
            
            try:
                response = get(url, headers=headers, params=params)
                response.raise_for_status()
                audio_features_data = response.json()
                features = audio_features_data.get("audio_features", [])
                all_features.extend(features)
            except Exception as e:
                st.error(f"Error fetching audio features for batch: {e}")
                continue
    
    return all_features

# Streamlit UI setup
st.title("🎵 Spotify Audio Features Finder")
st.markdown("Extract audio features from Spotify tracks and playlists")

# Sidebar for credentials
with st.sidebar:
    st.header("Spotify API Credentials")
    st.markdown("[Get your credentials here](https://developer.spotify.com/dashboard)")
    client_id = st.text_input("Client ID")
    client_secret = st.text_input("Client Secret", type="password")

# Main content
tab1, tab2 = st.tabs(["🎵 Single Track", "📋 Playlist"])

with tab1:
    st.subheader("Get Audio Features for a Single Track")
    song_link = st.text_input("Enter Spotify song link", placeholder="https://open.spotify.com/track/...")
    
    if st.button("Get Song Audio Features", type="primary"):
        if not client_id or not client_secret:
            st.error("⚠️ Please enter your Client ID and Client Secret in the sidebar.")
        elif not song_link:
            st.error("⚠️ Please enter a Spotify song link.")
        else:
            token = get_token(client_id, client_secret)
            if token:
                track_id = extract_id(song_link, type="track")
                if track_id:
                    with st.spinner("Fetching audio features..."):
                        audio_features = get_audio_features(token, track_id)
                        track_details = get_track_details(token, track_id)
                    
                    if audio_features and track_details:
                        # Display track info
                        st.success("✅ Audio features retrieved successfully!")
                        col1, col2 = st.columns([1, 3])
                        with col1:
                            if track_details.get('album', {}).get('images'):
                                st.image(track_details['album']['images'][0]['url'])
                        with col2:
                            st.markdown(f"**{track_details['name']}**")
                            st.markdown(f"*{', '.join([artist['name'] for artist in track_details['artists']])}*")
                        
                        # Create DataFrame with track name
                        audio_features['track_name'] = track_details['name']
                        audio_features['artist'] = ', '.join([artist['name'] for artist in track_details['artists']])
                        
                        df_single_track = pd.DataFrame([audio_features])
                        
                        # Reorder columns to show track info first
                        cols = ['track_name', 'artist'] + [col for col in df_single_track.columns if col not in ['track_name', 'artist']]
                        df_single_track = df_single_track[cols]
                        
                        st.dataframe(df_single_track, use_container_width=True)
                        
                        csv = df_single_track.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="📥 Download audio features as CSV",
                            data=csv,
                            file_name='single_track_audio_features.csv',
                            mime='text/csv',
                        )
                    else:
                        st.error("❌ Could not fetch audio features.")
            else:
                st.error("❌ Invalid credentials. Please check your Client ID and Client Secret.")

with tab2:
    st.subheader("Get Audio Features for a Playlist")
    playlist_link = st.text_input("Enter Spotify playlist link", placeholder="https://open.spotify.com/playlist/...")
    
    if st.button("Get Playlist Audio Features", type="primary"):
        if not client_id or not client_secret:
            st.error("⚠️ Please enter your Client ID and Client Secret in the sidebar.")
        elif not playlist_link:
            st.error("⚠️ Please enter a Spotify playlist link.")
        else:
            token = get_token(client_id, client_secret)
            if token:
                playlist_id = extract_id(playlist_link, type="playlist")
                if playlist_id:
                    playlist_tracks = get_playlist_tracks(token, playlist_id)
                    
                    if playlist_tracks:
                        # Filter out None tracks and extract valid track IDs
                        valid_tracks = [
                            track for track in playlist_tracks 
                            if track.get('track') and track['track'].get('id')
                        ]
                        
                        if not valid_tracks:
                            st.error("❌ No valid tracks found in the playlist.")
                        else:
                            st.info(f"Found {len(valid_tracks)} tracks in playlist")
                            
                            track_ids = [track['track']['id'] for track in valid_tracks]
                            audio_features = get_audio_features_for_tracks(token, track_ids)
                            
                            if audio_features:
                                # Filter out None values in audio features
                                audio_features = [f for f in audio_features if f is not None]
                                
                                # Add track names and artists
                                for i, feature in enumerate(audio_features):
                                    if i < len(valid_tracks):
                                        track = valid_tracks[i]['track']
                                        feature['track_name'] = track.get('name', 'Unknown')
                                        feature['artist'] = ', '.join([artist['name'] for artist in track.get('artists', [])])
                                
                                df_playlist = pd.DataFrame(audio_features)
                                
                                # Reorder columns
                                cols = ['track_name', 'artist'] + [col for col in df_playlist.columns if col not in ['track_name', 'artist']]
                                df_playlist = df_playlist[cols]
                                
                                st.success(f"✅ Retrieved audio features for {len(audio_features)} tracks!")
                                st.dataframe(df_playlist, use_container_width=True)
                                
                                csv = df_playlist.to_csv(index=False).encode('utf-8')
                                st.download_button(
                                    label="📥 Download playlist audio features as CSV",
                                    data=csv,
                                    file_name='playlist_audio_features.csv',
                                    mime='text/csv',
                                )
                            else:
                                st.error("❌ Could not fetch audio features for the tracks.")
                    else:
                        st.error("❌ Failed to fetch playlist tracks.")
            else:
                st.error("❌ Invalid credentials. Please check your Client ID and Client Secret.")