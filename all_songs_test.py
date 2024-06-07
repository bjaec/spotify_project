from flask import Flask, request, render_template, jsonify
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import os
#use plotly instead because more aesthetic version of matplotlib 
import plotly.express as px
import plotly.graph_objects as go
import json

app = Flask(__name__)

load_dotenv()
#get the client id and secret to access spotify API

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_url = "http://localhost:8888/callback"

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id,
        client_secret,
        redirect_url,
        scope='user-top-read'
    )
)

#home page
@app.route('/')
def home():
    return render_template('index.html')

#analysis page
@app.route('/analyze', methods=['GET'])
def analyze_page():
    return render_template('analyze.html')

#results of analysis page
@app.route('/analyze', methods=['POST'])
def analyze():
    num_songs = int(request.form.get('num_songs', 10))
    if num_songs < 1 or num_songs > 50:
        return jsonify({'error': 'Number of songs must be between 1 and 50'}), 400
    
    time_range = request.form.get('time_range', 'short_term')
    audio_features = request.form.getlist('audio_features')

    top_tracks = sp.current_user_top_tracks(limit=num_songs, time_range=time_range)
    track_ids = [track['id'] for track in top_tracks['items']]
    features = sp.audio_features(track_ids)

    df = pd.DataFrame(features)
    df['Song Title'] = [f"{rank+1}. {track['name']}" for rank, track in enumerate(top_tracks['items'])]
    df = df[['Song Title'] + audio_features]
    df.set_index('Song Title', inplace=True)

    df = df * 100 

    # Create figure
    fig = go.Figure()

   # Define pastel colors for specific features
    feature_colors = {
        'energy':'#FFD700',  # Darker pastel yellow (Gold)
        'danceability': '#E57373',   # Darker pastel red
        'default': '#B0E0E6'  # Light pastel blue for others
    }


    # Add traces for each audio feature
    for feature in audio_features:
        color = feature_colors.get(feature, feature_colors['default'])
        fig.add_trace(go.Bar(
            x=df.index,
            y=df[feature],
            name=feature.capitalize(),
            marker_color=color,
            hovertemplate=f'<b>Audio Feature</b>: {feature.capitalize()}<br><b>Song Title</b>: %{{x}}<br><b>{feature.capitalize()} Percentage</b>: %{{y:.2f}}%<extra></extra>'
        ))


    fig.update_layout(
        title="Your Top Tracks' Vibes 🎧",
        plot_bgcolor='black',
        paper_bgcolor='black',
        font=dict(
            family="Poppins, sans-serif",
            size=12,
            color='white'
        ),
        xaxis=dict(showgrid=False, zeroline=False, title='Song Title'),
        yaxis=dict(showgrid=False, zeroline=False, title='Percentage (%)'),
        barmode='group',
        autosize=True,
        margin=dict(l=40, r=40, t=60, b=40),
        height=700,
        width=1200
    )

    graphJSON = fig.to_json()

    return render_template('results.html', graphJSON=graphJSON)
    

if __name__ == '__main__':
    app.run(debug=True, port=8888)
#debug = tree allows us to save changes and refresh the page to reflect updates to the code
