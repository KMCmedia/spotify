import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from datetime import datetime
import numpy as np

class Playlist():
    def __init__(self, playlist_link: str, ID: str, SECRET_ID: str):
        self.sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=ID,
                                                                   client_secret=SECRET_ID))
        self.playlist_id = playlist_link.split('/')[-1]
        self.playlist = self.sp.playlist(playlist_link)

    def get_creation_date(self):
        # Setting up constants
        oldest_date = datetime.today()
        # Iterate over the tracks in the playlist
        for item in self.playlist['tracks']['items']:
            #getting the date of the release of the track
            release_date = datetime.strptime(item['added_at'][:10], '%Y-%m-%d')
            if release_date < oldest_date:
                oldest_date = release_date
        return oldest_date

    def get_playlist_artists(self):
        # Extract the artists from the playlist
        artists = set()
        for track in self.playlist['tracks']['items']:
            artist_names = [artist['id'] for artist in track['track']['artists']]
            artists.update(artist_names)
        return artists

    def get_likes(self):
        return self.playlist['followers']['total']

    def get_playlist_name(self):
        return self.playlist['name']

    def get_owner_username(self):
        return self.playlist['owner']['display_name']

    def get_playlist_description(self):
        return self.playlist['description']

    def get_playlist_total_tracks(self):
        return self.playlist['tracks']['total']

    def get_list_of_track_names(self):
        # Retrieve all tracks in the playlist using pagination
        tracks = []
        offset = 0
        limit = 100

        total_tracks = self.playlist['tracks']['total']

        while offset < total_tracks:
            results = self.sp.playlist_tracks(self.playlist_id, offset=offset, limit=limit)
            tracks.extend(results['items'])
            offset += limit

        # Get the names of all tracks
        return [track['track']['name'] for track in tracks]

    def get_total_time(self):
        # Retrieve all tracks in the playlist using pagination
        tracks = []
        offset = 0
        limit = 100

        total_tracks = self.playlist['tracks']['total']

        while offset < total_tracks:
            results = self.sp.playlist_tracks(self.playlist_id, offset=offset, limit=limit)
            tracks.extend(results['items'])
            offset += limit

        return int(np.sum([track['track']['duration_ms'] for track in tracks])//60000)

