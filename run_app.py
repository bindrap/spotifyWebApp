#!/usr/bin/env python3
"""
Simple runner script for the Spotify Playlist Extractor
"""
import os
import sys

def main():
    # Add current directory to Python path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Import and run the Flask app
    from app import app
    
    print("🎵 Starting Spotify Playlist Extractor...")
    print("📱 Open your browser and go to: http://127.0.0.1:5000")
    print("🔧 Make sure you have your Spotify app credentials ready!")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 50)
    
    app.run(debug=True, port=5000, host='127.0.0.1')

if __name__ == "__main__":
    main()