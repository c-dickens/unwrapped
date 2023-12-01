import os 
import base64
import requests 
import json
from dotenv import load_dotenv
from tabulate import tabulate

class SpotifyClient:
    def __init__(self):
        load_dotenv() # need .env in same directory as main.py
        self.client_id = os.getenv("CLIENT_ID")
        self.client_secret = os.getenv("CLIENT_SECRET")
        pass
    
    def set_token(self) -> None:
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
    
    def search_for_artist_id(self, artist_name:str) -> tuple[str, str] | None:
        """returns (artist_name, artist_id)""" 
        url = "https://api.spotify.com/v1/search"
        headers = self.get_auth_header()
        params = {"q" : artist_name, "type" : "artist"} # equivalent to query = f"q={artist_name}&type=artist&limit=1"
        result = requests.get(url, headers=headers, params=params)
        json_result = json.loads(result.content)["artists"]["items"]
        if len(json_result) == 0:
            print(f"Could not find artist {artist_name}")
            return None
        else:
            return json_result[0]["name"], json_result[0]["id"]

    def get_songs_by_artist(self, artist_id:str) -> dict:
        url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks"
        headers = self.get_auth_header()
        params = {"country" : "GB"}
        result = requests.get(url, headers=headers, params=params)
        json_result = json.loads(result.content)["tracks"]
        return json_result

    def print_songs(self, songs:dict) -> None:
        # Create a list of lists for tabulation
        table_data = [[idx + 1, song['name'], song['album']['name']] for idx, song in enumerate(songs)]
        headers = ["#", "Song Name", "Album Name"]
        print(tabulate(table_data, headers, tablefmt="fancy_grid"))
