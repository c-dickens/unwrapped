from spotify_client import SpotifyClient
from collections import Counter

def main():
    spotify_client = SpotifyClient()
    artist_name, artist_id = spotify_client.search_for_artist_id("dave")
    print(f"\nSelected artist: {artist_name}")
    print(artist_id)
    songs = spotify_client.get_songs_by_artist(artist_id)
    spotify_client.print_songs(songs)

    # get the genres for three artists
    # test case chosen as dave, spice, beck all need manual lookup
    # dave has count incremented twice
    # arctic monkeys is a new key that has count of exactly one.
    artist_list = ["dave", "spice", "beck", "dave", "arctic monkeys"]
    artist_ctr = Counter(artist_list)
    print(artist_ctr)
    genres = spotify_client.get_genres_from_artist_list(artist_list)
    for k, v in genres.items():
        assert v["count"] == artist_ctr[k]

        
    
if __name__ == "__main__":
    main()