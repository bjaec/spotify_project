from flask import Flask, request, redirect
from dotenv import load_dotenv
import os
import base64
from requests import post, get, delete
#allows us to send post request
import json
import webbrowser

import requests

load_dotenv()

#below is to create local Flask server to access the client and access the token
app = Flask(__name__)

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = "http://localhost:8888/callback"
token = os.getenv("TOKEN")



def create_auth_url():
    scope = "playlist-read-private playlist-modify-private playlist-modify-public user-library-read user-library-modify"
    auth_url = f"https://accounts.spotify.com/authorize?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&scope={scope.replace(' ', '%20')}&show_dialog=true"
    return auth_url

def exchange_code_for_token(code):
    url = "https://accounts.spotify.com/api/token"
    auth_string = f"{client_id}:{client_secret}"
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri
    }
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    return json_result["access_token"]

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if code:
        token = exchange_code_for_token(code)
        return f"Authorization successful! Token: {token}"
    return "No code provided by Spotify."


def fetch_all_saved_tracks(token):
    url = "https://api.spotify.com/v1/me/tracks"
    headers = get_auth_header(token)
    all_tracks = []
    while url:
        response = get(url, headers=headers)
        json_response = json.loads(response.content)
        all_tracks.extend(json_response['items'])
        url = json_response['next']  # Spotify provides the next URL if there are more tracks to fetch

    return all_tracks

def fetch_all_user_playlists(token):
    url = "https://api.spotify.com/v1/me/playlists"
    headers = {"Authorization": "Bearer " + token}
    playlists = []
    while url:
        response = get(url, headers=headers)
        data = response.json()
        playlists.extend(data['items'])
        url = data.get('next')  # Move to the next page of playlists
    return playlists

def fetch_tracks_from_playlist(token, playlist_id):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = {"Authorization": "Bearer " + token}
    tracks = []
    while url:
        response = get(url, headers=headers)
        data = response.json()
        tracks.extend(data['items'])
        url = data.get('next')
    return tracks

def identify_duplicates(tracks):
    unique_tracks = {}
    duplicates = []
    duplicate_details = []  # List to store details of duplicates for logging

    for item in tracks:
        track = item['track']
        track_id = track['id']
        artist_name = track['artists'][0]['name']
        track_name = track['name']
        track_key = (artist_name.lower(), track_name.lower())

        if track_key in unique_tracks:
            duplicates.append(track_id)
            duplicate_details.append((track_name, artist_name))  # Store song title and artist name
        else:
            unique_tracks[track_key] = track_id

    return duplicates, duplicate_details

def remove_tracks_in_batches(token, track_ids, batch_size=50):
    url = "https://api.spotify.com/v1/me/tracks"
    headers = {"Authorization": "Bearer " + token}
    batches = [track_ids[i:i + batch_size] for i in range(0, len(track_ids), batch_size)]
    for batch in batches:
        data = json.dumps({"ids": batch})
        response = delete(url, headers=headers, data=data)
        print(f"Batch Response Status: {response.status_code}, Response Body: {response.text}")
        if response.status_code not in [200, 202]:
            return False  # Return false if any batch fails
    return True

#below is code to start the server to attain access to spotify account 
webbrowser.open(create_auth_url())
app.run(port=8888, debug=True)

playlists = fetch_all_user_playlists(token)

#below is code to remove duplicates from each playlist 
#just prints the # of duplicates rn

for playlist in playlists:
        print(f"Processing playlist: {playlist['name']}")
        tracks = fetch_tracks_from_playlist(token, playlist['id'])
        duplicate_ids, _ = identify_duplicates(tracks)

        if duplicate_ids:
            print(f"Found {len(duplicate_ids)} duplicates in playlist '{playlist['name']}'")
            status = remove_tracks_from_playlist(token, playlist['id'], duplicate_ids)
            print(f"Removed duplicates with status {status}")
        else:
            print("No duplicates found in this playlist.")

#below is code to remove duplicates from all liked songs 
#just prints the # of duplicates rn

# tracks = fetch_all_saved_tracks(token)

# # Identify duplicates
# duplicate_ids, duplicate_details = identify_duplicates(tracks)  # Now also retrieves details

# # Remove duplicates
# if duplicate_ids:
#     result = remove_tracks_in_batches(token, duplicate_ids)
#     for title, artist in duplicate_details:
#             print(f"{title} by {artist}")  # Log the title and artist of duplicates
#     print(f"Removed {len(duplicate_ids)} duplicates with status {result}")
# else:
#     print("No duplicates found.")



