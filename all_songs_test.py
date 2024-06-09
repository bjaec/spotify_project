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
    percentage_features = request.form.getlist('percentage_features')
    individual_feature = request.form.get('individual_features')

    top_tracks = sp.current_user_top_tracks(limit=num_songs, time_range=time_range)
    track_ids = [track['id'] for track in top_tracks['items']]
    features = sp.audio_features(track_ids)

    df = pd.DataFrame(features)
    df['Song Title'] = [f"{rank+1}. {track['name']}" for rank, track in enumerate(top_tracks['items'])]

    #for category 1: percentage features
    
    if percentage_features:
        df = df[['Song Title'] + percentage_features]
        df.set_index('Song Title', inplace=True)
        df[percentage_features] = df[percentage_features] * 100  # Convert to percentages

        feature_descriptions = {
            "danceability": "0% = least danceable and 100% = most danceable based on tempo, rhythm stability, and overall regularity.",
            "energy": "0% = low energy and 100% = high energy based on dynamic range, perceived loudness, timbre, onset rate, and general entropy. Typically, energetic tracks feel fast, loud, and noisy.",
            "speechiness": "TLDR: 0% = less speech & 100% = more speech.\n\nThe more exclusively speech-like the recording (e.g. talk show, audio book, poetry), the closer to 100% the attribute value. Values above 66% describe tracks that are probably made entirely of spoken words. Values between 33% and 66% describe tracks that may contain both music and speech, either in sections or layered, including such cases as rap music. Values below 33% most likely represent music and other non-speech-like tracks.",
            "acousticness": "A confidence measure from 0% to 100% of whether the track is acoustic.",
            "instrumentalness": "TLDR: 0% = more instrumental, less vocals & 100% = less instrumental, more vocals.\n\nPredicts whether a track contains no vocals. 'Ooh' and 'aah' sounds are treated as instrumental in this context. Rap or spoken word tracks are clearly 'vocal'. The closer the instrumentalness value is to 100%, the greater likelihood the track contains no vocal content. Values above 50% are intended to represent instrumental tracks, but confidence is higher as the value approaches 100%",
            "valence": "A measure from 0% to 100% describing the musical positiveness conveyed by a track. Tracks with high valence sound more positive (e.g. happy, cheerful, euphoric), while tracks with low valence sound more negative (e.g. sad, depressed, angry).",
            "key": "The key in which the track is composed.",
            "time_signature": "An estimated time signature. The time signature (meter) is a notational convention to specify how many beats are in each bar (or measure). The time signature ranges from 3 to 7 indicating time signatures of 3/4, to 7/4.",
            "mode": "The modality (major or minor) of the track. Yellow indicates a major key whereas Purple indicates a minor key.",
            "loudness": "The overall loudness of a track in decibels (dB). Loudness values are averaged across the entire track and are useful for comparing relative loudness of tracks. Loudness is the quality of a sound that is the primary psychological correlate of physical strength (amplitude). Values typically range between -60 and 0 dB. A dB value closer to 0 in this case indicates more loudness.",
            "tempo": "The overall estimated tempo of a track in beats per minute (BPM). In musical terminology, tempo is the speed or pace of a given piece and derives directly from the average beat duration."
        }

        feature_descriptions = {
            "danceability": "0% = least danceable and 100% = most danceable based on tempo, rhythm stability, and overall regularity.",
            "energy": "0% = low energy and 100% = high energy based on dynamic range, perceived loudness, timbre, onset rate, and general entropy. Typically, energetic tracks feel fast, loud, and noisy.",
            "speechiness": "TLDR: 0% = less speech & 100% = more speech.\n\nThe more exclusively speech-like the recording (e.g. talk show, audio book, poetry), the closer to 100% the attribute value. Values above 66% describe tracks that are probably made entirely of spoken words. Values between 33% and 66% describe tracks that may contain both music and speech, either in sections or layered, including such cases as rap music. Values below 33% most likely represent music and other non-speech-like tracks.",
            "acousticness": "A confidence measure from 0% to 100% of whether the track is acoustic.",
            "instrumentalness": "TLDR: 0% = more instrumental, less vocals & 100% = less instrumental, more vocals.\n\nPredicts whether a track contains no vocals. 'Ooh' and 'aah' sounds are treated as instrumental in this context. Rap or spoken word tracks are clearly 'vocal'. The closer the instrumentalness value is to 100%, the greater likelihood the track contains no vocal content. Values above 50% are intended to represent instrumental tracks, but confidence is higher as the value approaches 100%",
            "valence": "A measure from 0% to 100% describing the musical positiveness conveyed by a track. Tracks with high valence sound more positive (e.g. happy, cheerful, euphoric), while tracks with low valence sound more negative (e.g. sad, depressed, angry).",
            "key": "The key in which the track is composed.",
            "time_signature": "An estimated time signature. The time signature (meter) is a notational convention to specify how many beats are in each bar (or measure). The time signature ranges from 3 to 7 indicating time signatures of 3/4, to 7/4.",
            "mode": "The modality (major or minor) of the track. Yellow indicates a major key whereas Purple indicates a minor key.",
            "loudness": "The overall loudness of a track in decibels (dB). Loudness values are averaged across the entire track and are useful for comparing relative loudness of tracks. Loudness is the quality of a sound that is the primary psychological correlate of physical strength (amplitude). Values typically range between -60 and 0 dB. A dB value closer to 0 in this case indicates more loudness.",
            "tempo": "The overall estimated tempo of a track in beats per minute (BPM). In musical terminology, tempo is the speed or pace of a given piece and derives directly from the average beat duration."
        }

        # Create figure for percentage features (select multiple)

        fig = go.Figure()
        feature_colors = {
            'energy': '#FFD700',  # Darker pastel yellow (Gold) 
            'danceability': '#E57373',  # Darker pastel red
            'default': '#B0E0E6'  # Light pastel blue for others
        }

        for feature in percentage_features:
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

     #for category 2: individual features (select one)

    elif individual_feature:
        df = df[['Song Title', individual_feature]]
        df.set_index('Song Title', inplace=True)

        # Create figure for individual feature
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df.index,
            y=df[individual_feature],
            name=individual_feature.capitalize(),
            marker_color='#FFB6C1',  # Light pastel pink
            hovertemplate=f'<b>Audio Feature</b>: {individual_feature.capitalize()}<br><b>Song Title</b>: %{{x}}<br><b>{individual_feature.capitalize()} Value</b>: %{{y}}<extra></extra>'
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
            yaxis=dict(showgrid=False, zeroline=False, title='Value'),
            autosize=True,
            margin=dict(l=40, r=40, t=60, b=40),
            height=700,
            width=1200
        )

    graphJSON = fig.to_json()
    return render_template('results.html', graphJSON=graphJSON, feature_descriptions=feature_descriptions)

if __name__ == '__main__':
    app.run(debug=True, port=8888)
#debug = true allows us to save changes and refresh the page to reflect updates to the code
