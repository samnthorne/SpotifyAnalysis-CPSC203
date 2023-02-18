import pandas as pd
from dataclasses import dataclass, field, asdict
from typing import List, Tuple
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import json
import billboard
from collections import defaultdict, Counter
from models import *
import matplotlib.patches as mpatches
import plotly.express as px

#spotipy wraps the official spotify api providing simple python functions.
# TODO: Replace these two variables with the client_id and client_secret that you generated
CLIENT_ID = "5914d85622154ebf81922c8c9a7ac5b1"
CLIENT_SECRET = "4e041c4ddd3a4038be845492f61e5e4b"

#https://developer.spotify.com/dashboard/applications to get client_id and client_secret
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=CLIENT_ID,
                                                           client_secret=CLIENT_SECRET))


# ----------------------------------------------------------------------------------------------------------------

def getPlaylist(id: str) -> List[Track]:
    '''
    Given a playlist ID, returns a list of Track objects corresponding to the songs on the playlist. See
    models.py for the definition of dataclasses Track, Artist, and AudioFeatures.
    We need the audio features of each track to populate the audiofeatures list.
    We need the genre(s) of each artist in order to populate the artists in the artist list.

    We've written parts of this function, but it's up to you to complete it!
    '''
    
    # fetch tracks data from spotify given a playlist id
    playlistdata = sp.playlist(id)
    tracks = playlistdata['tracks']['items'] # is a list containing all the information each track in the playlist.
    # print(json.dumps(tracks, indent=4))
    # print(s['track']['id'] for s in tracks)
    # The contents are mostly dictionaries
    # print(s['track']['artists']['id'] for s in tracks)


    # fetch audio features based on the data stored in the playlist result
    track_ids = [s['track']['id'] for s in tracks]  # TODO: build a list of track_ids from the tracks
    # print(track_ids)


    audio_features = sp.audio_features(track_ids)
    # print(json.dumps(audio_features, indent=4))

    audio_info = {}  # Audio features list might not be in the same order as the track list
    for af in audio_features:
        audio_info[af['id']] = AudioFeatures(af['danceability'], \
                                             af['energy'], \
                                             af['key'],  \
                                             af['loudness'],  \
                                             af['mode'],  \
                                             af['speechiness'], \
                                             af['acousticness'], \
                                             af['instrumentalness'], \
                                             af['liveness'], \
                                             af['valence'], \
                                             af['tempo'], \
                                             af['duration_ms'], \
                                             af['time_signature'], \
                                             af['id'])


    # prepare artist dictionary
    # all_artist_ids0 = [a['track']['artists'][0]['id'] for a in tracks] # Figure out how to include all artists for each song later!
    # all_artist_ids1 = [a['track']['artists'][1]['id'] for a in tracks]
    # print(all_artist_ids0)

    artist_ids = []
    for a in tracks:
        for b in a['track']['artists']:
            if b not in artist_ids:
                artist_ids.append(b['id'])


    #artist_ids = [i for n, i in enumerate(all_artist) if i not in all_artist[:n]] # TODO: make a list of unique artist ids from tracks list
    # print(artist_ids)

    artists = {}

    for k in range(1+len(artist_ids)//50): # can only request info on 50 artists at a time!
        artists_response = sp.artists(artist_ids[k*50:min((k+1)*50, len(artist_ids))]) #what is this doing?
        for a in artists_response['artists']:
            artists[a['id']] = Artist(a['id'],
                                      a['name'],
                                      a['genres']) # TODO: create the Artist for each id (see audio_info, above)


    # populate track dataclass
        # the ids can come from the index of the track_id list or just repulled on its own
        # the name can simply be pulled on its own via track['track']['name']
        # the artists needs to be changed above to be a list of artist for each song.
        # we need a list of the dataclass Artist.
        # The key is the artist id so that needs to be pulled and then can be input into the dictionary.
        # audiofeatures is audioinfo, which is a dictionary with the key as the track id,
        # maybe use index that matches the original id to find this?

    # art.append(Artist[t['track']['artists'][q]['id']] for q in range(len(t['track']['artists'])))


    trackList = []
    for t in tracks:
        trackList.append(Track(id = t['track']['id'],
                               name = t['track']['name'],
                               artists = [artists[t['track']['artists'][q]['id']] for q in range(len(t['track']['artists']))],
                               audio_features = audio_info[t['track']['id']]))

    '''   
    [Artist[t['track']['artists'][q]['id']] for q in range(len(t['track']['artists']))]
    trackList = [Track(id = tracks['track']['id'],  # TODO: your code here     , \  # id: str
                       name= tracks['track']['name'],  # TODO: your code here    , \  # name: str
                       artists= [Artist[t['track']['artists'][]['id']],  # TODO: your code here , \  # artists = List[Artist]
                       audio_features= audio_info[t['track']['id']])]  # TODO: your code here ) \  # audio_features = AudioFeatures
    '''
    return trackList

# print(getPlaylist('0G4eZwPeA0O04wlSXZfkE0'))

# -----------------------------------------------------------------------------------------------------------------

''' this function is just a way of naming the list we're using. You can write
additional functions like "top Canadian hits!" if you want.'''
def getHot100() -> List[Track]:
    # Billboard hot 100 Playlist ID URI
    hot_100_id = "6UeSakyzhiEt4NB3UAd6NQ"
    return getPlaylist(hot_100_id)

def random_playlist() -> List[Track]:
    random = '0G4eZwPeA0O04wlSXZfkE0'
    return getPlaylist(random)

# ----------------------------------------------------------------------------------------------------------------

# part1: implement helper functions to organize data into DataFrames

def getGenres(t: Track) -> List[str]:
    '''
    TODO
    Takes in a Track and produce a list of unique genres that the artists of this track belong to
    '''
    genress = []
    for a in t.artists:
        for g in a.genres:
            if g not in genress:
                genress.append(g)
    return genress
# print(getGenres(Track(id='3PdcxgzpWzAsUGgkmykIFc', name='Welcome to Chilis', artists=[Artist(id='2YOYua8FpudSEiB9s88IgQ', name='Yung Gravy', genres=['meme rap', 'minnesota hip hop', 'pop rap']), Artist(id='41X1TR6hrK8Q2ZCpp2EqCz', name='bbno$', genres=['canadian hip hop', 'dark trap', 'meme rap', 'pop rap', 'vapor trap'])], audio_features=AudioFeatures(danceability=0.839, energy=0.454, key=10, loudness=-9.09, mode=0, speechiness=0.157, acousticness=0.359, instrumentalness=0, liveness=0.0755, valence=0.804, tempo=159.987, duration_ms=157500, time_signature=4, id='3PdcxgzpWzAsUGgkmykIFc'))))

def doesGenreContains(t: Track, genre: str) -> bool:
    '''
    TODO
    Checks if the genres of a track contains the key string specified
    For example, if a Track's unique genres are ['pop', 'country pop', 'dance pop']
    doesGenreContains(t, 'dance') == True
    doesGenreContains(t, 'pop') == True
    doesGenreContains(t, 'hip hop') == False
    '''
    if genre in getGenres(t):
        return True
    else:
        return False

# print(doesGenreContains(Track(id='3PdcxgzpWzAsUGgkmykIFc', name='Welcome to Chilis', artists=[Artist(id='2YOYua8FpudSEiB9s88IgQ', name='Yung Gravy', genres=['meme rap', 'minnesota hip hop', 'pop rap']), Artist(id='41X1TR6hrK8Q2ZCpp2EqCz', name='bbno$', genres=['canadian hip hop', 'dark trap', 'meme rap', 'pop rap', 'vapor trap'])], audio_features=AudioFeatures(danceability=0.839, energy=0.454, key=10, loudness=-9.09, mode=0, speechiness=0.157, acousticness=0.359, instrumentalness=0, liveness=0.0755, valence=0.804, tempo=159.987, duration_ms=157500, time_signature=4, id='3PdcxgzpWzAsUGgkmykIFc')), 'pop rap'))
# print(doesGenreContains(Track(id='3PdcxgzpWzAsUGgkmykIFc', name='Welcome to Chilis', artists=[Artist(id='2YOYua8FpudSEiB9s88IgQ', name='Yung Gravy', genres=['meme rap', 'minnesota hip hop', 'pop rap']), Artist(id='41X1TR6hrK8Q2ZCpp2EqCz', name='bbno$', genres=['canadian hip hop', 'dark trap', 'meme rap', 'pop rap', 'vapor trap'])], audio_features=AudioFeatures(danceability=0.839, energy=0.454, key=10, loudness=-9.09, mode=0, speechiness=0.157, acousticness=0.359, instrumentalness=0, liveness=0.0755, valence=0.804, tempo=159.987, duration_ms=157500, time_signature=4, id='3PdcxgzpWzAsUGgkmykIFc')), 'pop'))

# ----------------------------------------------------------------------------------------------------------------

def getTrackDataFrame(tracks: List[Track]) -> pd.DataFrame:
    '''
    This function is given.
    Prepare dataframe for a list of tracks
    audio-features: 'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness',
                    'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo',
                    'duration_ms', 'time_signature', 'id', 
    track & artist: 'track_name', 'artist_ids', 'artist_names', 'genres', 
                    'is_pop', 'is_rap', 'is_dance', 'is_country'
    '''
    # populate records
    records = []
    for t in tracks:
        to_add = asdict(t.audio_features) #converts the audio_features object to a dict
        to_add["track_name"] = t.name
        to_add["artist_ids"] = list(map(lambda a: a.id, t.artists)) # we will discuss this in class
        to_add["artist_names"] = list(map(lambda a: a.name, t.artists))
        to_add["genres"] = getGenres(t)
        to_add["is_pop"] = doesGenreContains(t, "pop")
        to_add["is_rap"] = doesGenreContains(t, "rap")
        to_add["is_dance"] = doesGenreContains(t, "dance")
        to_add["is_country"] = doesGenreContains(t, "country")
        
        records.append(to_add)
        
    # create dataframe from records
    df = pd.DataFrame.from_records(records)
    return df

# minor testing code:
top100Tracks = getHot100()
df = getTrackDataFrame(top100Tracks)
# you may want to experiment with the dataframe now!
# print(df)

# ----------------------------------------------------------------------------------------------------------------
# Part2: The most popular artist of the week

def artist_with_most_tracks(tracks: List[Track]) -> (Artist, int):
    '''
    TODO
    List of tracks -> (artist, number of tracks the artist has)
    This function finds the artist with most number of tracks on the list
    If there is a tie, you may return any of the artists
    '''

    artist = []
    for t in tracks:
        for a in t.artists:
            artist.append(a)

    art_id = [] # this is a list of artist ids
    for h in artist:
        art_id.append(h.id)

    for a in artist:
        artists = {a.id: a}

    #tally = Counter(art_id)
    # max = tally.most_common()

    full_count = [[x, art_id.count(x)] for x in set(art_id)] # this is a list of lists with the artist id and the number of times in appears.

    one_left = [0, 0]
    for p in full_count:
        if p[1] > one_left[1]:
            one_left = p

    for a in artist:
        if a.id == one_left[0]:
            the_artist = a
    return the_artist, one_left[1]

# print(artist_with_most_tracks(top100Tracks))

# minor testing code:
artist, num_track = artist_with_most_tracks(top100Tracks)
print("%s has the most number of tracks on this week's Hot 100 at a whopping %d tracks!" % (artist.name, num_track))


# -----------------------------------------------------------------------------------------------------

# Part3: Data Visualization

# 3.1 scatter plot of dancability-tempo colored by genre is_rap
# On a scatter plot, display all the tracks with "danceability" as x-axis and "speechiness" as y-axis.
# Color the dots based on whether the track "is_rap". Label the axis of the plot and add a legend.

# need to make a list of the top100 danceability
# need to make a list with top100 speechiness

def top100_sd_plt(df):
    not_rap = df.loc[df['is_rap'] == False]
    is_rap = df.loc[df['is_rap'] == True]

    vs = plt.gca()
    not_rap.plot(kind = 'scatter', x = 'danceability', y = 'speechiness', c = 'blue', ax = vs)
    is_rap.plot(kind = 'scatter', x = 'danceability', y = 'speechiness', c = 'green', ax = vs)
    plt.tight_layout()
    plt.xlabel('Danceability')
    plt.ylabel('Speechiness')
    plt.title("Spotify's top 100 playlist")
    green_patch = mpatches.Patch(color = 'green', label = 'Is rap')
    blue_patch = mpatches.Patch(color = 'blue', label = 'Is not rap')
    plt.legend(handles = [blue_patch, green_patch], loc = 'upper left')
    plt.show()
    return None

print(top100_sd_plt(df))

# ---------------------------------------------------------------------------------------------------------------
# 3.2 scatter plot (ask your own question)

# compare the energy to the duration_ms of the song in relation to how many artists worked on each song, artist_ids
# make new column of the number of artists in the track
# change duration to be in seconds rather than ms
# maybe change the duration into minutes so it is easier to understand
def divide_thousand(x):
    return x/1000

def to_min(x):
    return x/60

needed = df
for a in needed['artist_ids']:
    needed['num_art'] = [str(len(a)) for a in needed['artist_ids']]
# needed['num_art'] = needed[int(needed['num_art'])]
needed['dur_sec'] = needed['duration_ms'].apply(divide_thousand)
needed['duration_min'] = needed['dur_sec'].apply(to_min)

def discovery_plot(df):

    one_art = needed[needed['num_art'] == '1']
    two_art = needed[needed['num_art'] == '2']
    three_art = needed[needed['num_art'] == '3']
    four_art = needed[needed['num_art'] == '4']

    all_art = plt.gca()
    one_art.plot(kind = 'scatter', x = 'duration_min', y = 'energy', c = 'orange', ax = all_art)
    two_art.plot(kind = 'scatter', x = 'duration_min', y = 'energy', c = 'green', ax = all_art)
    three_art.plot(kind = 'scatter', x = 'duration_min', y = 'energy', c = 'blue', ax = all_art)
    four_art.plot(kind = 'scatter', x = 'duration_min', y = 'energy', c = 'red', ax = all_art)
    plt.tight_layout()
    plt.xlabel('Duration in minutes')
    plt.ylabel('Energy of track')
    plt.title('Relations to the duration of songs')
    one_p = mpatches.Patch(color = 'orange', label = 'One Artist')
    two_p = mpatches.Patch(color = 'green', label = 'Two Artists')
    three_p = mpatches.Patch(color = 'blue', label = 'Three Artists')
    four_p = mpatches.Patch(color = 'red', label = 'Four Artists')
    plt.legend(handles = [one_p, two_p, three_p, four_p], title = 'Number of Artists on Track')
    plt.show()


    return None

print(discovery_plot(df))


# ---------------------------------------------------------------------------------------------------------------

# (Bonus) Part4: 
# take a song that's not on the list, compute distance with the songs on the list and see if we get the same artist

# For the bonus I just tried to use plotly.
# I made the same graph as above with the hover function and to be displayed on plotly
# I also changed the y-axis to tempo because I was curious how tempo relates to the duration
def plotly_plot(df):
    graph = px.scatter(needed, x = 'duration_min', y = 'tempo', color = 'num_art', hover_data = ['track_name', 'artist_names'],
                       labels = dict(duration_min = 'Duration of song (min)', tempo = 'Tempo (beats/min)', num_art = 'Number of artists in track',
                                     track_name = 'Name of track', artist_names = 'Artists'),
                       title = 'Duration of songs compared to tempo and number of artists')
    graph.show()
    return None

print(plotly_plot(df))
