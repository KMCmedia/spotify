# Kiremico 
This project aims to assist data scraping from Spotify. 
Each file serves a separate purpose. As of now the exact properties of each file and functions are the 
following:
* Analysis - contain functions related to an actual scraping of the Spotify API
* * DataVisuals.py - In the future this file will provide visualizations to the artist predictive model, such as graphs for linear models/plots of Monthly listeners against collected parameters/Covariance matrix
* * SingleMusicianAnalysis.py - This file has all the lower level functions related to the collection of data. Open the file in order to see them. 
* * PlaylistAnalysis.py - This file is nested on the previous one. It provides information about the playlists, such as date of release, number of followers, artists in it, etc.
* Collected Data - This is where the currently collected data is stored, and it's strongly suggested that any new file with information should be stored here as well. 
* * Goal 3 - 