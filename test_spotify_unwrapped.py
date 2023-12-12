from spotify_unwrapped import SpotifyUnwrapped
import pandas as pd

def main():
    unwrapped = SpotifyUnwrapped()
    json_files = ["MySpotifyData/StreamingHistory0.json"]
    all_dfs = []
    for json_file in json_files:
        df = unwrapped.json_batch_update(json_file)
        all_dfs.append(df)
    yearly_data = pd.concat(all_dfs, axis=0)
    unwrapped.finalise_dataframes(yearly_data)

    year_top_artist_streams, year_top_artist_time = unwrapped.get_yearly_top_artists()
    year_top_songs_streams, year_top_songs_time = unwrapped.get_yearly_top_songs()
    year_top_podcs_streams, year_top_podcs_time = unwrapped.get_yearly_top_podcasts()
    year_top_albums_streams, year_top_albums_cum_time = unwrapped.get_yearly_top_albums()
    print(year_top_albums_streams)
    print(year_top_albums_cum_time)
    unwrapped.get_yearly_album_artwork(year_top_albums_streams)
    #print(year_top_podcs_streams)
    #print(year_top_podcs_time)
    #yearly_data = unwrapped.add_genres_to_df(yearly_data)
    #print(yearly_data.head(10))
    #print(yearly_data.tail(10))
    #yearly_data.to_csv("test.csv")


    #unwrapped.get_yearly_top_genres(yearly_data)

if __name__ == "__main__":
    main()