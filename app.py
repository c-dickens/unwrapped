import os
import time
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
    "albums": alt.value('purple'), #"#7D3C98
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


    analysis_options = {
        "standard" : "Standard (Top 5 Artists, Songs, Podcasts, Artist Recommendations)",
        "detailed" : "Detailed (Top 5 Artists, Songs, Albums, Podcasts, Artist Recommendations, genres and albums)"
    }
    option = st.selectbox(
        'Which version would you like?',
        (analysis_options["standard"],
        analysis_options["detailed"])
    )
    st.write('You selected:', option)    

    # Add a switch (checkbox)
    recommendation_switch = st.checkbox("Do you want artist/song recommendations?")
    st.write("Recommendations will also be provided.  Please be patient with the query.")


    with st.form(key='my_form_to_submit'):
        submit_button = st.form_submit_button(label='Submit')

    if submit_button and uploaded_file is not None:
        # the main object that we will update with each item
        unwrapped = SpotifyUnwrapped() # sk_wrap = SketchUnwrapper()

        # stream the data
        all_dfs = []
        for file in uploaded_file:
            #json_data = json.load(file)
            df = unwrapped.json_batch_update(file)
            all_dfs.append(df)
    
        # outputs
        st.write("## Unwrapping your 2023 Spotify Data...")
        unwrapped.finalise_dataframes(all_dfs)
        year_top_artist_streams, year_top_artist_time = unwrapped.get_yearly_top_artists()
        year_top_songs_streams, year_top_songs_time = unwrapped.get_yearly_top_songs()
        year_top_podcs_streams, year_top_podcs_time = unwrapped.get_yearly_top_podcasts()
        
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

        if option == analysis_options["detailed"]:
            year_top_albums_streams, year_top_albums_cum_time = unwrapped.get_yearly_top_albums()
            # Album summaries and plot
            for a, lab in zip([year_top_albums_streams, year_top_albums_cum_time], ["Streams", "Time (hours)"]):
                if lab == "Streams":
                    out = "number of streams"
                else:
                    out = "total time (hours)"
                st.write(f"### Your top 5 albums by {out} are...")
                st.write(alt.Chart(a).mark_bar().encode(
                    x=lab,
                    y=alt.Y("Album", sort=None),
                    color=colours["albums"]  
                ).properties(height=500, width=750))

         

        # to do integrate album and podcasts into the unwrapped app.

        # # album summaries and plot
        # # album_plays  = sk_wrap.get_yearly_album_summaries()
        # # st.write(f"### Your top 5 Albums by {out} are...")
        # # st.write(alt.Chart(album_plays).mark_bar().encode(
        # #         x=lab,
        # #         y=alt.Y("Track", sort=None),  
        # # ).properties(height=500, width=750))

        if recommendation_switch:
            #load_dotenv() # need .env in same directory as main.py
            #open_ai_api_key = os.getenv("OPENAI_API_KEY")
            print("Getting the GPT predictions for artists...")
            top_artists_str = ""
            for a in year_top_artist_streams["Artist"]:
                top_artists_str += a + ", "
            print(top_artists_str)

            #client = OpenAI()
            # defaults to getting the key using os.environ.get("OPENAI_API_KEY")
            # # if you saved the key under a different environment variable name, you can do something like:
            client = OpenAI(
              api_key=os.environ.get("OPENAI_API_KEY"),
            )
            with st.spinner('Please weait. Generating recommendations...'):
                time.sleep(5)
                recommender = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "My top artists are " + top_artists_str + "and I want to listen to more artists like them.  Recommend five more artists."},
                ]
                )
            recs = recommender.choices[0].message.content
            st.success("### Your recommendations are...\n",)
            st.success(recs)


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