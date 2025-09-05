# 🎵 Spotify Playlist Extractor Web App

A user-friendly Flask web application that allows anyone to extract their Spotify playlists and liked songs as text files. No technical knowledge required!

## ✨ Features

- **Easy Setup**: Web interface guides users through getting Spotify credentials
- **User-Friendly**: No command line required - everything happens in your browser
- **Progress Tracking**: Real-time progress bars show export status
- **Selective Export**: Choose individual playlists or export everything at once
- **Secure**: Credentials are stored locally in your `.env` file

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Clone or download this project
# Navigate to the project folder

# Install required packages
pip install -r requirements.txt
```

### 2. Run the Application

```bash
# Option 1: Run directly
python app.py

# Option 2: Use the runner script
python run_app.py
```

### 3. Open in Browser

Go to: `http://127.0.0.1:5000`

### 4. Follow the Web Interface

The app will guide you through:
1. Setting up Spotify credentials
2. Connecting to your Spotify account
3. Selecting and downloading playlists

## 🔑 Getting Spotify Credentials

The web app includes detailed instructions, but here's a quick overview:

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Log in with your Spotify account
3. Click "Create App"
   - **App Name**: "My Playlist Extractor" (or any name)
   - **App Description**: "Extract my playlists"
   - **Redirect URI**: `http://127.0.0.1:5000/callback`
   - **API**: Check "Web API"
4. Save and open your new app
5. Go to "Settings" 
6. Copy your **Client ID** and **Client Secret**
7. Paste them into the web app

## 📁 File Structure

```
spotify-playlist-extractor/
├── app.py                 # Main Flask application
├── run_app.py            # Simple runner script
├── requirements.txt      # Python dependencies
├── .env                  # Your Spotify credentials (auto-created)
├── .cache               # Spotify auth cache (auto-created)
├── templates/           # HTML templates
│   ├── base.html        # Base template
│   ├── index.html       # Home page
│   └── dashboard.html   # Playlist dashboard
└── Playlists/           # Exported playlist files (auto-created)
    ├── likedSongs.txt
    ├── My_Awesome_Playlist.txt
    └── ...
```

## 📋 Exported File Format

Each playlist is exported as a text file with one song per line:

```
Artist Name - Song Title
The Beatles - Hey Jude
Queen - Bohemian Rhapsody
...
```

## 🔒 Privacy & Security

- All credentials are stored locally on your computer
- No data is sent to external servers (except Spotify's official API)
- You can clear credentials anytime using the "Logout" button
- The app only requests read permissions for your playlists

## 🛠️ Troubleshooting

### "ModuleNotFoundError"
Make sure you've installed dependencies:
```bash
pip install -r requirements.txt
```

### "Invalid client" or authentication errors
- Double-check your Client ID and Client Secret
- Make sure the Redirect URI in your Spotify app settings is exactly: `http://127.0.0.1:5000/callback`
- Try clearing credentials and setting them up again

### Browser shows "This site can't be reached"
- Make sure the Flask app is running (you should see output in your terminal)
- Check that you're going to the correct URL: `http://127.0.0.1:5000`
- Try refreshing the page

### Downloads not working
- Make sure you're authenticated with Spotify (green checkmark on home page)
- Check the progress modal for error messages
- Verify you have playlists in your Spotify account

## 🔄 Updating Credentials

If you need to change your Spotify app credentials:
1. Click "Logout" in the web app
2. Enter your new Client ID and Client Secret
3. Re-authenticate with Spotify

## 📝 Requirements

- Python 3.7 or higher
- A Spotify account (free or premium)
- A Spotify Developer app (free to create)

## 🎯 Future Features

- [ ] Download files directly through browser
- [ ] Export to different formats (CSV, JSON)
- [ ] Batch export with progress tracking
- [ ] Playlist metadata export
- [ ] Duplicate song detection

## 💡 Tips

- **Large playlists**: The app handles large playlists efficiently with progress tracking
- **Multiple users**: Each user needs their own Spotify Developer app
- **Backup**: The exported text files can be easily backed up or shared
- **Re-run anytime**: You can export updated playlists whenever you want

## 🐛 Issues?

If you encounter any problems:
1. Check the troubleshooting section above
2. Make sure all requirements are installed
3. Verify your Spotify app settings match the requirements
4. Clear your browser cache and try again

## 📄 License

This project is for personal use. Make sure to comply with Spotify's Terms of Service.