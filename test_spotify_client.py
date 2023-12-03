from spotify_client import SpotifyClient

def main():
    spotify_client = SpotifyClient()
    _, artist_id = spotify_client.search_for_artist_id("SZA")
    songs = spotify_client.get_songs_by_artist(artist_id)
    #spotify_client.print_songs(songs)

    # get the genres for three artists
    artist_list = ["SZA", "Arctic Monkeys", "Haim"]
    first_genres = spotify_client.get_genre_from_artist(artist_id)
    #print(first_genres)
    genres = spotify_client.get_genres_from_artist_list(artist_list)
    print(genres)

        
    
if __name__ == "__main__":
    main()