"""
Spotify Metadata Fetcher - Standalone Python Script
Fetch track, album, artist, and playlist metadata from Spotify API
Works with Development Mode (no audio features)
"""

import requests
import base64
import json
import re
import pandas as pd
from typing import Optional, Dict, List

class SpotifyMetadataFetcher:
    """Fetches metadata from Spotify API using Client Credentials flow"""
    
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = None
        self._authenticate()
    
    def _authenticate(self):
        """Get access token from Spotify"""
        auth_string = f"{self.client_id}:{self.client_secret}"
        auth_base64 = base64.b64encode(auth_string.encode()).decode()
        
        url = "https://accounts.spotify.com/api/token"
        headers = {
            "Authorization": f"Basic {auth_base64}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {"grant_type": "client_credentials"}
        
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        
        self.token = response.json()["access_token"]
        print("✅ Successfully authenticated with Spotify API")
    
    def _get_headers(self) -> Dict[str, str]:
        """Return authorization headers"""
        return {"Authorization": f"Bearer {self.token}"}
    
    def _extract_id(self, spotify_link: str, type: str = "track") -> Optional[str]:
        """Extract Spotify ID from URL"""
        patterns = {
            "track": r"open\.spotify\.com\/track\/([a-zA-Z0-9]+)",
            "album": r"open\.spotify\.com\/album\/([a-zA-Z0-9]+)",
            "artist": r"open\.spotify\.com\/artist\/([a-zA-Z0-9]+)",
            "playlist": r"open\.spotify\.com\/playlist\/([a-zA-Z0-9]+)"
        }
        match = re.search(patterns.get(type, patterns["track"]), spotify_link)
        return match.group(1) if match else None
    
    def get_track(self, track_url_or_id: str) -> Optional[Dict]:
        """
        Get track metadata
        
        Args:
            track_url_or_id: Spotify track URL or ID
            
        Returns:
            Dictionary with track metadata
        """
        track_id = self._extract_id(track_url_or_id, "track") or track_url_or_id
        
        url = f"https://api.spotify.com/v1/tracks/{track_id}"
        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()
        
        track = response.json()
        
        # Format the data
        return {
            'id': track['id'],
            'name': track['name'],
            'artists': ', '.join([a['name'] for a in track['artists']]),
            'album': track['album']['name'],
            'duration_ms': track['duration_ms'],
            'duration_formatted': f"{track['duration_ms'] // 1000 // 60}:{(track['duration_ms'] // 1000) % 60:02d}",
            'popularity': track['popularity'],
            'explicit': track['explicit'],
            'release_date': track['album']['release_date'],
            'track_number': track['track_number'],
            'spotify_url': track['external_urls']['spotify'],
            'preview_url': track.get('preview_url'),
            'album_image': track['album']['images'][0]['url'] if track['album']['images'] else None
        }
    
    def get_album(self, album_url_or_id: str) -> Optional[Dict]:
        """
        Get album metadata including all tracks
        
        Args:
            album_url_or_id: Spotify album URL or ID
            
        Returns:
            Dictionary with album metadata and track list
        """
        album_id = self._extract_id(album_url_or_id, "album") or album_url_or_id
        
        url = f"https://api.spotify.com/v1/albums/{album_id}"
        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()
        
        album = response.json()
        
        tracks = []
        for track in album['tracks']['items']:
            tracks.append({
                'track_number': track['track_number'],
                'name': track['name'],
                'artists': ', '.join([a['name'] for a in track['artists']]),
                'duration_ms': track['duration_ms'],
                'duration_formatted': f"{track['duration_ms'] // 1000 // 60}:{(track['duration_ms'] // 1000) % 60:02d}",
                'explicit': track['explicit'],
                'id': track['id']
            })
        
        return {
            'id': album['id'],
            'name': album['name'],
            'artists': ', '.join([a['name'] for a in album['artists']]),
            'release_date': album['release_date'],
            'total_tracks': album['total_tracks'],
            'popularity': album['popularity'],
            'label': album.get('label'),
            'genres': ', '.join(album.get('genres', [])),
            'spotify_url': album['external_urls']['spotify'],
            'album_image': album['images'][0]['url'] if album['images'] else None,
            'tracks': tracks
        }
    
    def get_artist(self, artist_url_or_id: str) -> Optional[Dict]:
        """
        Get artist metadata
        
        Args:
            artist_url_or_id: Spotify artist URL or ID
            
        Returns:
            Dictionary with artist metadata
        """
        artist_id = self._extract_id(artist_url_or_id, "artist") or artist_url_or_id
        
        url = f"https://api.spotify.com/v1/artists/{artist_id}"
        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()
        
        artist = response.json()
        
        return {
            'id': artist['id'],
            'name': artist['name'],
            'followers': artist['followers']['total'],
            'popularity': artist['popularity'],
            'genres': ', '.join(artist.get('genres', [])),
            'spotify_url': artist['external_urls']['spotify'],
            'artist_image': artist['images'][0]['url'] if artist['images'] else None
        }
    
    def get_playlist(self, playlist_url_or_id: str) -> Optional[Dict]:
        """
        Get playlist metadata including all tracks
        
        Args:
            playlist_url_or_id: Spotify playlist URL or ID
            
        Returns:
            Dictionary with playlist metadata and track list
        """
        playlist_id = self._extract_id(playlist_url_or_id, "playlist") or playlist_url_or_id
        
        url = f"https://api.spotify.com/v1/playlists/{playlist_id}"
        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()
        
        playlist = response.json()
        
        tracks = []
        for item in playlist['tracks']['items']:
            if item['track']:
                track = item['track']
                tracks.append({
                    'name': track['name'],
                    'artists': ', '.join([a['name'] for a in track['artists']]),
                    'album': track['album']['name'],
                    'duration_ms': track['duration_ms'],
                    'duration_formatted': f"{track['duration_ms'] // 1000 // 60}:{(track['duration_ms'] // 1000) % 60:02d}",
                    'popularity': track['popularity'],
                    'added_at': item['added_at'],
                    'id': track['id']
                })
        
        return {
            'id': playlist['id'],
            'name': playlist['name'],
            'owner': playlist['owner']['display_name'],
            'total_tracks': playlist['tracks']['total'],
            'followers': playlist['followers']['total'],
            'public': playlist['public'],
            'description': playlist.get('description', ''),
            'spotify_url': playlist['external_urls']['spotify'],
            'playlist_image': playlist['images'][0]['url'] if playlist['images'] else None,
            'tracks': tracks
        }
    
    def save_to_csv(self, data: Dict, filename: str, include_tracks: bool = True):
        """
        Save metadata to CSV file
        
        Args:
            data: Dictionary with metadata
            filename: Output CSV filename
            include_tracks: For albums/playlists, save tracks to separate file
        """
        # Save main data
        main_data = {k: v for k, v in data.items() if k != 'tracks'}
        df = pd.DataFrame([main_data])
        df.to_csv(filename, index=False)
        print(f"✅ Saved to {filename}")
        
        # Save tracks if present
        if include_tracks and 'tracks' in data and data['tracks']:
            tracks_filename = filename.replace('.csv', '_tracks.csv')
            df_tracks = pd.DataFrame(data['tracks'])
            df_tracks.to_csv(tracks_filename, index=False)
            print(f"✅ Saved tracks to {tracks_filename}")


# Example usage
if __name__ == "__main__":
    # Replace with your credentials
    CLIENT_ID = "your_client_id_here"
    CLIENT_SECRET = "your_client_secret_here"
    
    try:
        # Initialize the fetcher
        fetcher = SpotifyMetadataFetcher(CLIENT_ID, CLIENT_SECRET)
        
        # Example 1: Get track metadata
        print("\n=== TRACK EXAMPLE ===")
        track = fetcher.get_track("https://open.spotify.com/track/7C0LbWtZgDYjmaSuz10AeD")
        print(f"Track: {track['name']} by {track['artists']}")
        print(f"Album: {track['album']}")
        print(f"Duration: {track['duration_formatted']}")
        print(f"Popularity: {track['popularity']}/100")
        fetcher.save_to_csv(track, "track_metadata.csv")
        
        # Example 2: Get album metadata
        print("\n=== ALBUM EXAMPLE ===")
        album = fetcher.get_album("https://open.spotify.com/album/1A2GTWGtFfWp7KSQTwWOyo")
        print(f"Album: {album['name']} by {album['artists']}")
        print(f"Release Date: {album['release_date']}")
        print(f"Total Tracks: {album['total_tracks']}")
        print(f"Tracks:")
        for track in album['tracks'][:5]:  # Show first 5
            print(f"  {track['track_number']}. {track['name']} ({track['duration_formatted']})")
        fetcher.save_to_csv(album, "album_metadata.csv")
        
        # Example 3: Get artist metadata
        print("\n=== ARTIST EXAMPLE ===")
        artist = fetcher.get_artist("https://open.spotify.com/artist/06HL4z0CvFAxyc27GXpf02")
        print(f"Artist: {artist['name']}")
        print(f"Followers: {artist['followers']:,}")
        print(f"Popularity: {artist['popularity']}/100")
        print(f"Genres: {artist['genres']}")
        fetcher.save_to_csv(artist, "artist_metadata.csv")
        
        # Example 4: Get playlist metadata
        print("\n=== PLAYLIST EXAMPLE ===")
        playlist = fetcher.get_playlist("https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M")
        print(f"Playlist: {playlist['name']} by {playlist['owner']}")
        print(f"Total Tracks: {playlist['total_tracks']}")
        print(f"Followers: {playlist['followers']:,}")
        print(f"First 5 tracks:")
        for track in playlist['tracks'][:5]:
            print(f"  • {track['name']} by {track['artists']}")
        fetcher.save_to_csv(playlist, "playlist_metadata.csv")
        
    except Exception as e:
        print(f"❌ Error: {e}")