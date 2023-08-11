# Kiremico
#### Team Leader: Federico Rodriguez
#### Creator: Ilia Popov
## Abstract:

<p>This project aims to assist data scraping from Spotify as well as provide guidance to aspiring artists on improvement of their career. This is valuable for a variety of reasons, which will get clearer as you read the text. Here are some of our achievements:</p>

<table>
  <tr>
    <th>r-squared for the model</th> 
    <th>Number of collected data points</th>
    <th>Span of monthly listeners</th>
  </tr>
  <tr>
    <td>0.93</td>
    <td>~4000</td> 
    <td>5-100'000'000 </td>
  </tr>
</table>


## Applications

<p>You might be wondering what exactly can this application do. There are four things:</p>
<ul>
<li> Collect data about the <strong>musician</strong> based on the Spotify link to their account.</li>
<li> Collect data about the <strong>playlist</strong> based on the Spotify link to it.</li>
<li> Create a <strong>dataframe</strong> with the information you desire.</li>
<li> Get an estimate on how well the artist is performing and whether he/she has potential for <strong>success.</strong></li>

</ul>
<p> *Note: there are variables called ID and SECRET_ID. Those are provided in <strong>main.py</strong></p>
<p>*Note 2: every code snippet should be copy-pasted and ran in <strong>main.py</strong></p>

#### Musician Data Collection:

As of now you can collect variables by using the following procedure:

    #Identifying an object and then applying functions to it. All objects are strings
    musician = Musician( link_to_artist, ID, SECRET_ID) 
    musician.get_name() #gets the name of the artist 
    musician.get_release_history() #gets an array of total career time/number of tracks, avg_time_between_releases, time_since_latest_release, career_time, released_tracks
    musician.get_instagram_info() #gets average likes, comments, and average release of posts on instagram 

<p>Those are just a few of the available functions, documentation for which you will find inside the file <strong>SingleMusicianAnalysis.py</strong></p>

#### Playlist Data collection:

<p>Playlist data collection is one step on top of the Musician Analysis, and you can interact with it the following way:</p>

    #Identifying the object you will be working with:
    playlist = Playlist( playlist_link, ID, SECRET_ID)
    playlist.get_playlist_artists() #we get the artists inside the playlist as an array
    playlist.get_list_of_track_names() #we get an array of tracks in the playlist
<p>Once again, those are not all the functions inside the file, but a few examples. <br>For full list of functions go to <strong>PlaylistAnalysis.py</strong></p>

#### DataFrame creation:

<p>This file is most useful for using already created solutions. <br> For understanding what each goal means go to <strong>Documentation</strong> section.</p>

    #Creating the object we will be working with:
    df = DataFrame(ID, SECRET_ID)
    Goal_14 = df.Goal14(playlist_link) #we get IG link, Song Name and their name as well as their picture inside pictures Kiremico folder
    Goal_14.to_csv('Collected_Data/... .csv', index = False) #you set the name of the csv instead of ...

<p>After saving the dataframe as a .csv file, you should expect the result to look the following way: </p>
<table>
  <tr>
    <th>Index</th>
    <th>Song Name</th> 
    <th>Artist</th>
    <th>IG</th>
  </tr>
  <tr>
    <td>0</td>
    <td>Another Reason Why</td>
    <td>Charles On TV</td> 
    <td>https://instagram.com/charlesontv/?hl=en </td>
  </tr>
  <tr>
    <td>1</td>
    <td>Miss Interpretation</td>
    <td>Prismala</td> 
    <td>https://instagram.com/weareprismala/</td>
  </tr>
  <tr>
    <td>...</td>
    <td>...</td>
    <td>...</td> 
    <td>...</td>
  </tr>
  <tr>
    <td>100</td>
    <td>Lowkey</td>
    <td>Nate Redmond</td> 
    <td>https://instagram.com/nate_redmond</td>
  </tr>
</table>

 #### Model Application:

Model files serve two important functions to keep in mind:
<ul>
<li>Expand on the existing dataset</li>
<li>Retrain/train the model and apply it to the artist in question</li>
</ul>

<strong> How to expand on the existing dataset? </strong>

    model = TrainingSet(ID, SECRET_ID)
    model.ExpandData('Model') #change the name if you want to collect name from ground up

<strong>How to use the model?</strong>
<p>Here's a presentation of what the model looks like in its 3-dimensional projection:</p>

![Model](Collected_Data/READMEfiles/3d_scatter_plot_spin.gif)

<p> In order to use this model you need to run the following code:</p>

    model = Model(ID, SECRET_ID, 'Collected_Data/Model.csv', 'Monthly Listeners')
    links = [...]
    model.get_artist_prediction(links).to_csv('Collected_Data/Results.csv', index=False)

## Documentation
<p>
Each file serves a separate purpose and is embedded into the structure of the file. As of now the exact properties of each file and functions are the 
following:</p>

<ul>
<li> <strong>Analysis</strong> - contain functions related to an actual scraping of the Spotify API</li>
<ul>
<li><strong>SingleMusicianAnalysis.py</strong> - This file has all the lower level functions related to the collection of data. Open the file in order to see them. </li>
<li><strong>PlaylistAnalysis.py</strong> - This file is nested on the previous one. It provides information about the playlists, such as date of release, number of followers, artists in it, etc.</li>
</ul>
<li><strong>Collected Data</strong> - This is where the currently collected data is stored, and it's strongly suggested that any new file with information should be stored here as well. </li>
<ul>
    <li> <strong> Results.csv</strong> - this is the file where model results are stored</li>
    <li> <strong>Model.csv</strong> - this is where the data is</li>
</ul>
</ul>
