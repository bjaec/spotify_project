from flask import Flask, request, render_template, jsonify
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import os
#use plotly instead because more aesthetic version of matplotlib 
import plotly.express as px
import plotly.utils
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
    df['Song Title'] = [track['name'] for track in top_tracks['items']]
    df = df[['Song Title'] + audio_features]
    df.set_index('Song Title', inplace=True)

    df = df * 100 

    fig = px.bar(df, x=df.index, y=audio_features, barmode='group', title="Your Top Tracks' Vibes 🎧",
                 labels={"value": "Percentage", "variable": "Audio Feature", "index": "Song Title"})
    
    # Customize hover information
    for trace in fig.data:
        trace.hovertemplate = '<b>Audio Feature</b>: %{x}<br><b>Percentage</b>: %{y:.2f}%<extra></extra>'
        trace.name = trace.name.split("=")[-1]  # Update trace name to be the audio feature name

    TEST
    
    # Update the layout to set background color and text color
    fig.update_layout(
        plot_bgcolor='black',
        paper_bgcolor='black',
        font=dict(
            family="Poppins, sans-serif",
            size=12,
            color='white'
        ),
        xaxis=dict(showgrid=False, zeroline=False, title='Song Title'),
        yaxis=dict(showgrid=False, zeroline=False, title='Percentage (%)'),
        autosize=True,
        height=800,  # Adjust this as needed
        colorway=['#FFDDC1', '#FFABAB', '#FFC3A0', '#FF677D', '#D4A5A5', '#392F5A', '#31A2AC', '#61C0BF']
    )

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('results.html', graphJSON=graphJSON)
    

if __name__ == '__main__':
    app.run(debug=True, port=8888)
#debug = tree allows us to save changes and refresh the page to reflect updates to the code
