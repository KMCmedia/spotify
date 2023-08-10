import joblib
from sklearn.linear_model import LinearRegression
from Analysis.SingleMusicianAnalysis import Musician
from Analysis.PlaylistAnalysis import Playlist
import os
import itertools
import pandas as pd
import numpy as np
import spotipy
import math
from spotipy.oauth2 import SpotifyClientCredentials


def safe_log(x: object) -> object:
    if x > 0:
        return np.log(x)
    else:
        return x


def clean_up_data(link_to_data: str):
    df = pd.read_csv(link_to_data)

    # Drop the identified columns (MAKE BETTER)
    columns_we_dont_like = {'index', 'Instagram Link', 'Artist Inside', 'Artists Spotify Link', 'Artist',
                            'Artist AVG Release', 'Artist Link.1', 'Average Likes.1', 'Average Comments.1', 'Average Release Time IG.1',
                            'Playlist Link', 'Playlist Description', 'Instagram Subscribers', 'Artist Link'}
    columns_to_drop_existing = columns_we_dont_like.intersection(set(df.columns))
    df = df.drop(columns=columns_to_drop_existing)

    # Deleting duplicates
    df = df.drop_duplicates()
    # Deleting rows with Nans
    df = df.dropna()
    # Deleting rows where there are no likes
    df = df.drop(df[df['Average Likes'] == -1].index)
    # Dropping every column with an error
    for column in df.columns:
        df = df.drop(df[df[column] == 'Error'].index)
    # converting everything to a number
    df = df.astype(float)
    # taking the logarithm of everything
    df_1 = df.loc[:, df.columns != 'Popularity Index'].applymap(safe_log)
    df = pd.concat([df['Popularity Index'], df_1], axis=1, join='inner')
    return df


class Model():
    def __init__(self, ID, SECRET_ID, link_to_data, y_name):
        self.ID = ID
        self.SECRET_ID = SECRET_ID
        self.sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=ID,
                                                                        client_secret=SECRET_ID))
        self.model = 'Collected_Data/models/best_model.joblib'
        self.parameters = 'Collected_Data/models/best_parameters.npy'
        self.link_to_data = link_to_data
        self.y_name = y_name

    def train_model(self):
        df = clean_up_data(self.link_to_data)
        # We want our model to find the best fit for monthly listeners, so we delete column where it's present
        columns = np.delete(np.array(df.columns), np.where(np.array(df.columns) == self.y_name))
        # All possible combinations of columns
        combinations = [np.array(combination) for r in range(3, len(columns) + 1) for combination in
                        itertools.combinations(columns, r)]

        # We run maximization
        best_r = 0
        best_combination = []
        best_model = None

        # Run through all possibilities
        for el in combinations:
            df_now = df[el]
            x = df_now.values.tolist()
            y = df[self.y_name].tolist()
            model = LinearRegression().fit(x, y)
            r_sq = model.score(x, y)
            if r_sq > best_r:
                best_r = r_sq
                best_combination = el
                best_model = model

        # Saving the model for later use
        if not os.path.exists(self.model):
            joblib.dump(best_model, self.model)
        else:
            os.remove(self.model)
            joblib.dump(best_model, self.model)

        # Saving the parameters for later use
        output_parameters = np.array(best_combination)
        if not os.path.exists(self.parameters):
            np.save(self.parameters, output_parameters)
        else:
            os.remove(self.parameters)
            np.save(self.parameters, output_parameters)
        return best_r, best_combination, best_model

    def get_representative_artists(self, num_of_buckets: int):
        #read the file
        df = pd.read_csv(self.link_to_data)
        # Deleting duplicates
        df = df.drop_duplicates()
        # Deleting rows with Nans
        df = df.dropna()
        # Deleting rows where there are no likes
        df = df.drop(df[df['Average Likes'] == -1].index)
        # Dropping every column with an error
        for column in df.columns:
            df = df.drop(df[df[column] == 'Error'].index)

        #get the model
        model = joblib.load(self.model)
        parameters = np.load(self.parameters)

        #Getting the edges of the spectrum
        df[self.y_name] = df[self.y_name].astype(float)
        minimum = min(df[self.y_name])
        step = (max(df[self.y_name])-min(df[self.y_name]))/num_of_buckets

        #creating output array
        array = []
        min_residual = 10e5
        for j in range(num_of_buckets+1):
            array.append(['Sample_name', min_residual, {key: 1 for key in parameters}])

        for index, row in df.iterrows():
            # get the x for the model
            x = []
            for column in parameters:
                if column != 'Popularity Index':
                    x.append(safe_log(float(row[column])))
                else:
                    x.append(float(row[column]))

            predicted_y = model.predict(np.array(x).reshape(1, -1))
            y = row[self.y_name]
            residual = np.abs(predicted_y - y)
            # residual = predicted_y - y - this is for getting bad artists
            bucket_num = int((y - minimum)//step)
            if array[bucket_num][1] > residual:
                array[bucket_num][0] = row['Artist Inside']
                array[bucket_num][1] = int(y)
                array[bucket_num][2] = dict(zip(parameters, [np.exp(el) for el in x]))

        #process the produced array
        dictionary = {'Bucket range': [], 'Monthly listeners': [], 'Name': []}
        for parameter in parameters:
            dictionary[parameter] = []
        for i in range(num_of_buckets):
            dictionary['Bucket range'].append(f'{int(minimum + i*step)}-{int(minimum + (i+1)*step)}')
            dictionary['Monthly listeners'].append(array[i][1])
            dictionary['Name'].append(array[i][0])
            for parameter in parameters:
                if parameter == 'Popularity Index':
                    dictionary[parameter].append(int(np.log(array[i][2][parameter])))
                else:
                    dictionary[parameter].append(int(array[i][2][parameter]))
        df = pd.DataFrame(dictionary)
        df = df.drop(df[df['Name'] == 'Sample_name'].index)
        df.to_csv(f'Collected_Data/buckets_{num_of_buckets}.csv')
        return None

    def get_artist_data(self, link):
        artist = Musician(link, self.ID, self.SECRET_ID)
        playlists = artist.get_discovered_on_playlists()[:2]
        print('Collected playlists...')
        d = {'Artist AVG Release': [], 'Playlists Likes': [], 'Playlist AVG Release Time': [], 'AVG Release Time Artist': [],
             'Monthly Listeners': [], 'Career Started': [], 'Time Since Latest Release': [], 'Number of Tracks': [],
             'AVG Release Time Per Track Artist': [], 'Popularity Index': [], 'Average Likes': [], 'Average Comments': [],
             'Average Release Time IG': [], 'Number of artists in playlist': [], 'AVG listeners playlist': []}
        i, j, time = 0, 0, 0
        likes = 0
        avg_artist_num = 0
        avg_listeners = 0
        for playlist in playlists:
            play = Playlist(playlist, self.ID, self.SECRET_ID)
            likes += play.get_likes()
            i += 1
            artists = play.get_playlist_artists()
            print(f'Collected Data by {100*i//2}%...')
            avg_artist_num += len(artists)
            if len(artists) > 4:
                artists = artists[:4]
            for art in artists:
                mus = Musician(art, self.ID, self.SECRET_ID)
                time += mus.get_release_history()[0]
                avg_listeners += mus.get_monthly_listeners()
                j += 1
        array = artist.get_release_history()
        array_1 = artist.get_instagram_info()
        #Dumb troubleshooting
        if array_1[2] == 0:
            array_1 = [100, 1, 20]
        if i == 0 or j == 0:
            i,j = 1,1
        d['Artist AVG Release'].append(array[0])
        d['Number of artists in playlist'].append(avg_artist_num / i)
        d['AVG listeners playlist'].append(avg_listeners/i)
        d['Playlists Likes'].append(likes / i)
        d['Playlist AVG Release Time'].append(time / j)
        d['AVG Release Time Artist'].append(array[1])
        d['Monthly Listeners'].append(artist.get_monthly_listeners())
        d['Career Started'].append(array[3])
        d['Time Since Latest Release'].append(array[2])
        d['Number of Tracks'].append(array[4])
        d['AVG Release Time Per Track Artist'].append(array[0])
        d['Popularity Index'].append(np.exp(artist.get_popularity()))
        d['Average Likes'].append(array_1[0])
        d['Average Comments'].append(array_1[1])
        d['Average Release Time IG'].append(array_1[2])
        return pd.DataFrame(d)

    def get_strategy_data(self, scale_of_zoom: int, artist_link: str):
        # produce points that lie on the line
        if not os.path.exists(f'Collected_Data/buckets_{scale_of_zoom}.csv'):
            self.get_representative_artists(scale_of_zoom)
            df_compare = pd.read_csv(f'Collected_Data/buckets_{scale_of_zoom}.csv')
        else:
            df_compare = pd.read_csv(f'Collected_Data/buckets_{scale_of_zoom}.csv')

        #get the model
        model = joblib.load(self.model)
        parameters = np.load(self.parameters)

        # produce the x-axis and the y
        print('Collecting data...')
        df = self.get_artist_data(artist_link)
        print('Collected Data')
        y = df[self.y_name][0]
        columns_to_drop = set(parameters) ^ set(df.columns)
        df = df.drop(columns=columns_to_drop)
        x = [safe_log(df[parameter][0]) for parameter in parameters]

        # get residual (if positive, good, if negative bad)
        residual_percentage = 100*(y/model.predict(np.array(x).reshape(1, -1)) - 1)
        # Let's get what needs to be increased
        filtered_row = df_compare[df_compare['Monthly listeners'] > y].iloc[[0]]
        x = [int(np.exp(element)) for element in x]
        i = 0
        for parameter in parameters:
            if parameter == 'Popularity Index':
                filtered_row[parameter] -= int(np.log(x[i]))
            else:
                filtered_row[parameter] -= x[i]
            if filtered_row[parameter].to_numpy()[0] > 0:
                filtered_row[parameter] = f'You need an increase by {filtered_row[parameter].to_numpy()[0] }'
            else:
                filtered_row[parameter] = f'You are better by {-filtered_row[parameter].to_numpy()[0] }'
            i += 1
        if residual_percentage > 100:
            filtered_row['Performance'] = f'You are doing better by {residual_percentage[0]-100}% than model predicted. Keep up!'
        else:
            filtered_row['Performance'] = f'You are doing worse by {100-residual_percentage[0]}% than model predicted. Time to improve!'
        filtered_row['Name of the artist we are analyzing'] = Musician(artist_link, self.ID, self.SECRET_ID).get_name()
        return filtered_row

    def get_artist_prediction(self, links: list):
        SCALE = 5000
        df_0 = pd.DataFrame()
        i = 0
        for link in links:
            df = self.get_strategy_data(SCALE, link)
            if df_0.empty:
                df_0 = df
            else:
                df_0 = pd.concat([df, df_0], ignore_index=True)
        return df_0


