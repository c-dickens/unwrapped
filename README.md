# UnWrapped

This repository provides a simple application to approximately recover your year's [Wrapped](https://www.spotify.com/us/wrapped/).

## Structure
- `spotify_client.py` handles the spotify lookups 
- `spotify_unwrapped.py` analyses the spotify data


## To do.
- Integrate the spotify api lookup into the app.
- separate out the analysis into a different class and add exact and estimation mode.
- `spotify_stream_analyser.py` - analyses the spotify data in a streaming fashion

## Problems:
Input artist `Dave` is an incorrect lookup.  
This is a problem for other artists such as `Spice ` and `Beck`.
Instead, we will look up an artist by `trackName`.`

## Dependencies
- Spotify yearly streaming data
- Install the requirements and run `streamlit run app.py`