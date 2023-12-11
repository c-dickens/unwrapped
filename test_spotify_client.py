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
    album_list = spotify_client.get_album_from_song_list(queries)
    for resp, ans in zip(album_list, answers):
        assert resp.lower() == ans.lower()
    print(album_list)

def test_album_lookups_sample():
    np.random.seed(1235123462)
    queries = [
               ("dave", "streatham"), 
               ("taylor swift", "i forgot that you existed"), 
               ("haim", "now i'm in it"), 
               ("foals", "the runner"),
               ("Tierra Whack", "hookers"),
               ("yard act", "rich"),
               ]
    queries = queries + [("foals", "the runner"),
                        ("dave", "location"),
                        ("dave", "purple heart"),]
    answers = ["psychodrama", "lover", "women in music pt. iii", 
               "everything not saved will be lost part ii",
               "whack world", "the overload"]
    answers = answers + ["everything not saved will be lost part ii", "psychodrama", "psychodrama"]
    #n = len(queries)
    #sample_rate = 0.5
    €sample_size = np.ceil(sample_rate*n).astype(int)
    sampled_ids = np.random.choice(n, sample_size, replace=False)
    print(sampled_ids)
    albums = [None for _ in range(n)]
    sampled_data = [queries[i] for i in sampled_ids]
    sampled_answers = [answers[i] for i in sampled_ids]
    spotify_client = SpotifyClient()
    album_list = spotify_client.get_album_from_song_list(sampled_data)
    for ii, (resp, ans) in enumerate(zip(album_list, sampled_answers)):
        assert resp.lower() == ans.lower()
        albums[sampled_ids[ii]] = resp
    album_counter = Counter(albums)
    album_counter_scaled = {k : v / sample_rate  for k, v in album_counter.items() if k != None}
    print(albums)
    print(album_counter)
    print(album_counter_scaled)
    
    

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
    test_album_lookups_sample()
    
if __name__ == "__main__":
    main()