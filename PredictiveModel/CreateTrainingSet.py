from Analysis.PlaylistAnalysis import Playlist
from Analysis.SingleMusicianAnalysis import Musician
import pandas as pd
import numpy as np
import spotipy
from os import path
from spotipy.oauth2 import SpotifyClientCredentials

dummy_row = {'Artist': [], 'Artist AVG Release': [], 'Playlist Link': [], 'Playlist Description': [],
     'Playlists Likes': [], 'Playlist AVG Release Time': [],
     'Artist Inside': [], 'Artists Spotify Link': [], 'AVG Release Time Artist': [], 'Monthly Listeners': []
    , 'Career Started': [], 'Time Since Latest Release': [], 'Number of Tracks': [],
     'AVG Release Time Per Track Artist': [],
     'Instagram Link': [], 'Instagram Subscribers': [], 'Popularity Index': [],
     'Average Likes': [], 'Average Comments': [], 'Average Release Time IG': []}

def add_listeners_and_artists(df):
    #dropping columns if they are there
    existing_columns = set(df.columns)
    columns_to_drop = {'index', 'AVG listeners playlist', 'Number of artists in playlist', 'level_0', 'index'}
    columns_to_drop_existing = columns_to_drop.intersection(existing_columns)

    if columns_to_drop_existing:
        df.drop(columns=list(columns_to_drop_existing), axis=1, inplace=True)

    unique_playlists = np.unique(df['Playlist Link'])
    listen_list = np.array([])
    singer_list = np.array([])
    for playlist in unique_playlists:
        list_of_monthly_listeners = df.loc[df['Playlist Link'] == playlist]['Monthly Listeners'].to_list()
        if list_of_monthly_listeners[0] == 'Error':
            num_singers = len(list_of_monthly_listeners)
            avg_listen = 0
        else:
            list_of_monthly_listeners = [float(x) for x in list_of_monthly_listeners]
            num_singers = len(list_of_monthly_listeners)
            avg_listen = np.average(list_of_monthly_listeners)
        sub_list = np.ones(num_singers) * avg_listen
        sub_list_1 = np.ones(num_singers) * num_singers
        listen_list = np.concatenate((listen_list, sub_list))
        singer_list = np.concatenate((singer_list, sub_list_1))
    df_1 = df
    df_2 = pd.DataFrame(np.column_stack((listen_list, singer_list)),
                        columns=['AVG listeners playlist', 'Number of artists in playlist'])
    df_main = pd.concat([df_1.reset_index(), df_2], axis=1, join='inner')
    return df_main


class TrainingSet():
    def __init__(self, ID, SECRET_ID):
        self.sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=ID,
                                                                        client_secret=SECRET_ID))
        self.ID = ID
        self.SECRET_ID = SECRET_ID
        self.df_Goal10 = pd.read_excel('Collected_Data/Goal10.xlsx')
        self.df_Goal3 = pd.read_excel('Collected_Data/Goal3.xlsx')
    def ExpandData(self, save_name:str):

        # In Goal 11 we collect the information about the artists to create a predictive model based on their
        # current performance. That's why we use so many metrics

        # Those DataFrames by their creation contain KMC artists, and playlists those artists are in
        output_file_link = 'Collected_Data/'+save_name+'.csv'
        df_playlist = self.df_Goal10
        df_artists = self.df_Goal3

        # We separate playlists by artists
        playlists = df_playlist.groupby('Artist Link')['Artist Playlist'].apply(list).reset_index()

        # In case there's no output file we'll update with new information, we create one
        if not path.exists(output_file_link):
            d = dummy_row
            pd.DataFrame(data=d).to_csv(output_file_link, index=False)

        # This the update part
        df_now = pd.read_csv(output_file_link)
        artists = df_artists['Artist Link'].to_numpy()[len(np.unique(df_now['Artist']))+1:]

        # We analyze the data from the artist and add it to the dataframe
        for artist in artists:
            df_now = pd.read_csv(output_file_link)
            output = self.Full_Dataframe(artist)

            #in case nothing is produced for an artist
            if output.empty:
                d = dummy_row
                for key in d.keys():
                    if key == 'Artist':
                        d['Artist'].append(Musician(artist, self.ID, self.SECRET_ID).get_name())
                    else:
                        d[key].append('Error')
                dummy_df = pd.DataFrame(d)
                common_columns = set(output.columns).intersection(dummy_df.columns)
                output = pd.concat([output[common_columns], dummy_df[common_columns]], ignore_index=True)
                output = pd.concat([df_now, output])
                output.to_csv(output_file_link, index=False)
            else:
                #merge output with what was created before
                output = pd.concat([df_now, output])
                output = add_listeners_and_artists(output)
                output = output.drop_duplicates()
                output.to_csv(output_file_link, index=False)
        return None

    def Full_Dataframe(self, link: str):
        elements_analyzed = 0

        # Creating a dictionary which will be turned into a dataframe
        d = dummy_row

        # looping through every artist given
        musician = Musician(link, self.ID, self.SECRET_ID)
        artist_name = musician.get_name()
        release_freq = musician.get_release_history()[1]
        playlist_links = musician.get_artist_radios()
        # Here we find discovered-on playlists
        additional_links = self.df_Goal10.loc[self.df_Goal10['Artist Link'] == link, 'Artist Playlist'].to_list()
        if len(additional_links) != 0:
            playlist_links.extend(additional_links)
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
                artist_information_about_instagram = artist_obj.get_instagram_info()
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
                d['Average Likes'].append(artist_information_about_instagram[0])
                d['Average Comments'].append(artist_information_about_instagram[1])
                d['Average Release Time IG'].append(artist_information_about_instagram[2])
                elements_analyzed += 1
            d['Playlist AVG Release Time'].extend(np.ones(len(artists)) * np.average(release_freq_array))
            if elements_analyzed > 500:
                return pd.DataFrame(data=d)
        return pd.DataFrame(data=d)
