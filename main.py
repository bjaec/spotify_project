from flask import Flask, request, render_template, jsonify
import os
from dotenv import load_dotenv

import spotipy
from spotipy.oauth2 import SpotifyOAuth #to implement OAuth (allows me to just access for permission once)

from requests import post, get, delete  # Add this line

import pandas as pd #for dataframes
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

def fetch_all_user_playlists():
    url = "https://api.spotify.com/v1/me/playlists"
    headers = {"Authorization": "Bearer " + sp.auth_manager.get_access_token(as_dict=False)}
    playlists = []
    while url:
        response = get(url, headers=headers)
        data = response.json()
        playlists.extend(data['items'])
        url = data.get('next')
    return playlists

# Custom context processor to add zip to Jinja2 context
@app.context_processor
def utility_processor():
    return dict(zip=zip)

#home page
@app.route('/')
def home():
    print("Home Page Accessed")
    return render_template('index.html')

#analysis page
@app.route('/analyze-options', methods=['GET'])
def analyze_options():
    print("Analyze Options Page Accessed")
    return render_template('analyze_options.html')

@app.route('/analyze-all', methods=['GET'])
def analyze_all():
    return render_template('analyze_all_songs.html')

@app.route('/analyze-playlist', methods=['GET'])
def analyze_by_playlist():
    playlists = fetch_all_user_playlists() 
    return render_template('analyze_by_playlist.html', playlists=playlists)

# Results page route for handling analysis results
@app.route('/analyze-all-songs', methods=['POST'])
def analyze_all_songs():
    num_songs = int(request.form.get('num_songs', 10))
    if num_songs < 1 or num_songs > 50:
        return jsonify({'error': 'Number of songs must be between 1 and 50'}), 400

    time_range = request.form.get('time_range', 'short_term')
    percentage_features = request.form.getlist('percentage_features')
    individual_feature = request.form.get('individual_features')

    # Retrieve top tracks and their audio features from Spotify
    top_tracks = sp.current_user_top_tracks(limit=num_songs, time_range=time_range)
    track_ids = [track['id'] for track in top_tracks['items']]
    features = sp.audio_features(track_ids)

    # Create a DataFrame from the audio features
    df = pd.DataFrame(features)
    df['Song Title'] = [f"{rank+1}. {track['name']}" for rank, track in enumerate(top_tracks['items'])]

    # Handle percentage features
    if percentage_features:
        return handle_percentage_features(df, percentage_features)

    # Handle individual feature
    elif individual_feature:
        return handle_individual_feature(df, individual_feature)

    return jsonify({'error': 'No features selected'}), 400

@app.route('/analyze-playlist-songs', methods=['POST'])
def analyze_playlist_songs():
    playlist_id = request.form.get('playlist_id')
    num_songs = int(request.form.get('num_songs', 10))
    if num_songs < 1 or num_songs > 50:
        return jsonify({'error': 'Number of songs must be between 1 and 50'}), 400

    # Retrieve playlist tracks and their audio features from Spotify
    tracks = sp.playlist_tracks(playlist_id, limit=num_songs)
    track_ids = [track['track']['id'] for track in tracks['items']]
    features = sp.audio_features(track_ids)

    # Create a DataFrame from the audio features
    df = pd.DataFrame(features)
    df['Song Title'] = [f"{rank+1}. {track['track']['name']}" for rank, track in enumerate(tracks['items'])]

    # Handle percentage features
    percentage_features = request.form.getlist('percentage_features')
    if percentage_features:
        return handle_percentage_features(df, percentage_features)

    # Handle individual feature
    individual_feature = request.form.get('individual_features')
    if individual_feature:
        return handle_individual_feature(df, individual_feature)

    return jsonify({'error': 'No features selected'}), 400

def handle_percentage_features(df, percentage_features):
    """
    Handle analysis and visualization of percentage features.
    """
    df = df[['Song Title'] + percentage_features]
    df.set_index('Song Title', inplace=True)
    df[percentage_features] = df[percentage_features] * 100  # Convert to percentages

    # Descriptions for each audio feature
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

    # Create bar chart figure for percentage features
    fig = go.Figure()
    feature_colors = {
        'danceability': '#AF7AC5',  # Darker pastel red
        'energy': '#F7DC6F',  # Darker pastel yellow (Gold)
        'speechiness': '#34495E',  
        'acousticness': '#D2B48C',  # Light pastel brown
        'instrumentalness': '#FFA07A',  # Light pastel orange
        'valence': '#138D75',  # Light pastel green
    }

    pie_charts = []
    fun_messages = []

    for feature in percentage_features:
        color = feature_colors[feature]
        fig.add_trace(go.Bar(
            x=df.index,
            y=df[feature],
            name=feature.capitalize(),
            marker_color=color,
            hovertemplate=f'<b>Audio Feature</b>: {feature.capitalize()}<br><b>Song Title</b>: %{{x}}<br><b>{feature.capitalize()} Percentage</b>: %{{y:.2f}}%<extra></extra>'
        ))

        # Create pie chart for the feature
        avg_value = df[feature].mean()
        pie_fig = create_pie_chart(feature, avg_value, feature_colors)
        pie_charts.append(pie_fig.to_json())

        # Generate fun message based on thresholds
        message = generate_fun_message(feature, avg_value)
        fun_messages.append(message)

    fig.update_layout(
        title="Your Top Tracks' Vibes 🎧",
        plot_bgcolor='black', #set background color to black
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

    #useful in web applications where the backend generates the data and the frontend renders the visualization.
    graphJSON = fig.to_json()
    #why to json? Serialization: fig.to_json() serializes the Plotly figure into a JSON string, making it easy to send via HTTP as part of the response. 
    #This is necessary because HTTP communication requires data to be in a text format.

    #also Frontend Integration: By converting the figure to JSON, you can include the serialized figure data in your HTML template.
    # On the client side (in the browser), JavaScript can parse the JSON and render the Plotly chart.

    return render_template('results.html', graphJSON=graphJSON, pie_charts=pie_charts, fun_messages=fun_messages, feature_descriptions=feature_descriptions)

def create_pie_chart(feature, avg_value, feature_colors):
    """
    Create a pie chart for the given feature and average value.
    """
    labels = ['Average', 'Remainder']
    values = [avg_value, 100 - avg_value]
    color = feature_colors.get(feature)  

    fig = go.Figure(data=[go.Pie(labels=labels, values=values, marker=dict(colors=[color, '#000000']))])  # '#17202A' is for the remainder

    fig.update_layout(
        title=f'{feature.capitalize()} Average:',
        showlegend=False,
        annotations=[dict(text=f'{avg_value:.1f}%', x=0.5, y=0.5, 
                    font_size=50, font_color='white', showarrow=False, font=dict(color='white', 
                    size=80, family="Poppins, sans-serif"))],
        margin=dict(l=20, r=20, t=30, b=20),
        paper_bgcolor='black',
        plot_bgcolor='black',
        font=dict(color='white', family="Poppins, sans-serif")
    )
    return fig

def generate_fun_message(feature, avg_value):
    """
    Generate a fun message based on the average value of the feature.
    """
    if feature == 'danceability':
        if avg_value > 70:
            return "very energetic and upbeat playlist!"
        elif avg_value < 30:
            return "not very energetic"
        else:
            return "It's got some groove"
    elif feature == 'energy':
        if avg_value > 70:
            return "High energy vibes!"
        elif avg_value < 30:
            return "Chill and mellow."
        else:
            return "A balanced energy mix."
    elif feature == 'speechiness':
        if avg_value > 70:
            return "A lot of talking here!"
        elif avg_value < 30:
            return "Is this classical?"
        else:
            return "A good mix of speech and music. Like when I talk frfr."
    elif feature == 'acousticness':
        if avg_value > 70:
            return "Very acoustic, earthy vibes!"
        elif avg_value < 30:
            return "Not much acoustic type shit."
        else:
            return "Some acoustic elements."
    elif feature == 'instrumentalness':
        if avg_value > 70:
            return "Mostly instrumental tracks!"
        elif avg_value < 30:
            return "Lots of vocals here."
        else:
            return "A good mix of instrumentals and vocals."
    elif feature == 'valence':
        if avg_value > 70:
            return "Happy and cheerful tunes!"
        elif avg_value < 30:
            return "Quite somber and serious."
        else:
            return "A mix of happy and sad."
    # Add more messages for other features if needed
    return ""

#this method hasnt been properly developed yet
def handle_individual_feature(df, individual_feature):
    """
    Handle analysis and visualization of an individual feature.
    """
    df = df[['Song Title', individual_feature]]
    df.set_index('Song Title', inplace=True)

    # Create bar chart figure for the individual feature
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
    return render_template('results.html', graphJSON=graphJSON)

#below is logic for removing duplicates 

@app.route('/remove-duplicates')
def remove_duplicates():
    return render_template('remove_duplicates_loading.html')

@app.route('/process-remove-duplicates', methods=['POST'])
def process_remove_duplicates():
    # Fetch all saved tracks
    tracks = fetch_all_saved_tracks()
    duplicate_ids, duplicate_details = identify_duplicates(tracks)

    duplicate_songs = {"Liked Songs": duplicate_details}

    if duplicate_ids:
        remove_tracks_in_batches(duplicate_ids)

    return render_template('remmove_duplicates_results.html', duplicate_songs=duplicate_songs)

def fetch_all_saved_tracks():
    url = "https://api.spotify.com/v1/me/tracks"
    headers = {"Authorization": "Bearer " + sp.auth_manager.get_access_token(as_dict=False)}
    all_tracks = []
    while url:
        response = get(url, headers=headers)  # Using get from requests
        json_response = response.json()
        all_tracks.extend(json_response['items'])
        url = json_response.get('next')
    return all_tracks

def identify_duplicates(tracks):
    unique_tracks = {}
    duplicates = []
    duplicate_details = []

    for item in tracks:
        track = item['track']
        track_id = track['id']
        artist_name = track['artists'][0]['name']
        track_name = track['name']
        track_key = (artist_name.lower(), track_name.lower())

        if track_key in unique_tracks:
            duplicates.append(track_id)
            duplicate_details.append((track_name, artist_name))
        else:
            unique_tracks[track_key] = track_id

    return duplicates, duplicate_details

def remove_tracks_in_batches(track_ids, batch_size=50):
    url = "https://api.spotify.com/v1/me/tracks"
    headers = {"Authorization": "Bearer " + sp.auth_manager.get_access_token(as_dict=False)}
    batches = [track_ids[i:i + batch_size] for i in range(0, len(track_ids), batch_size)]
    for batch in batches:
        data = json.dumps({"ids": batch})
        response = delete(url, headers=headers, data=data)  # Using delete from requests
        if response.status_code not in [200, 202]:
            return False
    return True

if __name__ == '__main__':
    app.run(debug=True, port=8888)
#debug = true allows us to save changes and refresh the page to reflect updates to the code
