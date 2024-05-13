import spotipy 
from spotipy.oauth2 import SpotifyOAuth
#allows us to retrieve credentials just once (instead of everytime)
import streamlit as st
#using streamlit for a more aesthetic UI than just jupyter notebook
import pandas as pd
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

st.set_page_config(page_title='Spotify Song Analysis', page_icon=':musical_note:')
st.title('Analysis for Top Songs')
st.write('Discover Insights for Spotify Learning Habits')

top_tracks = sp.current_user_top_tracks(limit=10, time_range='short_term')
track_ids = [track['id'] for track in top_tracks['items']]
audio_features = sp.audio_features(track_ids)

df=pd.DataFrame(audio_features)
df['track_name'] = [track['name'] for track in top_tracks['items']]
df = df[['track_name', 'danceability', 'energy', 'valence']]
df.set_index('track_name', inplace=True)

st.subheader('Audio Feature for Top Tracks')
st.bar_chart(df, height=500)

