from setuptools import setup, find_packages

setup(
    name="spotify-playlist-extractor",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "Flask>=2.3.3",
        "spotipy>=2.23.0",
        "python-dotenv>=1.0.0",
        "tqdm>=4.66.1",
    ],
    python_requires=">=3.7",
    author="Your Name",
    description="A Flask web app to extract Spotify playlists",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
)