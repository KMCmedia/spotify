from Analysis.PlaylistAnalysis import Playlist
from Analysis.SingleMusicianAnalysis import Musician
import pandas as pd
import numpy as np
import spotipy
from os import path
from spotipy.oauth2 import SpotifyClientCredentials

# This dictionary sets up thresholds which are used later
SAMPLE_DICT = {'MAX_SP': 20000, 'MIN_SP': 2500, 'LAST_TRACK': 60, 'GENRES': ['indie', 'rock', 'grunge', 'pop'],
               'ON_TOUR': True, 'IG_LINK': True}


class DataFrame():
    def __init__(self, ID: str, SECRET_ID: str):
        self.sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=ID,
                                                                        client_secret=SECRET_ID))
        self.ID = ID
        self.SECRET_ID = SECRET_ID

    def Goal_11(self, df_Goal3, df_Goal10, output_file_link: str):

        # In Goal 11 we collect the information about the artists to create a predictive model based on their
        # current performance. That's why we use so many metrics

        # Those DataFrames by their creation contain KMC artists, and playlists those artists are in
        df_playlist = df_Goal10
        df_artists = df_Goal3

        # We separate playlists by artists
        playlists = df_playlist.groupby('Artist Link')['Artist Playlist'].apply(list).reset_index()

        # In case there's no output file we'll update with new information, we create one
        if not path.exists(output_file_link):
            d = {'Artist': [], 'Artist AVG Release': [], 'Playlist Link': [], 'Playlist Description': [],
                 'Playlists Likes': [], 'Playlist AVG Release Time': [],
                 'Artist Inside': [], 'Artists Spotify Link': [], 'AVG Release Time Artist': [], 'Monthly Listeners': []
                , 'Career Started': [], 'Time Since Latest Release': [], 'Number of Tracks': [],
                 'AVG Release Time Per Track Artist': [],
                 'Instagram Link': [], 'Instagram Subscribers': [], 'Popularity Index': []}
            pd.DataFrame(data=d).to_excel(output_file_link, index=False)

        #This the update part
        df_now = pd.read_excel(output_file_link)
        artists = df_artists['Artist Link'].to_numpy()[len(np.unique(df_now['Artist'])):]

        #We analyze the data from the artist and add it to the dataframe
        for artist in artists:
            df_now = pd.read_excel(output_file_link)
            output = self.Full_Dataframe(artist, playlists)
            output = pd.concat([df_now, output])
            output = output.drop_duplicates()
            output.to_excel(output_file_link, index=False)
        return None

    def apply_thresholds_to_artist(self, artist: str, thresholds: dict):
        # Initializing a class to analyze it
        musician = Musician(artist, self.ID, self.SECRET_ID)
        # Necessary variables
        monthly_listeners = musician.get_monthly_listeners()
        latest_release = musician.get_release_history()[2]
        genres = musician.get_genres()
        tour_bool = musician.is_on_tour()
        IG_link = musician.get_insta_link()

        if thresholds['MAX_SP'] > monthly_listeners > thresholds['MIN_SP'] and latest_release < thresholds[
            'LAST_TRACK'] and np.intersect1d(genres, thresholds['GENRES']) != [] and tour_bool and IG_link != 'No Instagram':
            return True, musician.get_name(), IG_link, musician.get_latest_release()
        else:
            return False, False

    def Goal_Artist_Scout(self, playlists: list, thresholds = SAMPLE_DICT):
        filtered_artists = {'Artist Name': [], 'IG Link': [], 'Latest Release': []}
        for playlist in playlists:
            artists = Playlist(playlist, self.ID, self.SECRET_ID).get_playlist_artists()
            for artist in artists:
                values = self.apply_thresholds_to_artist(f'https://open.spotify.com/artist/{artist}', thresholds)
                print(values)
                if values[0]:
                    filtered_artists['Artist Name'].append(values[1])
                    filtered_artists['IG Link'].append(values[2])
                    filtered_artists['Latest Release'].append(values[3])
        return pd.DataFrame(data=filtered_artists)

    def Full_Dataframe(self, link: str, df):
        # Creating a dictionary which will be turned into a dataframe
        d = {'Artist': [], 'Artist AVG Release': [], 'Playlist Link': [], 'Playlist Description': [],
             'Playlists Likes': [], 'Playlist AVG Release Time': [],
             'Artist Inside': [], 'Artists Spotify Link': [], 'AVG Release Time Artist': [], 'Monthly Listeners': []
            , 'Career Started': [], 'Time Since Latest Release': [], 'Number of Tracks': [],
             'AVG Release Time Per Track Artist': [],
             'Instagram Link': [], 'Instagram Subscribers': [], 'Popularity Index': []}

        # looping through every artist given
        musician = Musician(link, self.ID, self.SECRET_ID)
        artist_name = musician.get_name()
        release_freq = musician.get_release_history()[1]
        playlist_links = musician.get_artist_radios()
        additional_links = df.loc[df['Artist Link'] == link, 'Artist Playlist'].to_list()
        if len(additional_links) != 0:
            playlist_links.extend(additional_links[0])
        counter_playlist = 0
        for playlist in playlist_links:
            # Getting the relevant playlist information
            playlist_obj = Playlist(playlist, self.ID, self.SECRET_ID)
            playlist_descr = playlist_obj.get_playlist_description()
            playlist_likes = playlist_obj.get_likes()
            release_freq_array = []
            counter_artist = 0
            counter_playlist += 1
            artists = playlist_obj.get_playlist_artists()
            for artist in artists:
                counter_artist += 1
                link_artist = 'https://open.spotify.com/artist/' + artist
                artist_obj = Musician(link_artist, self.ID, self.SECRET_ID)
                artist_within_playlist_name = artist_obj.get_name()
                array = artist_obj.get_release_history()

                # If the release history is broken we fill it out with errors
                # Otherwise we populate it with values
                if array[0] == 'Error':
                    release_freq_within_playlist = array[0]
                    start_career = array[0]
                    release_freq_within_playlist_per_track = array[0]
                    number_of_tracks = array[0]
                    latest_release = array[0]
                else:
                    release_freq_within_playlist = array[1]
                    release_freq_within_playlist_per_track = array[0]
                    number_of_tracks = array[4]
                    latest_release = array[2]
                    release_freq_array.append(release_freq_within_playlist)
                    start_career = array[3]

                # Sometimes this method produces errors
                try:
                    monthly_listeners = artist_obj.get_monthly_listeners()
                except:
                    monthly_listeners = 'Error'

                # Sending signal to the console
                print(f'Artist {counter_artist} out of {len(artists)} is analyzed in playlist {counter_playlist} '
                      f'out of {len(playlist_links)}')

                # Updating the dataframe:
                d['Artist'].append(artist_name)
                d['Artist AVG Release'].append(release_freq)
                d['Playlist Link'].append(playlist)
                d['Playlist Description'].append(playlist_descr)
                d['Playlists Likes'].append(playlist_likes)
                d['AVG Release Time Per Track Artist'].append(release_freq_within_playlist_per_track)
                d['Number of Tracks'].append(number_of_tracks)
                d['Time Since Latest Release'].append(latest_release)
                d['Artist Inside'].append(artist_within_playlist_name)
                d['Artists Spotify Link'].append(link_artist)
                d['AVG Release Time Artist'].append(release_freq_within_playlist)
                d['Monthly Listeners'].append(monthly_listeners)
                d['Career Started'].append(start_career)
                d['Instagram Link'].append(artist_obj.get_insta_link())
                d['Instagram Subscribers'].append(artist_obj.get_instagram_followers())
                d['Popularity Index'].append(artist_obj.get_popularity())
            d['Playlist AVG Release Time'].extend(np.ones(len(artists)) * np.average(release_freq_array))
        return pd.DataFrame(data=d)
