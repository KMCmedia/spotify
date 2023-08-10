from geopy.geocoders import Nominatim
import geopy
from bs4 import BeautifulSoup
import re
import datetime
import numpy as np
import requests
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import urllib.request
from PIL import Image

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def contains_only_numbers_and_letters(input_string):
    # Define the regular expression pattern to match alphanumeric characters
    pattern = r'^[a-zA-Z0-9]+$'

    # Use the re.match() function to check if the entire string matches the pattern
    match = re.match(pattern, input_string)

    # If match is not None, it means the string contains only numbers and letters
    return match is not None
def find_nearest(array, value):
    # Finding the nearest value to the given one in the array
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]


def convert_num(num):
    # This function converts numbers from the format ...K/M into floats
    if num[-1] == ' ':
        num = num[:-1]
    if num[-1] == 'M':
        # M converting to millions
        return float(num[:-1]) * 10 ** 6
    elif num[-1] == 'K':
        # K converting to thousands
        return float(num[:-1]) * 10 ** 3
    else:
        # Deleting the commas separating thousands
        return float(num.replace(',', ''))

def time_difference(start_date, end_date):
    date_format = "%Y-%m-%d"
    start_datetime = datetime.datetime.strptime(start_date, date_format)
    end_datetime = datetime.datetime.strptime(end_date, date_format)
    time_delta = end_datetime - start_datetime
    return time_delta


class Musician():
    def __init__(self, artist_link: str, ID: str, SECRET_ID: str):
        self.sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=ID,
                                                                        client_secret=SECRET_ID))
        self.items = self.sp.artist(artist_link.split('/')[-1])
        self.link = artist_link
        self.artist_id = artist_link.split('/')[-1]
        self.artist_uri = self.items['uri']

        # Earliest possible release date
        self.CONST = datetime.datetime(1860, 4, 8)

        # getting the html of the website as a text
        self.soup_str = str(BeautifulSoup(requests.get(self.link).content, 'html.parser'))

        # coordinates of the city we reside in:
        self.coords_B = (52.520008, 13.404954)

    def get_name(self):
        # Gets a name of an artist based on his/her ID
        return self.soup_str[self.soup_str.find('content="Listen to ') + 19:self.soup_str.find(' on Spotify. Artist')]

    def get_profile_picture(self):
        # Getting the name of an artist
        pic_name = self.get_name()

        # Get all the links which fit the condition for an image
        link_regex = re.compile(r'(https://i.scdn.co/image/\S+)')

        # Get the indexes of all the links
        links = re.findall(link_regex, self.soup_str)

        # requesting the image of the last link
        urllib.request.urlretrieve(links[0][:-1], f"{pic_name}.png")

        # Saving the collected image
        img = Image.open(f"{pic_name}.png")
        img.save(f"Collected_Data/Images Kiremico/{pic_name}.png")
        return None

    def get_similar_artists(self):
        # Artists related through Spotify suggestions
        related_artists = self.sp.artist_related_artists(self.artist_id)

        artist_info = []
        for artist_el in related_artists['artists']:
            # Description format (name, followers, link to Spotify)
            name = artist_el['name']  # We get the name
            followers = artist_el['followers']['total']  # We get Spotify followers
            # Getting the artists link through what was submitted
            SPLink = f"https://open.spotify.com/artist/{self.sp.search(q=artist_el['name'], type='artist', limit=1)['artists']['items'][0]['id']}"
            artist_description = (name, followers, SPLink)
            artist_info.append(artist_description)

        artist_info = sorted(artist_info, key=lambda x: x[1])  # We sort artists by their following
        if len(artist_info) > 10:  # We don't do more than 10 artists suggested by Spotify
            return artist_info[:10]
        else:
            return artist_info

    def get_insta_link(self):
        # Every external link starts with rel. That's we get all the instances of those links
        all_rel = np.array([m.start() for m in re.finditer('rel', self.soup_str)])

        # We use try-except structure because the instagram link might be missing
        try:
            value = self.soup_str[self.soup_str.find('instagram.com') - 8: find_nearest(all_rel, self.soup_str.find(
                'instagram.com')) - 2]
        except:
            value = ''
        if value == '':
            # If the part of the string where Instagram link was supposed to be is empty, we return nothing
            return 'No Instagram'
        else:
            return value

    def get_instagram_followers(self):
        try:
            link = self.get_insta_link()
            if link != 'No Instagram':
                # As we don't want to run into problems with viewing instagram many times, we run requests library
                # Which is 10 times faster than using headless Chrome for our purposes
                string = str(BeautifulSoup(requests.get(link).content, 'html.parser'))
                Followers_raw = convert_num(string[string.find('property="og:url"') + 34: string.find('Followers') - 1])
                return Followers_raw
            else:
                return -1
        except:
            return -1

    def get_followers(self):
        if len(self.items) > 0:
            # Retrieve the number of Spotify followers for the artist
            followers = self.items['followers']['total']
            return followers
        else:
            return None

    def get_artist_radios(self):
        #Find all the instances of the word playlist, which is usually related to artist radio
        indexes = [m.start() for m in re.finditer('href="/playlist/', self.soup_str)]
        links = []
        for index in indexes:
            if contains_only_numbers_and_letters(self.soup_str[index + 6:index + 38]):
                links.append('https://open.spotify.com' + self.soup_str[index + 6:index + 38])
        return links

    def get_monthly_listeners(self):
        try:
            #Monthly listeners stat with a dot surrounded by spaces
            all_dot = np.array([m.start() for m in re.finditer(' · ', self.soup_str)])
            return convert_num(self.soup_str[
                               find_nearest(all_dot, self.soup_str.find('monthly listeners')) + 3:self.soup_str.find(
                                   'monthly listeners')])
        except:
            return 0

    def get_latest_release(self):
        # Search for the artist and his/her releases
        results = self.sp.artist_albums(self.artist_id)['items']
        results = sorted(results, key=lambda x: x['release_date'])
        return results[-1]['external_urls']['spotify']

    def get_genres(self):
        if len(self.items) > 0:
            # Retrieve the genres
            followers = self.items['genres']
            return followers
        else:
            return None

    def get_popularity(self):
        if len(self.items) > 0:
            # Retrieve the popularity
            followers = self.items['popularity']
            return followers
        else:
            return None

    def get_release_history(self):
        results = self.sp.artist_albums(self.artist_id)
        albums = results['items']
        while results['next']:
            results = self.sp.next(results)
            albums.extend(results['items'])
        # Setting up initial constants

        released_tracks = 0
        latest_release = self.CONST
        oldest_release = datetime.datetime.today()

        distance_between_tracks_list = []
        for i in range(len(albums)):
            if albums[i]['album_group'] != 'appears_on':  # We don't want to count features
                released_tracks += albums[i]['total_tracks']
                if len(albums[i]['release_date']) == 10:  # Checking for the format
                    time = datetime.datetime.strptime(albums[i]['release_date'], "%Y-%m-%d")
                    if latest_release != self.CONST:
                        time_difference = np.abs(time - last_time).total_seconds()
                        distance_between_tracks_list.append(int(time_difference // (60 * 60 * 24)))
                    if time > latest_release:
                        latest_release = time
                    if time < oldest_release:
                        oldest_release = time
                    last_time = time
        # Structure of the return (How long ago was the latest release (days), Frequency of production of songs (every N days) per song,
        # number of songs produced)
        if len(distance_between_tracks_list) == 0 or released_tracks == 0 or latest_release == self.CONST:
            return np.zeros(5)

        # Calculating the variables we care about
        avg_track_release_time = int((datetime.datetime.today() - oldest_release).total_seconds()
                                     / (60 * 60 * 24 * released_tracks))
        try:
            avg_time_between_releases = np.average(distance_between_tracks_list)
        except:
            avg_time_between_releases = 0

        time_since_latest_release = (datetime.datetime.today() - latest_release).total_seconds() / (60 * 60 * 24)
        career_time = int((datetime.datetime.today() - oldest_release).total_seconds() / (60 * 60 * 24))
        # 'Average Track Release Time (days)', 'Average Time Between Tracks (days)', 'Time Since Last Release (days)', 'Total Career'
        d = [avg_track_release_time, avg_time_between_releases, time_since_latest_release, career_time, released_tracks]
        return d

    def is_on_tour(self):
        # getting the html file using requests library
        if self.soup_str.find('On tour') == -1:
            return False
        else:
            return True

    def get_tour_info(self):
        URL = self.link + '/concerts'
        geolocator = Nominatim(user_agent="geoapiExercises")
        response = requests.get(URL)
        soup_str = str(BeautifulSoup(response.content, 'html.parser'))

        # Parsing the html data
        all_occurences_of_dates = re.findall("\d+\-\d+\-\d+", self.soup_str)
        all_occurences_of_lat = [m.start() for m in re.finditer('latitude', soup_str)]
        all_occurences_of_long = [m.start() for m in re.finditer('longitude', soup_str)]
        all_occurences_of_add = [m.start() for m in re.finditer('address":{', soup_str)]

        d = {'Date': all_occurences_of_dates, 'Location': [], 'Distance to main location (km)': []}
        for i in range(len(all_occurences_of_dates)):
            Latitude = soup_str[all_occurences_of_lat[i] + 10: all_occurences_of_long[i] - 2]
            Longitude = soup_str[all_occurences_of_long[i] + 11: all_occurences_of_add[i] - 2]
            location = geolocator.reverse(Latitude + "," + Longitude)
            coords_1 = (float(Latitude), float(Longitude))
            if location != None:
                d['Location'].append(location)
            else:
                d['Location'].append('')
            d['Distance to Berlin (km)'].append(geopy.distance.geodesic(coords_1, self.coords_B).km)
        # Returns a dictionary of {Date, Location, Distance} format
        return d

    def get_discovered_on_playlists(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(self.link + '/discovered-on')
        html = str(driver.execute_script("return document.documentElement.innerHTML;"))
        links = []
        all_occurrences = [m.start() for m in re.finditer('href="/playlist/', html)]
        if len(all_occurrences) > 5:
            all_occurrences = all_occurrences[:5]
        for occurrence in all_occurrences:
            links.append('https://open.spotify.com' + html[occurrence + 6:occurrence + 38])
        return links

    def get_instagram_info(self):
        try:
            link = self.get_insta_link()
            string = str(BeautifulSoup(requests.get(link).content, 'html.parser'))
            listing = [m.start() for m in re.finditer('dateCreated', string)]
            dates = []
            for i in range(1, len(listing)):
                if string[listing[i - 1]:listing[i]].find('dateModified') != -1:
                    dates.append(re.findall("\d+\-\d+\-\d+",string[listing[i - 1]:listing[i]])[0])
            comments_avg = np.average([int(m[16:-1]) for m in re.findall('"commentCount":"\d+"', string)])  # Average comments
            likes_avg = np.average(
                [int(m[23:]) for m in re.findall('"userInteractionCount":\d+', string) if int(m[23:]) != 0])  # Average likes
            sum = 0
            for i in range(1, len(dates)):
                sum += time_difference(dates[i], dates[i - 1]).total_seconds() // (60 * 60 * 24)
            avg_release_time = sum // (len(dates) - 1) # Average time in between posts on Insta in days
            return likes_avg, comments_avg, avg_release_time
        except:
            return -1, -1, -1
