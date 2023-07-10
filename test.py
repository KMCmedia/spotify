from SingleMusicianAnalysis import Musician
import time
def testing():
    ID = '903b9497e92c4c96aac4f0c5ca79c4d2'
    SECRET_ID = '46ef4319ef624aef8c9f54dafa9b9f70'
    testing_artists = ['https://open.spotify.com/artist/1McMsnEElThX1knmY4oliG',
                       'https://open.spotify.com/artist/1gCOYbJNUa1LBVO5rlx0jB',
                       'https://open.spotify.com/artist/1Qp56T7n950O3EGMsSl81D']
    method_list = [method for method in dir(Musician) if method.startswith('__') is False]
    for method in method_list:
        method_func = getattr(Musician(testing_artists[0], ID, SECRET_ID), method)
        method_func()
