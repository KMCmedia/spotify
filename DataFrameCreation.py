from SingleMusicianAnalysis import Musician
import time
def testing():
    testing_artists = ['https://open.spotify.com/artist/1McMsnEElThX1knmY4oliG',
                       'https://open.spotify.com/artist/1gCOYbJNUa1LBVO5rlx0jB',
                       'https://open.spotify.com/artist/1Qp56T7n950O3EGMsSl81D']
    method_list = [method for method in dir(Musician) if method.startswith('__') is False]
    for method in method_list:
        print(method_list)

def