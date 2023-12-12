from spotify_client import SpotifyClient
from collections import Counter
import numpy as np

def test_album_lookup_from_song():
    """
    for every (song, artist) pair in the dataset, lookup the album name
    by using the song id and the artist id.

    eg.
    (dave, streatham)                         -> PSYCHODRAMA
    (taylor swift, i forgot that you existed) -> Lover
    ("now i'm in it", "haim")                 -> Women In Music Pt. III
    (foals, the runner)                       -> Everything Not Saved Will Be Lost Part II
    """
    
    queries = [
               ("dave", "streatham"), 
               ("taylor swift", "i forgot that you existed"), 
               ("haim", "now i'm in it"), 
               ("foals", "the runner"),
               ("Tierra Whack", "hookers"),
               ("yard act", "rich"),
               ]
    answers = ["psychodrama", "lover", "women in music pt. iii", 
               "everything not saved will be lost part ii",
               "whack world", "the overload"]
    for q, a in zip(queries, answers):
        album = spotify_client.get_album_from_song(q[1], q[0])
        if album is not None:
            assert album.lower() == a.lower()

    queries = queries + [("foals", "the runner"),
                        ("dave", "location"),
                        ("dave", "purple heart"),]
    answers = answers + ["everything not saved will be lost part ii", "psychodrama", "psychodrama"]
    spotify_client = SpotifyClient()
    album_list = spotify_client.get_album_from_song_list(queries, sample_rate=1.)
    for resp, ans in zip(album_list, answers):
        assert resp.lower() == ans.lower()
    print(album_list)

def test_album_artwork():
    """
    for every artist in the dataframe, get the album artwork for the top album.
    Do this by getting the artist id and making a small number of calls to the API.
    """
    queries = [
               ("dave", "streatham"), 
               ("taylor swift", "i forgot that you existed"), 
               ("haim", "now i'm in it"), 
               ("foals", "the runner"),
               ("yard act", "rich"),
    ]
    answers = ["psychodrama", "lover", "women in music pt. iii", 
               "everything not saved will be lost part ii",
              "the overload"]
    spotify_client = SpotifyClient()
    album_list = spotify_client.get_album_from_song_list(queries, sample_rate=1.)
    for resp, ans in zip(album_list, answers):
        assert resp.lower() == ans.lower()
    artist_album_list = [(q[0], a) for q, a in zip(queries, album_list)]
    spotify_client.get_album_artwork(artist_album_list)

def test_genre_lookup_from_song():
    """
    get the genres for three artists
    test case chosen as dave, spice, beck all need manual lookup
    dave has count incremented twice
    arctic monkeys is a new key that has count of exactly one.
    """
    artist_list = ["dave", "spice", "beck", "dave", "arctic monkeys"]
    artist_ctr = Counter(artist_list)
    spotify_client = SpotifyClient()
    genres = spotify_client.get_genres_from_artist_list(artist_list)
    for k, v in genres.items():
        assert v["count"] == artist_ctr[k]

def main():
    #test_album_lookup_from_song()
    #test_genre_lookup_from_song()
    test_album_artwork()
    
if __name__ == "__main__":
    main()