from spotify_client import SpotifyClient

def main():
    spotify_client = SpotifyClient()
    artist_name, artist_id = spotify_client.search_for_artist_id("ACDC")
    songs = spotify_client.get_songs_by_artist(artist_id)
    spotify_client.print_songs(songs)

if __name__ == "__main__":
    main()