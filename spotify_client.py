import os 
import base64
import requests 
import json
import numpy as np
from dotenv import load_dotenv
from tabulate import tabulate
from thefuzz import fuzz
import warnings
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from typing import List, Tuple
from pprint import PrettyPrinter

class SpotifyClient:
    def __init__(self):
        load_dotenv() # need .env in same directory as main.py
        self.client_id = os.getenv("CLIENT_ID")
        self.client_secret = os.getenv("CLIENT_SECRET")
        self._set_token()
        client_credentials_manager = SpotifyClientCredentials(client_id=self.client_id, client_secret=self.client_secret)
        self.sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    
    def _set_token(self) -> None:
        """
        Sets the class token attribute to the access token from Spotify API
        """
        auth_string = f"{self.client_id}:{self.client_secret}"
        auth_bytes = auth_string.encode("utf-8")
        auth_base64 = str(base64.b64encode(auth_bytes), "utf-8") 
        url = "https://accounts.spotify.com/api/token"
        headers = {
            "Authorization" : f"Basic {auth_base64}",
            "Content-Type" : "application/x-www-form-urlencoded"
        }
        data = {"grant_type" : "client_credentials"}
        result = requests.post(url, headers=headers, data=data)
        json_result = json.loads(result.content)
        self.token = json_result["access_token"]

    def get_auth_header(self) -> dict:
        return {"Authorization" : f"Bearer {self.token}"}
    
    def search_for_artist_id(self, artist_name:str, track:str=None) -> tuple[str, str] | tuple[None, None]:
        """returns (artist_name, artist_id)""" 
        url = "https://api.spotify.com/v1/search"
        headers = self.get_auth_header()
        params = {"q" : artist_name, "type" : "artist", "limit": 5} # equivalent to query = f"q={artist_name}&type=artist&limit=1"
        result = requests.get(url, headers=headers, params=params)
        json_result = json.loads(result.content)["artists"]["items"]
        if len(json_result) == 0:
            warning_message = f"Could not find artist {artist_name}"
            warnings.warn(warning_message, UserWarning)
            return None, None
        test_artist_name = json_result[0]["name"]
        if test_artist_name.lower() == artist_name.lower():
            return json_result[0]["name"], json_result[0]["id"]
        else:
            # no match - lookup and do manual match
            # We need this fix for ambiguous names (eg. Dave, Beck)
            # Modified from https://stackoverflow.com/questions/65101111/spotipy-wrong-several-artist-coming-up-when-i-use-sp-search
            artist_names = [artist["name"] for artist in json_result]
            artist_scores = np.array([fuzz.ratio(artist_name, artist) for artist in artist_names])
            selected_artist_idx = np.argmax(artist_scores)
            return json_result[selected_artist_idx]["name"], json_result[selected_artist_idx]["id"]

    def get_songs_by_artist(self, artist_id:str) -> dict:
        url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks"
        headers = self.get_auth_header()
        params = {"country" : "GB"}
        result = requests.get(url, headers=headers, params=params)
        json_result = json.loads(result.content)["tracks"]
        return json_result
    
    def get_album_from_song(self, song_name:str, artist_name:str) -> str:
        """
        nb. not an obvious way to optimize this by memoizing the seen 
        artists (as in for genres) because artists have one list of genres
        but multiple distinct albums.
        """
        results = self.sp.search(q=f'track:{song_name} artist:{artist_name}', type='track')
        track = results['tracks']['items']
        if len(track) == 0:
            warning_message = f"Could not find song {song_name} by {artist_name}"
            warnings.warn(warning_message, UserWarning)
            return None
        track = track[0]
        album_name = track['album']['name']
        return album_name
    
    def get_album_from_song_list(self, artist_song_list:list, sample_rate:float=0.1) -> dict:
        """
        Given a list of (song, artist) pairs, return a dictionary of (song, album) pairs.
        """
        np.random.seed(235151123) # arbitrary seed
        n = len(artist_song_list)
        sample_size = np.ceil(sample_rate*n).astype(int)
        sampled_ids = np.random.choice(n, sample_size, replace=False)
        sampled_data = [artist_song_list[i] for i in sampled_ids]
        print(f"SAMPLING {sample_size} IDS from {n} total")
        song_albums = [None for _ in range(len(artist_song_list))]
        song_album_dict = {}
        #for i, (artist, song) in enumerate(artist_song_list):
        for i, (artist, song) in enumerate(sampled_data):
            print(i)
            if artist in song_album_dict and song in song_album_dict[artist]:
                song_albums[i] = song_album_dict[artist][song]
                continue
            album = self.get_album_from_song(song, artist)
            #song_albums[i] = album
            song_albums[sampled_ids[i]] = album
            song_album_dict[artist] = {}
            song_album_dict[artist][song] = album
        return song_albums #list(song_album_dict.values())
        
    def get_genre_from_artist(self, artist_id:str) -> list :
        """
        Returning an empty list for consistency between output modes on if conditional
        """
        url = f"https://api.spotify.com/v1/artists/{artist_id}"
        headers = self.get_auth_header()
        result = requests.get(url, headers=headers)
        if result.status_code == 400:
            # invalid query
            return []
        json_result = json.loads(result.content)
        if json_result is not None:
            return json_result["genres"]
        return []
    
    def get_genres_from_artist_list(self, artist_list:list) -> list:
        artist_genres = {}
        for artist in artist_list:
            if artist in artist_genres.keys():
                artist_genres[artist]["count"] += 1
            else:
                # not in dict so perform the lookup
                _, artist_id = self.search_for_artist_id(artist)
                genres = self.get_genre_from_artist(artist_id)
                artist_genres[artist] = {"genres" : genres, "count" : 1}
        return artist_genres

    def print_songs(self, songs:dict) -> None:
        # Create a list of lists for tabulation
        table_data = [[idx + 1, song['name'], song['album']['name']] for idx, song in enumerate(songs)]
        headers = ["#", "Song Name", "Album Name"]
        print(tabulate(table_data, headers, tablefmt="fancy_grid"))

    # def get_genres_from_song(self, song_id:str) -> list:
    #     url = f"https://api.spotify.com/v1/tracks/{song_id}"
    #     headers = self.get_auth_header()
    #     result = requests.get(url, headers=headers)
    #     json_result = json.loads(result.content)["artists"][0]["genres"]
    #     #print(song_id, json_result)
    #     return json_result
