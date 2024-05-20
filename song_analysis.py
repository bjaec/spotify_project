import spotipy 
from spotipy.oauth2 import SpotifyOAuth
#allows us to retrieve credentials just once (instead of everytime)
import streamlit as st
#using streamlit for a more aesthetic UI than just jupyter notebook
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

from dotenv import load_dotenv
load_dotenv()

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

#⚱️4️⃣빠 music analysis

playlist_id = os.getenv("PLAYLIST_ID1")  # Replace with your playlist ID

print("HI")
print(playlist_id)

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

playlist_id = os.getenv("PLAYLIST_ID2")  # Replace with your playlist ID


playlist_tracks = sp.playlist_tracks(playlist_id, fields='items.track.id,items.track.name', limit=100)

playlist_track_ids = [item['track']['id'] for item in playlist_tracks['items']]
playlist_audio_features = sp.audio_features(playlist_track_ids)

df_playlist = pd.DataFrame(playlist_audio_features)
df_playlist['track_name'] = [item['track']['name'] for item in playlist_tracks['items']]

df_playlist = df_playlist[['track_name','danceability', 'energy', 'speechiness', 'valence']]
df_playlist.set_index('track_name', inplace=True)

st.subheader('Audio Features for Playlist "HYPE music"')
st.bar_chart(df_playlist, height=500)

#comparing tempos in HYPE vs. 3 am mood

def get_playlist_data(playlist_id):
    playlist_tracks = sp.playlist_tracks(playlist_id, fields='items.track.id,items.track.name,total', limit=100)
    playlist_track_ids = [item['track']['id'] for item in playlist_tracks['items'] if item['track']]
    playlist_track_names = [item['track']['name'] for item in playlist_tracks['items'] if item['track']]
    playlist_audio_features = sp.audio_features(playlist_track_ids)
    df_playlist = pd.DataFrame(playlist_audio_features)
    df_playlist['track_name'] = playlist_track_names
    df_playlist = df_playlist[['track_name', 'tempo']]
    return df_playlist

# Replace with your playlist IDs
playlist_id_1 = os.getenv("PLAYLIST_ID2")
playlist_id_2 = os.getenv("PLAYLIST_ID3")

# Fetch data for both playlists
df_playlist_1 = get_playlist_data(playlist_id_1)
df_playlist_2 = get_playlist_data(playlist_id_2)

# Add a column to distinguish the playlists
df_playlist_1['playlist'] = 'HYPE'
df_playlist_2['playlist'] = '3 am mood'

# Combine the dataframes
df_combined = pd.concat([df_playlist_1, df_playlist_2])

# Apply Seaborn styling with a dark background and white text
sns.set(style="darkgrid", rc={"axes.facecolor": "black", "grid.color": "white", "text.color": "white", 
                              "axes.labelcolor": "white", "xtick.color": "white", "ytick.color": "white",
                              "axes.edgecolor": "white", "font.family": "Comic Sans MS"})

# Plotting
plt.figure(figsize=(12, 8))
boxplot = sns.boxplot(data=df_combined, x="playlist", y="tempo", palette="Set2")
boxplot.set_title('Tempo Distribution Comparison between Two Playlists', fontsize=16, color="white")
boxplot.set_xlabel('Playlist', fontsize=14, color="white")
boxplot.set_ylabel('Tempo', fontsize=14, color="white")
boxplot.tick_params(labelsize=12, colors="white")

# Additional customization for aesthetics
sns.despine(left=True)
plt.xticks(rotation=45, color="white")
plt.tight_layout()

# Set the figure background color to black
plt.gcf().set_facecolor('black')

# Display the plot in Streamlit
st.pyplot(plt)
