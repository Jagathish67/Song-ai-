import os
from flask import Flask, render_template, request, jsonify, redirect
import yt_dlp  # This is yt-dlp, which pafy should use
import pafy
import vlc
import openai
from gtts import gTTS
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Set pafy backend to "internal" to use yt-dlp
os.environ["PAFY_BACKEND"] = "internal"

# Initialize Flask app
app = Flask(__name__)

# OpenAI API Key (Replace with your real key)
OPENAI_API_KEY = "your_openai_api_key"  # Set your OpenAI API Key here
openai.api_key = OPENAI_API_KEY

# Spotify API credentials (Replace with your real credentials)
SPOTIPY_CLIENT_ID = "your_spotify_client_id"  # Set your Spotify Client ID here
SPOTIPY_CLIENT_SECRET = "your_spotify_client_secret"  # Set your Spotify Client Secret here
SPOTIPY_REDIRECT_URI = "http://localhost:5000/callback"  # Set your Spotify Redirect URI here

# Spotify authorization
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                               client_secret=SPOTIPY_CLIENT_SECRET,
                                               redirect_uri=SPOTIPY_REDIRECT_URI,
                                               scope="user-library-read"))

# VLC player instance
player = None

# Search for a song on YouTube
def search_youtube(song_name):
    search_query = f"ytsearch:{song_name}"
    ydl_opts = {"quiet": True, "format": "bestaudio"}
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(search_query, download=False)
        if "entries" in info:
            url = info["entries"][0]["url"]
            print(f"Found YouTube URL: {url}")  # Log the URL returned by yt_dlp
            # Check if the URL is a valid YouTube video URL
            if 'youtube.com' in url and 'v=' in url:
                video_id = url.split('v=')[1]
                if len(video_id) == 11:
                    print("Valid YouTube URL")
                    return url
                else:
                    print("Invalid YouTube video ID")
            else:
                print("Not a valid YouTube video URL")
    return None

# Search for a song on Spotify
def search_spotify(song_name):
    result = sp.search(song_name, limit=1)
    if result['tracks']['items']:
        track = result['tracks']['items'][0]
        return track['external_urls']['spotify']
    return None

# Play song from YouTube
def play_song(url):
    global player
    try:
        video = pafy.new(url)
        best_audio = video.getbestaudio()
        media = vlc.MediaPlayer(best_audio.url)
        media.play()
        player = media
    except Exception as e:
        print(f"Error playing song: {e}")
        return jsonify({"status": "error", "message": "Error playing song"}), 500

# Home route - Main page
@app.route('/')
def index():
    return render_template("index.html")  # This will render your index.html page

# Login route to handle Spotify OAuth
@app.route('/login')
def login():
    auth_url = sp.auth_manager.get_authorize_url()
    return redirect(auth_url)

# Callback route for Spotify OAuth
@app.route('/callback')
def callback():
    token_info = sp.auth_manager.get_access_token(request.args['code'])
    sp = spotipy.Spotify(auth=token_info['access_token'])
    return jsonify({"status": "Spotify OAuth Successful", "token_info": token_info})

# Play song route - Post request
@app.route('/play', methods=['POST'])
def play():
    data = request.json
    song_name = data.get("song")

    # Search for song either on Spotify or YouTube
    url = search_spotify(song_name) or search_youtube(song_name)

    if url:
        play_song(url)
        return jsonify({"status": "playing", "url": url})
    return jsonify({"status": "error", "message": "Song not found"}), 404

# Pause song route
@app.route('/pause', methods=['POST'])
def pause():
    if player:
        player.pause()
        return jsonify({"status": "paused"})
    return jsonify({"status": "error", "message": "No song playing"}), 400

# Resume song route
@app.route('/resume', methods=['POST'])
def resume():
    if player:
        player.play()
        return jsonify({"status": "resumed"})
    return jsonify({"status": "error", "message": "No song playing"}), 400

# Stop song route
@app.route('/stop', methods=['POST'])
def stop():
    if player:
        player.stop()
        return jsonify({"status": "stopped"})
    return jsonify({"status": "error", "message": "No song playing"}), 400

# Route to search Spotify directly
@app.route("/play_spotify", methods=['POST'])
def play_spotify():
    song_name = request.json.get("song")
    result = sp.search(song_name, limit=1)
    if result['tracks']['items']:
        track = result['tracks']['items'][0]
        track_url = track['external_urls']['spotify']
        return jsonify({"status": "found", "url": track_url})
    return jsonify({"status": "error", "message": "Song not found on Spotify"}), 404

if __name__ == '__main__':
    app.run(debug=True)
