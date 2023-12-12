import json
import pandas as pd 
import streamlit as st
from typing import Tuple, List
from tabulate import tabulate
from spotify_client import SpotifyClient


class SpotifyUnwrapped:
    """
    Class to analyse the data from the Spotify user data.
    """

    def __init__(self) -> None:
        """
        We set self.top_k_artists = 5 for consistency with the Spotfy Wrapped product.
        However, self.top_k_songs = 10 is set srbitrarily.
        """
        self.top_k_artists = 5
        self.top_k_songs = 10
        self.top_ks = {"artist" : self.top_k_artists, "songs": self.top_k_songs, "album" : self.top_k_artists}
        self.dataframes_finalised = False
        self.spotify_client = SpotifyClient()   

    def json_batch_update(self, fname:str | st.runtime.uploaded_file_manager.UploadedFile) -> pd.DataFrame:
        """
        Update the json file with the new data.
        Cleans the data so that it is in a format that is suitable to analyse 
        according to Spotify Wrapped requirements.
        """
        if isinstance(fname, str):
            with open(fname) as fname:
                json_data = json.load(fname)
        elif isinstance(fname, st.runtime.uploaded_file_manager.UploadedFile):
            json_data = json.load(fname)
        else:
            raise TypeError("Only str or Streamlit UploadedFile are acceptable.")

        df = pd.json_normalize(json_data)
        df['endTime'] = pd.to_datetime(df['endTime'], format='%Y-%m-%d %H:%M')
        df["minsPlayed"] = df["msPlayed"]/(60*1000) 
        df = df[df["endTime"].dt.strftime("%Y") == "2023"]
        df = df[df["endTime"].dt.strftime("%m") < "11"]
        df = df[df["minsPlayed"] > 0.5]
        return df
    
    def finalise_dataframes(self, dfs:List[pd.DataFrame]) -> None:
        """
        Sets the self.dataframes_finalised to True and separates the data into songs
        and podcasts using a simple rule of 10. minutes.
        To do: add more sophisticated approach to separate podcasts and songs.
        """
        if isinstance(dfs, pd.DataFrame):
            df = dfs 
        else:
            if len(dfs) == 0:
                raise ValueError("No dataframes to finalise.")
            elif len(dfs) == 1:
                df = dfs[0]
            else:
                df = pd.concat(dfs, axis=0)
        self.dataframes_finalised = True
        
        self.df = df#.iloc[:250] # remove for debugging later
        self.song_df = self.df[self.df["minsPlayed"] <= 10.]
        self.podcast_df = df[df["minsPlayed"] > 10.]

    def get_total_num_songs(self, df:pd.DataFrame) -> int:
        """
        Get the total number of songs listened to.
        """
        return df["trackName"].nunique()
    
    def get_yearly_top_artists(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get the top artists from the dataframe.
        """
        assert self.dataframes_finalised, "Dataframes have not been finalised."
        top_artists_num_plays = self.song_df[["artistName"]].value_counts().head(self.top_k_artists)#.index.tolist()
        top_artists_cum_time = self.song_df.groupby("artistName").agg({"minsPlayed": "sum"}).sort_values(by="minsPlayed", ascending=False).head(self.top_k_artists)#.index.tolist()

        # reset headers for compatibility with Altair
        top_artists_num_plays = top_artists_num_plays.reset_index().rename(columns={"count" : "Streams", "artistName" : "Artist"})
        top_artists_cum_time = top_artists_cum_time.reset_index().rename(columns={"minsPlayed" : "Time (hours)", "artistName" : "Artist"})
        top_artists_cum_time["Time (hours)"] /= 60
        return top_artists_num_plays, top_artists_cum_time
    
    def get_yearly_top_songs(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        assert self.dataframes_finalised, "Dataframes have not been finalised."
        top_songs_num_plays = self.song_df[["trackName"]].value_counts().head(self.top_k_songs)#.index.tolist()
        top_songs_cum_time = self.song_df.groupby("trackName").agg({"minsPlayed": "sum"}).sort_values(by="minsPlayed", ascending=False).head(self.top_k_songs)#.index.tolist()

        # reset headers for compatibility with Altair
        top_songs_num_plays = top_songs_num_plays.reset_index().rename(columns={"count" : "Streams", "trackName" : "Track"})
        top_songs_cum_time = top_songs_cum_time.reset_index().rename(columns={"minsPlayed" : "Time (hours)", "trackName" : "Track"})
        top_songs_cum_time["Time (hours)"] /= 60
        return top_songs_num_plays, top_songs_cum_time
    
    def get_yearly_top_podcasts(self) -> pd.DataFrame:
        assert self.dataframes_finalised, "Dataframes have not been finalised."
        top_podcasts_num_plays = self.podcast_df[["artistName"]].value_counts().head(self.top_k_artists)
        top_podcast_cum_time = self.podcast_df.groupby("artistName").agg({"minsPlayed": "sum"}).sort_values(by="minsPlayed", ascending=False).head(self.top_k_artists)  

        # reset headers for compatibility with Altair
        top_podcasts_num_plays = top_podcasts_num_plays.reset_index().rename(columns={"count" : "Streams", "artistName" : "Podcast"})
        top_podcast_cum_time = top_podcast_cum_time.reset_index().rename(columns={"minsPlayed" : "Time (hours)", "artistName" : "Podcast"})
        top_podcast_cum_time["Time (hours)"] /= 60
        return top_podcasts_num_plays, top_podcast_cum_time
    
    def get_yearly_top_albums(self, sample_rate:float=0.01) -> list:
        """
        To do: Replace with sampling for this step to avoid querying everything.
        """
        assert 0 < sample_rate <= 1, "Sample rate must be between 0 and 1."
        assert self.dataframes_finalised, "Dataframes have not been finalised."
        artist_song_list = list(self.song_df[["artistName", "trackName"]].itertuples(index=False, name=None))
        print(artist_song_list)
        album_list = self.spotify_client.get_album_from_song_list(artist_song_list, sample_rate)
        self.song_df["albumName"] = album_list
        print(self.song_df)
        top_albums_num_plays = self.song_df[["albumName"]].value_counts().head(self.top_ks["album"])
        top_albums_cum_time = self.song_df.groupby("albumName").agg({"minsPlayed": "sum"}).sort_values(by="minsPlayed", ascending=False).head(self.top_ks["album"])  

        # reset headers for compatibility with Altair
        top_albums_num_plays = top_albums_num_plays.reset_index().rename(columns={"count" : "Streams", "albumName" : "Album"})
        top_albums_cum_time = top_albums_cum_time.reset_index().rename(columns={"minsPlayed" : "Time (hours)", "albumName" : "Album"})
        top_albums_cum_time["Time (hours)"] /= 60
        print(top_albums_num_plays)
        print(top_albums_cum_time)
        return top_albums_num_plays, top_albums_cum_time

    def add_genres_to_df(self, df:pd.DataFrame) -> pd.DataFrame:
        """
        Add the genres to the dataframe.
        """
        all_artists = list(df["artistName"].unique())
        #Slow! -->artist_to_genres = {a : a["genres"] for a in spotify_client.get_genres_from_artist_list(all_artists[:10])}
        resp = self.spotify_client.get_genres_from_artist_list(all_artists)
        genre_df = pd.DataFrame(resp).T
        genre_df.drop(columns=["count"], inplace=True)
        genre_df.reset_index()
        genre_dict = genre_df.to_dict()["genres"]
        df["genres"] = df['artistName'].map(genre_dict) 
        return df
    
    # def get_yearly_top_genres(self, df:pd.DataFrame) -> list:
    #     artist_to_genres = []
        #resp = self.spotify_client.get_genres_from_artist_list(all_artists)
        #
        #spotify_client = SpotifyClient()
        #artist_to_genres = {a : a["genres"] for a in spotify_client.get_genres_from_artist_list(all_artists[:10])}
        # for a in spotify_client.get_genres_from_artist_list(all_artists[:10]):
        #     print(a, )
        # print(len(artist_to_genres))
        # print(artist_to_genres) 


        #print(test_df)
        # test_dfpd.merge(test_df, genre_df, on="artistName", how="left")
        
        # print(test_df)
        # print(df.head())
        # for i, (_, row) in enumerate(df.iterrows()):
        #     if i < 637:
        #         continue
        #     _, artist_id = spotify_client.search_for_artist_id(row["artistName"])
        #     genres = spotify_client.get_genre_from_artist(artist_id)
        #     print(i, _, row["trackName"], row["artistName"], genres)

    # def get_yearly_artist_summaries(self) -> (pd.DataFrame, pd.DataFrame):
    #     """Uses the yearly artist summaries to make the bar charts"""
    #     artist_streams = [ [a[0], a[1]] for a in self.yearly_artists_num_plays.get_frequent_items(frequent_items_error_type.NO_FALSE_POSITIVES)[:self.top_k_artists]]
    #     artist_times = [ [a[0], a[1] / 60] for a in self.yearly_artists_cum_time.get_frequent_items(frequent_items_error_type.NO_FALSE_POSITIVES)[:self.top_k_artists]]
    #     play_df = pd.DataFrame(artist_streams, columns=["Artist", "Streams"])
    #     time_df = pd.DataFrame(artist_times, columns=["Artist", "Time (hours)"])
    #     play_df.sort_values(by="Streams", inplace=True, ascending=False)
    #     time_df.sort_values(by="Time (hours)", inplace=True, ascending=False)
    #     return play_df, time_df  
            
            
        


