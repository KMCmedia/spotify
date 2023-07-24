from Analysis.SingleMusicianAnalysis import Musician
from Analysis.PlaylistAnalysis import Playlist
import time
class SimpleTest():
    def __init__(self, ID: str, SECRET_ID: str):
        self.ID = ID
        self.SECRET_ID = SECRET_ID

        # That's an extremely popular artist: Olivia Rodrigo. She's not going anywhere
        # So we can use her accounts as a reference
        self.testing_artist = 'https://open.spotify.com/artist/1McMsnEElThX1knmY4oliG'
        self.testing_album = 'https://open.spotify.com/playlist/37i9dQZF1DX4jP4eebSWR9'

    def initial_test(self) -> object:
        method_list_musician = [method for method in dir(Musician) if method.startswith('__') is False]
        method_list_album = [method for method in dir(Playlist) if method.startswith('__') is False]
        for method in method_list_musician:
            try:
                method_func = getattr(Musician(self.testing_artist, self.ID, self.SECRET_ID), method)
                start = time.time()
                method_func()
                stop = time.time()
                print(f'{method} took your machine {stop - start}s to execute')
            except:
                print(f'Method {method} did not pass the initial testing')
        for method in method_list_album:
            try:
                method_func = getattr(Playlist(self.testing_album, self.ID, self.SECRET_ID), method)
                start = time.time()
                method_func()
                stop = time.time()
                print(f'{method} took your machine {stop - start}s to execute')
            except:
                print(f'Method {method} did not pass the initial testing')