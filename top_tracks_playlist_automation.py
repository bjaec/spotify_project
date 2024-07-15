import os
import time
from dotenv import load_dotenv
from datetime import datetime, timedelta
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from apscheduler.schedulers.background import BackgroundScheduler

load_dotenv()

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv("CLIENT_ID"),
    client_secret=os.getenv("CLIENT_SECRET"),
    redirect_uri="http://localhost:8888/callback",
    scope="user-top-read playlist-modify-public playlist-modify-private"
))

def get_top_tracks_for_month():
    # Get the top 50 tracks for the last month
    top_tracks = sp.current_user_top_tracks(limit=50, time_range='short_term')
    return top_tracks['items']

def create_or_update_playlist(playlist_name, top_tracks):
    # Search for the playlist
    playlists = sp.current_user_playlists()
    playlist_id = None

    for playlist in playlists['items']:
        if playlist['name'] == playlist_name:
            playlist_id = playlist['id']
            break
    
    # If playlist does not exist, create it
    if not playlist_id:
        playlist = sp.user_playlist_create(sp.current_user()['id'], playlist_name, public=True)
        playlist_id = playlist['id']
    
    # Get the track URIs
    track_uris = [track['uri'] for track in top_tracks]
    
    # Clear the playlist
    sp.playlist_replace_items(playlist_id, track_uris)
    print(f"Updated playlist '{playlist_name}' with top tracks.")

def update_top_tracks_playlist():
    top_tracks = get_top_tracks_for_month()
    create_or_update_playlist("Top 50 Songs of the Month", top_tracks)

scheduler = BackgroundScheduler()
scheduler.add_job(update_top_tracks_playlist, 'interval', weeks=1, next_run_time=datetime.now() + timedelta(seconds=5))
scheduler.start()

# To keep the script running
try:
    while True:
        time.sleep(2)
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()
