from DataFrame import DataFrame
import Collected_Data
from Analysis.PlaylistAnalysis import Playlist
import pandas as pd
import os.path
import numpy as np
from os import path
from test import SimpleTest
from Analysis.SingleMusicianAnalysis import Musician

#In case IDs get overused, here's a couple others:
#ID: 903b9497e92c4c96aac4f0c5ca79c4d2, SECRET: 46ef4319ef624aef8c9f54dafa9b9f70
#ID:8ff0297906e742889803ee92eaa3a88d, SECRET: 75b1167b36884fd88c464a9f31dac548
#ID: d7424564ec664c6db9d06d960e8c17f2 SECRET: ac20a665473a4e8686c29b604a48db22
#ID: bf7a71c85e96406eb8d949fde850a5c4 SECRET: 9d4dd7b267b84d5eb559812ad6c23da8

ID = '8ff0297906e742889803ee92eaa3a88d'
SECRET_ID = '75b1167b36884fd88c464a9f31dac548'

if __name__ == '__main__':
    # test = SimpleTest(ID, SECRET_ID)
    # test.initial_test()

    # df_Goal_3 = pd.read_excel('Collected_Data/Goal3.xlsx')
    # df_Goal_10 = pd.read_excel('Collected_Data/Goal10.xlsx')
    #
    # #This function creates output on the desktop
    df = DataFrame(ID, SECRET_ID)
    save_path = 'Collected_Data/Goal13.csv'
    df_1 = df.Goal_13()
    df_1.to_csv(save_path)