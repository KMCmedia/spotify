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
    #Create a a link to the file we will save the dictionary at
    link = 'Collected_Data/'+name+'.csv'

    #Check if the file already exists
    if not path.exists(link):
        pd.DataFrame(data=dictionary).to_csv(link, index=False)
    else:
        #Look at the file that already exists
        df_now = pd.read_csv(link)
        df_new = pd.DataFrame(data=dictionary)

        #Overlap between dataframes
        int_df = pd.merge(df_new, df_now, how='inner')

        #Check whether the overlap between the dataframes is the size of collected data
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

        # Creating the necessary variables for running the program
        monthly_listeners = musician.get_monthly_listeners()
        latest_release = musician.get_release_history()[2]
        genres = musician.get_genres()
        tour_bool = musician.is_on_tour()
        IG_link = musician.get_insta_link()

        #Apply the thresholding to check whether the artists fit what we need
        if thresholds['MAX_SP'] > monthly_listeners > thresholds['MIN_SP'] and latest_release < thresholds[
            'LAST_TRACK'] and np.intersect1d(genres, thresholds['GENRES']) != [] and tour_bool and IG_link != 'No Instagram':
            return True, musician.get_name(), IG_link, musician.get_latest_release()
        else:
            return False, False

    def Goal_14(self, playlist_link: str):
        dictionary = {'Song Name': [], 'Artist': [], 'IG':[]}
        playlist = Playlist(playlist_link, self.ID, self.SECRET_ID)
        dictionary['Song Name'] = playlist.get_list_of_track_names()
        artists = playlist.get_playlist_artists(repeating = True)
        dictionary['Artist'] = [Musician(artist, self.ID, self.SECRET_ID).get_name() for artist in artists]
        dictionary['IG'] = [Musician(artist, self.ID, self.SECRET_ID).get_insta_link() for artist in artists]
        for artist in artists:
            Musician(artist, self.ID, self.SECRET_ID).get_profile_picture()
        print(dictionary)
        return pd.DataFrame(data=dictionary)

    def Goal_11_4(self):
        dictionary = {'Artist Link': [], 'Average Likes': [], 'Average Comments': [], 'Average Release Time IG': []}
        artists = pd.read_excel('Collected_Data/Goal11_3.xlsx')['Artists Spotify Link'][1000:]
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


    def Goal_Artist_Scout(self, playlists: list, thresholds = SAMPLE_DICT):
        filtered_artists = {'Artist Name': [], 'IG Link': [], 'Latest Release': []}

        # Set up counters to keep track where the program is at
        i, j = 0, 0
        for playlist in playlists:
            artists = Playlist(playlist, self.ID, self.SECRET_ID).get_playlist_artists()
            j += 1
            for artist in artists:
                i += 1

                #print the update
                print(f'Analyzed {i} artist out of {len(artists)} in a playlist {j} out of {len(playlists)}')

                #Check whether the artist fit the description
                values = self.apply_thresholds_to_artist(artist, thresholds)
                if values[0]:
                    filtered_artists['Artist Name'].append(values[1])
                    filtered_artists['IG Link'].append(values[2])
                    filtered_artists['Latest Release'].append(values[3])
            i = 0
        return pd.DataFrame(data=filtered_artists)

    def Goal_13(self, playlist_link = ''):

        dictionary_empty = {'Artist in main Playlist':[], 'Playlist': [], 'Artist Found':[], 'Artist Link':[], 'Monthly Listeners': [], 'IG':[], 'On Tour':[]}

        if playlist_link != '':
            links_in_playlist = Playlist(playlist_link, self.ID, self.SECRET_ID).get_playlist_artists()
        else:
            # We get links to spotify artists from Goal 6
            links_in_playlist = pd.read_excel('Collected_Data/Goal6.xlsx')['SP Link'][15:]
        i,j,k = 0,0,0
        for link in links_in_playlist:
            main_musician = Musician(link, self.ID, self.SECRET_ID)
            main_musician_name = main_musician.get_name()
            playlists = main_musician.get_discovered_on_playlists()
            dictionary = dictionary_empty
            i+=1
            for playlist in playlists:
                playlist_obj = Playlist(playlist, self.ID, self.SECRET_ID)
                artists = playlist_obj.get_playlist_artists()
                j+=1
                for artist in artists:
                    k+=1
                    musician = Musician(artist, self.ID, self.SECRET_ID)
                    print(f'Analyzed {i}/{len(links_in_playlist)} links, where analyzed {j}/{len(playlists)} playlists with {k}/{len(artists)}')
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
        return pd.DataFrame(data = dictionary)






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
                link_artist = artist
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
