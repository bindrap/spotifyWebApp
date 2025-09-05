from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import os
import re
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv, set_key
import threading
import time

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# Global variables for progress tracking
download_progress = {}
download_status = {}

# Configuration
REDIRECT_URI = "http://127.0.0.1:5000/callback"
SCOPE = "user-library-read playlist-read-private playlist-read-collaborative"
LIMIT = 50
CACHE_PATH = ".cache"
PLAYLIST_DIR = "Playlists"
ENV_FILE = ".env"

# Ensure directories exist
os.makedirs(PLAYLIST_DIR, exist_ok=True)

# Load environment variables
load_dotenv()

def safe_filename(name: str) -> str:
    """Sanitize playlist names into safe filenames"""
    return re.sub(r'[^a-zA-Z0-9_\-]', '_', name).strip("_") + ".txt"

def update_env_file(client_id, client_secret):
    """Update the .env file with new credentials"""
    try:
        set_key(ENV_FILE, "CLIENT_ID", client_id)
        set_key(ENV_FILE, "CLIENT_SECRET", client_secret)
        set_key(ENV_FILE, "REDIRECT_URI", REDIRECT_URI)
        return True
    except Exception as e:
        print(f"Error updating .env file: {e}")
        return False

def get_spotify_client():
    """Get authenticated Spotify client"""
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    
    if not client_id or not client_secret or not client_id.strip() or not client_secret.strip():
        return None
    
    try:
        auth_manager = SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=REDIRECT_URI,
            scope=SCOPE,
            cache_path=CACHE_PATH
        )
        
        # Check if we have a valid cached token
        token_info = auth_manager.get_cached_token()
        if not token_info:
            return None
            
        sp = spotipy.Spotify(auth_manager=auth_manager)
        
        # Test the connection by making a simple API call
        sp.current_user()
        return sp
    except Exception as e:
        print(f"Error creating Spotify client: {e}")
        return None

def export_liked_songs(sp, session_id):
    """Export liked songs with progress tracking"""
    try:
        download_status[session_id] = "Fetching liked songs..."
        download_progress[session_id] = 0
        
        total_results = sp.current_user_saved_tracks(limit=1, offset=0)['total']
        
        results = []
        offset = 0
        processed = 0
        
        while True:
            response = sp.current_user_saved_tracks(limit=LIMIT, offset=offset)
            tracks = response['items']
            if not tracks:
                break
            
            for item in tracks:
                track = item['track']
                if track and track.get('artists'):
                    artists = ", ".join([artist['name'] for artist in track['artists']])
                    title = track['name']
                    results.append(f"{artists} - {title}")
            
            processed += len(tracks)
            download_progress[session_id] = int((processed / total_results) * 100) if total_results > 0 else 100
            offset += LIMIT
        
        # Save to file
        liked_file = os.path.join(PLAYLIST_DIR, "likedSongs.txt")
        with open(liked_file, "w", encoding="utf-8") as f:
            for line in results:
                f.write(line + "\n")
        
        download_status[session_id] = f"Completed! Exported {len(results)} liked songs to {liked_file}"
        download_progress[session_id] = 100
        
    except Exception as e:
        download_status[session_id] = f"Error: {str(e)}"
        download_progress[session_id] = 0

def export_playlist(sp, playlist_id, playlist_name, session_id):
    """Export a single playlist with progress tracking"""
    try:
        download_status[session_id] = f"Exporting playlist: {playlist_name}..."
        download_progress[session_id] = 0
        
        playlist = sp.playlist(playlist_id)
        total = playlist["tracks"]["total"]
        
        results = []
        offset = 0
        processed = 0
        
        while True:
            tracks = sp.playlist_tracks(playlist_id, limit=LIMIT, offset=offset)["items"]
            if not tracks:
                break
            
            for item in tracks:
                track = item.get("track")
                if not track or not track.get("artists"):
                    continue
                artists = ", ".join([a["name"] for a in track["artists"] if a.get("name")])
                title = track.get("name", "Unknown Track")
                results.append(f"{artists} - {title}")
            
            processed += len(tracks)
            download_progress[session_id] = int((processed / total) * 100) if total > 0 else 100
            offset += LIMIT
        
        # Save to file
        filename = os.path.join(PLAYLIST_DIR, safe_filename(playlist_name))
        with open(filename, "w", encoding="utf-8") as f:
            for line in results:
                f.write(line + "\n")
        
        download_status[session_id] = f"Completed! Exported {len(results)} songs from '{playlist_name}' to {filename}"
        download_progress[session_id] = 100
        
    except Exception as e:
        download_status[session_id] = f"Error: {str(e)}"
        download_progress[session_id] = 0

@app.route('/')
def index():
    """Main page"""
    # Force reload environment variables
    load_dotenv(override=True)
    
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    
    credentials_set = bool(client_id and client_secret and client_id.strip() and client_secret.strip())
    spotify_connected = False
    
    if credentials_set:
        sp = get_spotify_client()
        spotify_connected = sp is not None
    
    print(f"🔍 Status Check - Credentials: {credentials_set}, Connected: {spotify_connected}")
    
    return render_template('index.html', 
                         credentials_set=credentials_set,
                         spotify_connected=spotify_connected)

@app.route('/setup_credentials', methods=['POST'])
def setup_credentials():
    """Handle credentials setup"""
    client_id = request.form.get('client_id', '').strip()
    client_secret = request.form.get('client_secret', '').strip()
    
    if not client_id or not client_secret:
        flash('Please provide both Client ID and Client Secret', 'error')
        return redirect(url_for('index'))
    
    # Clear any existing cache to force re-auth with new credentials
    if os.path.exists(CACHE_PATH):
        os.remove(CACHE_PATH)
    
    # Update environment file
    if update_env_file(client_id, client_secret):
        # Reload environment variables
        load_dotenv(override=True)
        flash('Credentials saved successfully! Now click "Connect to Spotify" to authenticate.', 'success')
    else:
        flash('Error saving credentials. Please try again.', 'error')
    
    return redirect(url_for('index'))

@app.route('/spotify_auth')
def spotify_auth():
    """Initiate Spotify authentication"""
    load_dotenv(override=True)
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    
    if not client_id or not client_secret:
        flash('Please set up your Spotify credentials first', 'error')
        return redirect(url_for('index'))
    
    # Create SpotifyOAuth object and get authorization URL
    auth_manager = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
        cache_path=CACHE_PATH
    )
    
    # Get authorization URL and redirect user to Spotify
    auth_url = auth_manager.get_authorize_url()
    print(f"🔗 Redirecting to Spotify: {auth_url}")
    return redirect(auth_url)

@app.route('/callback')
def callback():
    """Handle Spotify callback"""
    load_dotenv(override=True)
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    
    if not client_id or not client_secret:
        flash('Credentials not found', 'error')
        return redirect(url_for('index'))
    
    # Create SpotifyOAuth object
    auth_manager = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
        cache_path=CACHE_PATH
    )
    
    # Get the authorization code from the callback
    code = request.args.get('code')
    if code:
        try:
            # Exchange code for access token
            token_info = auth_manager.get_access_token(code)
            if token_info:
                print("✅ Successfully authenticated with Spotify!")
                flash('Successfully connected to Spotify!', 'success')
                return redirect(url_for('dashboard'))
        except Exception as e:
            print(f"❌ Error during callback: {e}")
    
    error = request.args.get('error')
    if error:
        print(f"❌ Spotify auth error: {error}")
        flash(f'Spotify authentication failed: {error}', 'error')
    else:
        flash('Failed to connect to Spotify', 'error')
    
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    """Dashboard showing user's playlists"""
    sp = get_spotify_client()
    if not sp:
        flash('Please authenticate with Spotify first', 'error')
        return redirect(url_for('index'))
    
    try:
        # Get user info
        user = sp.current_user()
        user_id = user['id']
        user_name = user['display_name'] or user_id
        
        print(f"✅ Successfully loaded dashboard for user: {user_name}")
        
        # Get user's playlists
        playlists = []
        results = sp.current_user_playlists(limit=50)
        
        while results:
            for playlist in results['items']:
                # Only include playlists owned by the user
                if playlist['owner']['id'] == user_id:
                    playlists.append({
                        'id': playlist['id'],
                        'name': playlist['name'],
                        'tracks': playlist['tracks']['total']
                    })
            
            if results['next']:
                results = sp.next(results)
            else:
                break
        
        # Get liked songs count
        liked_count = sp.current_user_saved_tracks(limit=1)['total']
        
        print(f"📊 Found {len(playlists)} playlists and {liked_count} liked songs")
        
        return render_template('dashboard.html', 
                             user_name=user_name,
                             playlists=playlists,
                             liked_count=liked_count)
    
    except Exception as e:
        print(f"❌ Error loading dashboard: {str(e)}")
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/download_liked')
def download_liked():
    """Download liked songs"""
    sp = get_spotify_client()
    if not sp:
        return jsonify({'error': 'Not authenticated'}), 401
    
    session_id = f"liked_{int(time.time())}"
    download_progress[session_id] = 0
    download_status[session_id] = "Starting..."
    
    # Start download in background thread
    thread = threading.Thread(target=export_liked_songs, args=(sp, session_id))
    thread.daemon = True
    thread.start()
    
    return jsonify({'session_id': session_id})

@app.route('/download_playlist/<playlist_id>')
def download_playlist(playlist_id):
    """Download a specific playlist"""
    sp = get_spotify_client()
    if not sp:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        playlist = sp.playlist(playlist_id)
        playlist_name = playlist['name']
        
        session_id = f"playlist_{playlist_id}_{int(time.time())}"
        download_progress[session_id] = 0
        download_status[session_id] = "Starting..."
        
        # Start download in background thread
        thread = threading.Thread(target=export_playlist, 
                                args=(sp, playlist_id, playlist_name, session_id))
        thread.daemon = True
        thread.start()
        
        return jsonify({'session_id': session_id})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download_all')
def download_all():
    """Download all playlists and liked songs"""
    return jsonify({'message': 'Feature coming soon! For now, please download playlists individually.'}), 200

@app.route('/progress/<session_id>')
def get_progress(session_id):
    """Get download progress"""
    progress = download_progress.get(session_id, 0)
    status = download_status.get(session_id, "Unknown session")
    
    return jsonify({
        'progress': progress,
        'status': status,
        'completed': progress >= 100
    })

@app.route('/clear_credentials')
def clear_credentials():
    """Clear stored credentials and cache"""
    try:
        # Clear the credentials from .env
        if os.path.exists(ENV_FILE):
            set_key(ENV_FILE, "CLIENT_ID", "")
            set_key(ENV_FILE, "CLIENT_SECRET", "")
        
        # Remove Spotify auth cache
        if os.path.exists(CACHE_PATH):
            os.remove(CACHE_PATH)
        
        # Reload environment variables
        load_dotenv(override=True)
        
        flash('Credentials cleared successfully', 'success')
    except Exception as e:
        flash(f'Error clearing credentials: {str(e)}', 'error')
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    print("🎵 Starting Spotify Playlist Extractor...")
    print("📁 Creating directories...")
    os.makedirs(PLAYLIST_DIR, exist_ok=True)
    print(f"📂 Playlist directory: {os.path.abspath(PLAYLIST_DIR)}")
    print(f"📄 Environment file: {os.path.abspath(ENV_FILE)}")
    print("🌐 Starting Flask server...")
    print("📱 Open your browser and go to: http://127.0.0.1:5000")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 50)
    app.run(debug=True, port=5000)