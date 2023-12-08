import altair as alt
import streamlit as st
import json
import pandas as pd 
import numpy as np
from spotify_unwrapped import SpotifyUnwrapped
from openai import OpenAI

colours = {
    "artist": alt.value('red'),
    "tracks": alt.value('steelblue'),
    "podcasts": alt.value('chartreuse')
}#, '#F4D03F', '#D35400', '#7D3C98']
# pd.DataFrame({
#     'x': range(6),
#     'color': ['red', 'steelblue', 'chartreuse', '#F4D03F', '#D35400', '#7D3C98']
# })

def main():
    
    st.title("Unwrapping Spotify's Unwrapped")
    st.write("Select your data and click submit.")
    # upload all of the json files
    uploaded_file = st.file_uploader("Choose a JSON file", accept_multiple_files=True, type=["json"])

    with st.form(key='my_form_to_submit'):
        submit_button = st.form_submit_button(label='Submit')

    if submit_button and uploaded_file is not None:
        # the main object that we will update with each item
        #sk_wrap = SketchUnwrapper()
        unwrapped = SpotifyUnwrapped()

        # stream the data
        all_dfs = []
        for file in uploaded_file:
            #json_data = json.load(file)
            df = unwrapped.json_batch_update(file)
            all_dfs.append(df)
            # Step 2: Convert JSON data to a DataFrame
            #df = pd.json_normalize(json_data)
            # df = pd.read_csv(uploaded_file, header=0, names=dtypes.keys(),
            #             dtype=dtypes, parse_dates=parse_dates)
            # df['endTime'] = pd.to_datetime(df['endTime'], format='%Y-%m-%d %H:%M')
            # df["minsPlayed"] = df["msPlayed"]/(60*1000) 
            # df = df[df["endTime"].dt.strftime("%Y") == "2023"]
            # df = df[df["endTime"].dt.strftime("%m") < "11"]
            # df = df[df["minsPlayed"] > 0.5]
            # sk_wrap.minibatch_update(df)
        # if streaming_complete:
        #     yearly_data = pd.concat(all_dfs, axis=0)
        
    
        # outputs
        st.write("## Unwrapping your 2023 Spotify Data...")
        unwrapped.finalise_dataframes(all_dfs)
        year_top_artist_streams, year_top_artist_time = unwrapped.get_yearly_top_artists()
        year_top_songs_streams, year_top_songs_time = unwrapped.get_yearly_top_songs()
        year_top_podcs_streams, year_top_podcs_time = unwrapped.get_yearly_top_podcasts()

        # Sketch approaches 
        # sk_wrap.update_yearly_sketches() # merge the month summaries into the year summary
        # artist_plays, artist_time = sk_wrap.get_yearly_artist_summaries()
        # song_plays, song_time = sk_wrap.get_yearly_song_summaries()
        # podcast_plays, podcast_time = sk_wrap.get_yearly_podcast_summaries()
        
        # artist plots
        for a, lab in zip([year_top_artist_streams, year_top_artist_time], ["Streams", "Time (hours)"]):
            if lab == "Streams":
                out = "number of streams"
            else:
                out = "total time (hours)"
            st.write(f"### Your top 5 artists by {out} are...")
            st.write(alt.Chart(a).mark_bar().encode(
                x=lab,
                y=alt.Y("Artist", sort=None), 
                color=colours["artist"]
            ).properties(height=500, width=750))

        # Song summaries and plot
        for a, lab in zip([year_top_songs_streams, year_top_songs_time], ["Streams", "Time (hours)"]):
            if lab == "Streams":
                out = "number of streams"
            else:
                out = "total time (hours)"
            st.write(f"### Your top 5 tracks by {out} are...")
            st.write(alt.Chart(a).mark_bar().encode(
                x=lab,
                y=alt.Y("Track", sort=None),
                color=colours["tracks"]  
            ).properties(height=500, width=750))

        # Podcast summaries and plot
        for a, lab in zip([year_top_podcs_streams, year_top_podcs_time], ["Streams", "Time (hours)"]):
            if lab == "Streams":
                out = "number of streams"
            else:
                out = "total time (hours)"
            st.write(f"### Your top 5 podcasts by {out} are...")
            st.write(alt.Chart(a).mark_bar().encode(
                x=lab,
                y=alt.Y("Podcast", sort=None),
                color=colours["podcasts"]  
            ).properties(height=500, width=750))

        # to do integrate album and podcasts into the unwrapped app.

        # # album summaries and plot
        # # album_plays  = sk_wrap.get_yearly_album_summaries()
        # # st.write(f"### Your top 5 Albums by {out} are...")
        # # st.write(alt.Chart(album_plays).mark_bar().encode(
        # #         x=lab,
        # #         y=alt.Y("Track", sort=None),  
        # # ).properties(height=500, width=750))

        # # Add a switch (checkbox)
        # switch_status = st.checkbox("Do you want artist/song recommendations?")
        # # Display a message based on the switch status
        # if switch_status:
        #     print("Getting the GPT predictions for artists...")
        #     top_artists_str = ""
        #     for a in artist_plays["Artist"]:
        #         top_artists_str += a + ", "

        #     client = OpenAI()
        #     # defaults to getting the key using os.environ.get("OPENAI_API_KEY")
        #     # if you saved the key under a different environment variable name, you can do something like:
        #     # client = OpenAI(
        #     #   api_key=os.environ.get("CUSTOM_ENV_NAME"),
        #     # )
        #     recommender = client.chat.completions.create(
        #     model="gpt-3.5-turbo",
        #     messages=[
        #         {"role": "system", "content": "My top artists are " + top_artists_str + "and I want to listen to more artists like them.  Recommend five more artists."},
        #     ]
        #     )
        #     recs = recommender.choices[0].message.content
        #     st.success("### Your recommendations are...\n",)
        #     st.success(recs)


        # else:
        #     st.warning("Skipping recommendation step.")
        

if __name__ == "__main__":
    main()


    # def make_yearly_top_songs(self, df:pd.DataFrame) -> None:
    #     for _, row in df.iterrows():
    #         if row["minsPlayed"] > 0.5:
    #             self.monthly_songs_num_plays[row["endTime"].month].update(item=row["trackName"], weight=1)
    #             self.monthly_songs_cum_time[row["endTime"].month].update(item=row["trackName"], weight=np.ceil(row["minsPlayed"]).astype(int))
    #     for month, month_sk in self.monthly_songs_num_plays.items():
    #         self.yearly_songs_num_plays.merge(month_sk)
    #         self.yearly_songs_cum_time.merge(self.monthly_songs_cum_time[month])   