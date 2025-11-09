from importlib.metadata import version as package_version
import os

from flask import Flask, request
from lyricsgenius import Genius


DEFAULT_HEADERS = {'Content-Type': 'text/plain'}

VERSION = package_version('glyrics')

app = Flask(__name__)
genius = Genius(os.getenv('GENIUS_API_CLIENT_ACCESS_TOKEN'))


@app.route('/api/status/health')
def health():
    return ''


@app.route('/api/status/version')
def version():
    return (VERSION, DEFAULT_HEADERS)


@app.route('/api/lyrics')
def get_lyrics():
    if 'artist' not in request.args or 'title' not in request.args:
        return ('Missing artist or title', 400, DEFAULT_HEADERS)

    artist = request.args['artist']
    title = request.args['title']
    
    if (song := genius.search_song(title, artist)):
        return (song.lyrics, DEFAULT_HEADERS)
    return ('Song not found', 404, DEFAULT_HEADERS)

