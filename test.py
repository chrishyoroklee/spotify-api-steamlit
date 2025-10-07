import requests
import base64

client_id = "88b7a428b55d4dc3993edde5a1eab613"
client_secret = "6ea04b4fd7d243bb8462629b192c38da"

# Get token
auth_string = f"{client_id}:{client_secret}"
auth_base64 = base64.b64encode(auth_string.encode()).decode()

response = requests.post(
    "https://accounts.spotify.com/api/token",
    headers={
        "Authorization": f"Basic {auth_base64}",
        "Content-Type": "application/x-www-form-urlencoded"
    },
    data={"grant_type": "client_credentials"}
)

print(f"Token request status: {response.status_code}")
token_data = response.json()
print(f"Token: {token_data.get('access_token')[:20]}...")

# Test audio features endpoint
token = token_data['access_token']
track_id = "7C0LbWtZgDYjmaSuz10AeD"  # The track that failed

audio_response = requests.get(
    f"https://api.spotify.com/v1/audio-features/{track_id}",
    headers={"Authorization": f"Bearer {token}"}
)

print(f"\nAudio features request status: {audio_response.status_code}")
print(f"Response: {audio_response.text}")

if audio_response.status_code == 200:
    print("\n✅ SUCCESS! Audio features retrieved:")
    print(audio_response.json())
else:
    print(f"\n❌ FAILED with status {audio_response.status_code}")
    print("Response headers:", dict(audio_response.headers))