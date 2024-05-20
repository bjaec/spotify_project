import spotipy 
from spotipy.oauth2 import SpotifyOAuth
#allows us to retrieve credentials just once (instead of everytime)
import streamlit as st
#using streamlit for a more aesthetic UI than just jupyter notebook
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_url = "http://localhost:8888/callback"

sp=spotipy.Spotify(
    #new instance of SpotifyOAuth
    auth_manager=SpotifyOAuth(
        client_id, 
        client_secret, 
        redirect_url, 
        scope='user-top-read'
        #scope just reads top liked songs rn
    )
)

#10 top songs analysis

st.set_page_config(page_title='Spotify Song Analysis', page_icon=':musical_note:')
st.title('Song Analysis')
st.write('Discover Insights for Spotify Listening Habits')

top_tracks = sp.current_user_top_tracks(limit=10, time_range='short_term')
track_ids = [track['id'] for track in top_tracks['items']]
audio_features = sp.audio_features(track_ids)

df=pd.DataFrame(audio_features)
df['track_name'] = [track['name'] for track in top_tracks['items']]
df = df[['track_name', 'danceability', 'energy', 'valence']]
df.set_index('track_name', inplace=True)

st.subheader('Audio Feature for Top 10 Tracks')
st.bar_chart(df, height=500)

#⚱️4️⃣빠 music analysis

playlist_id = "5opLvMHIBYpi62Dgw04Be5"  # Replace with your playlist ID
playlist_tracks = sp.playlist_tracks(playlist_id, fields='items.track.id,items.track.name', limit=100)

playlist_track_ids = [item['track']['id'] for item in playlist_tracks['items']]
playlist_audio_features = sp.audio_features(playlist_track_ids)

df_playlist = pd.DataFrame(playlist_audio_features)
df_playlist['track_name'] = [item['track']['name'] for item in playlist_tracks['items']]
df_playlist = df_playlist[['track_name', 'acousticness', 'valence', 'danceability']]
df_playlist.set_index('track_name', inplace=True)

st.subheader('Audio Features for Playlist "⚱️4️⃣빠 music"')
st.bar_chart(df_playlist, height=500)

#HYPE music analysis

playlist_id = "1aLX8sx2S53CW1CISAMCwX"  # Replace with your playlist ID
playlist_tracks = sp.playlist_tracks(playlist_id, fields='items.track.id,items.track.name', limit=100)

playlist_track_ids = [item['track']['id'] for item in playlist_tracks['items']]
playlist_audio_features = sp.audio_features(playlist_track_ids)

df_playlist = pd.DataFrame(playlist_audio_features)
df_playlist['track_name'] = [item['track']['name'] for item in playlist_tracks['items']]

df_playlist = df_playlist[['track_name','danceability', 'energy', 'speechiness', 'valence']]
df_playlist.set_index('track_name', inplace=True)

st.subheader('Audio Features for Playlist "HYPE music"')
st.bar_chart(df_playlist, height=500)

#summer '24 music analysis

playlist_id = "3dJwTKrfuPyu7yjOpSUsFr"  # Replace with your playlist ID
playlist_tracks = sp.playlist_tracks(playlist_id, fields='items.track.id,items.track.name', limit=100)

playlist_track_ids = [item['track']['id'] for item in playlist_tracks['items']]
playlist_audio_features = sp.audio_features(playlist_track_ids)

df_playlist = pd.DataFrame(playlist_audio_features)
df_playlist['track_name'] = [item['track']['name'] for item in playlist_tracks['items']]

df_playlist = df_playlist[['track_name','danceability', 'energy', 'valence', 'acousticness']]
df_playlist.set_index('track_name', inplace=True)

st.subheader('Audio Features for Playlist "summer 2024 music"')
st.bar_chart(df_playlist, height=500)

#3 am mood music analysis

playlist_id = "6nb3fBWOkMpl1SP54w8dgs"  # Replace with your playlist ID
playlist_tracks = sp.playlist_tracks(playlist_id, fields='items.track.id,items.track.name', limit=100)

playlist_track_ids = [item['track']['id'] for item in playlist_tracks['items']]
playlist_audio_features = sp.audio_features(playlist_track_ids)

df_playlist = pd.DataFrame(playlist_audio_features)
df_playlist['track_name'] = [item['track']['name'] for item in playlist_tracks['items']]

df_playlist = df_playlist[['track_name','danceability', 'energy', 'valence', 'acousticness']]
df_playlist.set_index('track_name', inplace=True)

st.subheader('Audio Features for Playlist "3 am mood music"')
st.bar_chart(df_playlist, height=500)

#3 am mood music analysis

playlist_id = "6nb3fBWOkMpl1SP54w8dgs"  # Replace with your playlist ID
playlist_tracks = sp.playlist_tracks(playlist_id, fields='items.track.id,items.track.name', limit=100)

playlist_track_ids = [item['track']['id'] for item in playlist_tracks['items']]
playlist_audio_features = sp.audio_features(playlist_track_ids)

df_playlist = pd.DataFrame(playlist_audio_features)
df_playlist['track_name'] = [item['track']['name'] for item in playlist_tracks['items']]

df_playlist = df_playlist[['track_name','danceability', 'energy', 'valence', 'acousticness']]
df_playlist.set_index('track_name', inplace=True)

st.subheader('Audio Features for Playlist "3 am mood music"')
st.bar_chart(df_playlist, height=500)

#3 am mood music analysis

playlist_id = "6nb3fBWOkMpl1SP54w8dgs"  # Replace with your playlist ID
playlist_tracks = sp.playlist_tracks(playlist_id, fields='items.track.id,items.track.name', limit=100)

playlist_track_ids = [item['track']['id'] for item in playlist_tracks['items']]
playlist_audio_features = sp.audio_features(playlist_track_ids)

df_playlist = pd.DataFrame(playlist_audio_features)
df_playlist['track_name'] = [item['track']['name'] for item in playlist_tracks['items']]

df_playlist = df_playlist[['track_name','loudness']]
df_playlist.set_index('track_name', inplace=True)

st.subheader('Audio Features for Playlist "3 am mood music"')
st.bar_chart(df_playlist, height=500)

#hippity hoppity mood music analysis

playlist_id = "4GHljgfSZKtfI9Wx5ptQcm"  # Replace with your playlist ID
playlist_tracks = sp.playlist_tracks(playlist_id, fields='items.track.id,items.track.name', limit=100)

playlist_track_ids = [item['track']['id'] for item in playlist_tracks['items']]
playlist_audio_features = sp.audio_features(playlist_track_ids)

df_playlist = pd.DataFrame(playlist_audio_features)
df_playlist['track_name'] = [item['track']['name'] for item in playlist_tracks['items']]

df_playlist = df_playlist[['track_name','speechiness', 'energy', 'acousticness']]
df_playlist.set_index('track_name', inplace=True)

st.subheader('Audio Features for Playlist "hippity hoppity 🐸 music"')
st.bar_chart(df_playlist, height=500)

#hippity hoppity mood music analysis

playlist_id = "4GHljgfSZKtfI9Wx5ptQcm"  # Replace with your playlist ID
playlist_tracks = sp.playlist_tracks(playlist_id, fields='items.track.id,items.track.name', limit=100)

playlist_track_ids = [item['track']['id'] for item in playlist_tracks['items']]
playlist_audio_features = sp.audio_features(playlist_track_ids)

df_playlist = pd.DataFrame(playlist_audio_features)
df_playlist['track_name'] = [item['track']['name'] for item in playlist_tracks['items']]

df_playlist = df_playlist[['track_name','loudness']]
df_playlist.set_index('track_name', inplace=True)

st.subheader('Audio Features for Playlist "hippity hoppity 🐸 music"')
st.bar_chart(df_playlist, height=500)
