# metalparser

**metalparser** is a Python API for obtaining song lyrics from diverse lyrics websites.
At the moment there is only one supported website, which is [DarkLyrics](http://www.darklyrics.com/), an online database of lyrics for heavy metal music.


## Description

This library scrapes the corresponding website for the lyrics and returns results according to the used API.
**Kindly read the [disclaimer](https://github.com/lucone83/metal-parser/blob/master/DISCLAIMER.md) to ensure that your use complies with it**.


## Installation

_metalparser_ is distributed as a Python package, freely available on [PyPI](https://pypi.org/project/metalparser/) and can easily be installed via pip.
Given that you are using ```python >= 3.5```:

```
pip install metalparser
```

Alternatively, it can be manually installed by cloning this project on your local computer:

```
cd <project-folder>
pip install .
```


## Documentation

The library comes (at the moment) with 6 APIs:
- get_songs
- get_albums
- get_artists
- get_lyrics_by_artist
- get_lyrics_by_album
- get_lyrics_by_song

More complete docs regarding this project can be found on [readthedocs](https://metalparser.readthedocs.io/).

### Some examples

```
from metalparser.darklyrics import DarkLyricsApi

api = DarkLyricsApi()
```

#### Retrieve the lyrics given a song and the corresponding artist:

```
song = 'under grey skies'
artist = 'kamelot'
lyrics = api.get_lyrics_by_song(song=song, artist=artist)

print(lyrics)

```

#### Get all the songs of a specific album:

```
artist = 'pantera'
album = 'vulgar display of power'
songs_only = True
songs_list = api.get_songs(artist, songs_only, album)

print(songs_list)
```

#### Get all the albums of a specific artist:

```
artist = 'iron maiden'
albums_list = api.get_albums(artist=artist)

print(albums_list)
```


## Support

Currently the following python versions are supported
- 3.6
- 3.7


## Thanks to

- res0nance and his [darklyrics project](https://github.com/res0nance/darklyrics) for inspiration;


