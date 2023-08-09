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


def temporary_save(name: str, dictionary):
    # Create a a link to the file we will save the dictionary at
    link = 'Collected_Data/' + name + '.csv'

    # Check if the file already exists
    if not path.exists(link):
        pd.DataFrame(data=dictionary).to_csv(link, index=False)
    else:
        # Look at the file that already exists
        df_now = pd.read_csv(link)
        df_new = pd.DataFrame(data=dictionary)

        # Overlap between dataframes
        int_df = pd.merge(df_new, df_now, how='inner')

        # Check whether the overlap between the dataframes is the size of collected data
        if int_df.shape[0] < df_new.shape[0]:
            output = pd.concat([df_now, df_new])
            output.to_csv(link, index=False)
    return None


class DataFrame():
    def __init__(self, ID: str, SECRET_ID: str):
        self.sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=ID,
                                                                        client_secret=SECRET_ID))
        self.ID = ID
        self.SECRET_ID = SECRET_ID

    def apply_thresholds_to_artist(self, artist: str, thresholds: dict):
        # Initializing a class to analyze it
        musician = Musician(artist, self.ID, self.SECRET_ID)

        # Creating the necessary variables for running the program
        monthly_listeners = musician.get_monthly_listeners()
        latest_release = musician.get_release_history()[2]
        genres = musician.get_genres()
        tour_bool = musician.is_on_tour()
        IG_link = musician.get_insta_link()

        # Apply the thresholding to check whether the artists fit what we need
        if thresholds['MAX_SP'] > monthly_listeners > thresholds['MIN_SP'] and latest_release < thresholds[
            'LAST_TRACK'] and np.intersect1d(genres,
                                             thresholds['GENRES']) != [] and tour_bool and IG_link != 'No Instagram':
            return True, musician.get_name(), IG_link, musician.get_latest_release()
        else:
            return False, False

    def Goal_14(self, playlist_link: str):
        dictionary = {'Song Name': [], 'Artist': [], 'IG': []}
        playlist = Playlist(playlist_link, self.ID, self.SECRET_ID)
        dictionary['Song Name'] = playlist.get_list_of_track_names()
        artists = playlist.get_playlist_artists(repeating=True)
        dictionary['Artist'] = [Musician(artist, self.ID, self.SECRET_ID).get_name() for artist in artists]
        dictionary['IG'] = [Musician(artist, self.ID, self.SECRET_ID).get_insta_link() for artist in artists]
        for artist in artists:
            Musician(artist, self.ID, self.SECRET_ID).get_profile_picture()
        return pd.DataFrame(data=dictionary)

    def Goal_11_4(self):
        dictionary = {'Artist Link': [], 'Average Likes': [], 'Average Comments': [], 'Average Release Time IG': []}
        artists = pd.read_excel('Collected_Data/PredictiveModelSet.csv')['Artists Spotify Link']
        i = 1
        for artist in artists:
            mus = Musician(artist, self.ID, self.SECRET_ID)
            result = mus.get_instagram_info()
            dictionary['Artist Link'].append(artist)
            dictionary['Average Likes'].append(result[0])
            dictionary['Average Comments'].append(result[1])
            dictionary['Average Release Time IG'].append(result[2])
            print(f'Analyzed {i}/{len(artists)} artists ')
            i += 1
        return pd.DataFrame(data=dictionary)

    def Goal_Artist_Scout(self, playlists: list, thresholds=SAMPLE_DICT):
        filtered_artists = {'Artist Name': [], 'IG Link': [], 'Latest Release': []}

        # Set up counters to keep track where the program is at
        i, j = 0, 0
        for playlist in playlists:
            artists = Playlist(playlist, self.ID, self.SECRET_ID).get_playlist_artists()
            j += 1
            for artist in artists:
                i += 1

                # print the update
                print(f'Analyzed {i} artist out of {len(artists)} in a playlist {j} out of {len(playlists)}')

                # Check whether the artist fit the description
                values = self.apply_thresholds_to_artist(artist, thresholds)
                if values[0]:
                    filtered_artists['Artist Name'].append(values[1])
                    filtered_artists['IG Link'].append(values[2])
                    filtered_artists['Latest Release'].append(values[3])
            i = 0
        return pd.DataFrame(data=filtered_artists)

    def Goal_13(self, playlist_link=''):

        dictionary_empty = {'Artist in main Playlist': [], 'Playlist': [], 'Artist Found': [], 'Artist Link': [],
                            'Monthly Listeners': [], 'IG': [], 'On Tour': []}

        if playlist_link != '':
            links_in_playlist = Playlist(playlist_link, self.ID, self.SECRET_ID).get_playlist_artists()
        else:
            # We get links to spotify artists from Goal 6
            links_in_playlist = pd.read_excel('Collected_Data/Goal6.xlsx')['SP Link'][15:]
        i, j, k = 0, 0, 0
        for link in links_in_playlist:
            main_musician = Musician(link, self.ID, self.SECRET_ID)
            main_musician_name = main_musician.get_name()
            playlists = main_musician.get_discovered_on_playlists()
            dictionary = dictionary_empty
            i += 1
            for playlist in playlists:
                playlist_obj = Playlist(playlist, self.ID, self.SECRET_ID)
                artists = playlist_obj.get_playlist_artists()
                j += 1
                for artist in artists:
                    k += 1
                    musician = Musician(artist, self.ID, self.SECRET_ID)
                    print(
                        f'Analyzed {i}/{len(links_in_playlist)} links, where analyzed {j}/{len(playlists)} playlists with {k}/{len(artists)}')
                    if musician.get_monthly_listeners() < 200000:
                        dictionary['Artist in main Playlist'].append(main_musician_name)
                        dictionary['Playlist'].append(playlist)
                        dictionary['Artist Found'].append(musician.get_name())
                        dictionary['Artist Link'].append(artist)
                        dictionary['Monthly Listeners'].append(musician.get_monthly_listeners())
                        dictionary['IG'].append(musician.get_insta_link())
                        dictionary['On Tour'].append(musician.is_on_tour())
                k = 0
                temporary_save('Goal_13', dictionary)
            j = 0
        return pd.DataFrame(data=dictionary)

