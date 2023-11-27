import altair as alt
import streamlit as st
import json
import pandas as pd 
import numpy as np
from datasketches import frequent_strings_sketch, frequent_items_error_type 
from openai import OpenAI



class SketchUnwrapper:
    def __init__(self) -> None:
        """
        Spotify data uses months January-October for the Unwrapped tool so months [1, 10]
        """
        self.artist_k = 7
        self.songs_k = 10
        self.sketch_ks = {"artist" : self.artist_k, "songs" : self.songs_k}
        self.top_k_artists = 5
        self.top_k_songs = 10
        self.top_ks = {"artist" : self.top_k_artists, "songs": self.top_k_songs}
        self.sza_count = 0

        # Artist sketches
        self.monthly_artists_num_plays = {m : frequent_strings_sketch(8) for m in range(1,11)}
        self.monthly_artists_cum_time = {m : frequent_strings_sketch(9) for m in range(1,11)}
        self.yearly_artists_num_plays = frequent_strings_sketch(self.artist_k)
        self.yearly_artists_cum_time = frequent_strings_sketch(self.artist_k)

        # Song sketches 
        self.monthly_songs_num_plays = {m : frequent_strings_sketch(self.songs_k) for m in range(1,11)}
        self.monthly_songs_cum_time = {m : frequent_strings_sketch(self.songs_k) for m in range(1,11)}
        self.yearly_songs_num_plays = frequent_strings_sketch(self.songs_k)
        self.yearly_songs_cum_time = frequent_strings_sketch(self.songs_k)

        self.fi_sk = frequent_strings_sketch(self.artist_k)

    def minibatch_update(self, df:pd.DataFrame) -> None:
        """
        Updates the monthly sketches with the current minibatch defined by df
        """
        for _, row in df.iterrows():
            self.monthly_artists_num_plays[row["endTime"].month].update(item=row["artistName"], weight=1)
            self.monthly_artists_cum_time[row["endTime"].month].update(item=row["artistName"], weight=np.ceil(row["minsPlayed"]).astype(int))
            self.monthly_songs_num_plays[row["endTime"].month].update(item=row["trackName"], weight=1)
            self.monthly_songs_cum_time[row["endTime"].month].update(item=row["trackName"], weight=np.ceil(row["minsPlayed"]).astype(int))

    def update_yearly_sketches(self,) -> None:
        """
        Merges all of the monthly summaries into a sketch for the full year.
        """
        for month, month_sk in self.monthly_artists_num_plays.items():
            self.yearly_artists_num_plays.merge(month_sk)
            self.yearly_artists_cum_time.merge(self.monthly_artists_cum_time[month])    
        for month, month_sk in self.monthly_songs_num_plays.items():
            self.yearly_songs_num_plays.merge(month_sk)
            self.yearly_songs_cum_time.merge(self.monthly_songs_cum_time[month])  

    def make_yearly_top_artists(self, df:pd.DataFrame) -> None:
        for _, row in df.iterrows():
            if row["minsPlayed"] > 0.5:
                self.monthly_artists_num_plays[row["endTime"].month].update(item=row["artistName"], weight=1)
                self.monthly_artists_cum_time[row["endTime"].month].update(item=row["artistName"], weight=np.ceil(row["minsPlayed"]).astype(int))
        for month, month_sk in self.monthly_artists_num_plays.items():
            self.yearly_artists_num_plays.merge(month_sk)
            self.yearly_artists_cum_time.merge(self.monthly_artists_cum_time[month])    

    def get_yearly_artist_summaries(self) -> (pd.DataFrame, pd.DataFrame):
        """Uses the yearly artist summaries to make the bar charts"""
        artist_streams = [ [a[0], a[1]] for a in self.yearly_artists_num_plays.get_frequent_items(frequent_items_error_type.NO_FALSE_POSITIVES)[:self.top_k_artists]]
        artist_times = [ [a[0], a[1] / 60] for a in self.yearly_artists_cum_time.get_frequent_items(frequent_items_error_type.NO_FALSE_POSITIVES)[:self.top_k_artists]]
        play_df = pd.DataFrame(artist_streams, columns=["Artist", "Streams"])
        time_df = pd.DataFrame(artist_times, columns=["Artist", "Time (hours)"])
        play_df.sort_values(by="Streams", inplace=True, ascending=False)
        time_df.sort_values(by="Time (hours)", inplace=True, ascending=False)
        return play_df, time_df  

    # def make_yearly_top_songs(self, df:pd.DataFrame) -> None:
    #     for _, row in df.iterrows():
    #         if row["minsPlayed"] > 0.5:
    #             self.monthly_songs_num_plays[row["endTime"].month].update(item=row["trackName"], weight=1)
    #             self.monthly_songs_cum_time[row["endTime"].month].update(item=row["trackName"], weight=np.ceil(row["minsPlayed"]).astype(int))
    #     for month, month_sk in self.monthly_songs_num_plays.items():
    #         self.yearly_songs_num_plays.merge(month_sk)
    #         self.yearly_songs_cum_time.merge(self.monthly_songs_cum_time[month])   

    def get_yearly_song_summaries(self) -> (pd.DataFrame, pd.DataFrame):
        """Uses the yearly artist summaries to make the bar charts"""
        track_streams = [ [a[0], a[1]] for a in self.yearly_songs_num_plays.get_frequent_items(frequent_items_error_type.NO_FALSE_POSITIVES)[:self.top_k_songs]]
        track_times = [ [a[0], a[1] / 60] for a in self.yearly_songs_cum_time.get_frequent_items(frequent_items_error_type.NO_FALSE_POSITIVES)[:self.top_k_songs]]
        play_df = pd.DataFrame(track_streams, columns=["Track", "Streams"])
        time_df = pd.DataFrame(track_times, columns=["Track", "Time (hours)"])
        play_df.sort_values(by="Streams", inplace=True, ascending=False)
        time_df.sort_values(by="Time (hours)", inplace=True, ascending=False)
        return play_df, time_df 

def main():
    
    st.title("Unwrapping Spotify's Unwrapped")

    # upload all of the json files
    uploaded_file = st.file_uploader("Choose a JSON file", accept_multiple_files=True, type=["json"])
    sketching_complete = False
    if uploaded_file is not None:
        # the main object that we will update with each item
        sk_wrap = SketchUnwrapper()

        # stream the data
        for file in uploaded_file:
            json_data = json.load(file)
            # Step 2: Convert JSON data to a DataFrame
            df = pd.json_normalize(json_data)
            # df = pd.read_csv(uploaded_file, header=0, names=dtypes.keys(),
            #             dtype=dtypes, parse_dates=parse_dates)
            df['endTime'] = pd.to_datetime(df['endTime'], format='%Y-%m-%d %H:%M')
            df["minsPlayed"] = df["msPlayed"]/(60*1000) 
            df = df[df["endTime"].dt.strftime("%Y") == "2023"]
            df = df[df["endTime"].dt.strftime("%m") < "11"]
            df = df[df["minsPlayed"] > 0.5]
            sk_wrap.minibatch_update(df)
    
        # outputs
        st.write("## Unwrapping your 2023 Spotify Data...")
        sk_wrap.update_yearly_sketches() # merge the month summaries into the year summary
        
        # artist plots
        artist_plays, artist_time = sk_wrap.get_yearly_artist_summaries()
        for a, lab in zip([artist_plays, artist_time], ["Streams", "Time (hours)"]):
            if lab == "Streams":
                out = "number of streams"
            else:
                out = "total time (hours)"
            st.write(f"### Your top 5 artists by {out} are...")
            st.write(alt.Chart(a).mark_bar().encode(
                x=lab,
                y=alt.Y("Artist", sort=None),  
            ).properties(height=500, width=750))

        # Song summaries and plot
        song_plays, song_time = sk_wrap.get_yearly_song_summaries()
        for a, lab in zip([song_plays, song_time], ["Streams", "Time (hours)"]):
            if lab == "Streams":
                out = "number of streams"
            else:
                out = "total time (hours)"
            st.write(f"### Your top 5 tracks by {out} are...")
            st.write(alt.Chart(a).mark_bar().encode(
                x=lab,
                y=alt.Y("Track", sort=None),  
            ).properties(height=500, width=750))

        # Add a switch (checkbox)
        switch_status = st.checkbox("Do you want artist/song recommendations?")
        # Display a message based on the switch status
        if switch_status:
            print("Getting the GPT predictions for artists...")
            top_artists_str = ""
            for a in artist_plays["Artist"]:
                top_artists_str += a + ", "

            client = OpenAI()
            # defaults to getting the key using os.environ.get("OPENAI_API_KEY")
            # if you saved the key under a different environment variable name, you can do something like:
            # client = OpenAI(
            #   api_key=os.environ.get("CUSTOM_ENV_NAME"),
            # )
            recommender = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "My top artists are " + top_artists_str + "and I want to listen to more artists like them.  Recommend five more artists."},
            ]
            )
            recs = recommender.choices[0].message.content
            st.success("### Your recommendations are...\n",)
            st.success(recs)


        else:
            st.warning("Skipping recommendation step.")
        

if __name__ == "__main__":
    main()