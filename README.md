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
git clone https://github.com/lucone83/metal-parser.git
cd metal-parser
pip install .
```


## Documentation

The library comes (at the moment) with 6 APIs:

- get_artists_list()
- get_albums_info()
- get_songs_info()
- get_album_info_and_lyrics()
- get_albums_info_and_lyrics_by_artist()
- get_song_info_and_lyrics()

More complete docs regarding this project can be found on [readthedocs](https://metalparser.readthedocs.io/).

### Some examples

I recommend not to change the default settings regarding requests rate per minute and the wait time (3 secs) after each request.
DarkLyrics does not have a robots.txt, so they don't really like scraping. Be gentle! :)

```
from metalparser.darklyrics import DarkLyricsApi

api = DarkLyricsApi()
```

#### Retrieve the lyrics given a song and the corresponding artist:

```
song = 'under grey skies'
artist = 'kamelot'
lyrics = api.get_song_info_and_lyrics(song=song, artist=artist, lyrics_only=True)

print(lyrics)

```

#### Get all the songs of a specific album:

```
artist = 'pantera'
album = 'vulgar display of power'
songs_list = api.get_songs_info(artist, album=album, title_only=True)

print(songs_list)
```

#### Get all the albums of a specific artist:

```
artist = 'iron maiden'
albums_list = api.get_albums_info(artist=artist, title_only=True)

print(albums_list)
```


## Support

Currently the following python versions are supported:

- 3.4.*
- 3.5.*
- 3.6.*
- 3.7.*
- 3.8.*


## Thanks to

- res0nance and his [darklyrics project](https://github.com/res0nance/darklyrics) for inspiration;


