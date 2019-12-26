.. _user_guide:

User guide
==========


Description
-----------

**metalparser** is a Python API for obtaining song lyrics from diverse
lyrics websites. At the moment there is only one supported website,
which is `DarkLyrics <http://www.darklyrics.com/>`__, an online database
of lyrics for heavy metal music.


This library scrapes the corresponding website for the lyrics and
returns results according to the used API. Kindly read the
`disclaimer <https://github.com/lucone83/metal-parser/blob/master/DISCLAIMER.md>`__
to ensure that your use complies with it.

Installation
------------

*metalparser* is distributed as a Python package, freely available on
`PyPI <https://pypi.org/project/metalparser/>`__ and can easily be
installed via pip. Given that you are using ``python >= 3.5``:

::

    pip install metalparser

Alternatively, it can be manually installed by cloning this project on
your local computer:

::

    cd <project-folder>
    pip install .

Documentation
-------------

The library comes (at the moment) with 6 APIs:

* get\_songs
* get\_albums
* get\_artists
* get\_lyrics\_by\_artist
* get\_lyrics\_by\_album
* get\_lyrics\_by\_song

Some examples
~~~~~~~~~~~~~

::

    from metalparser.darklyrics import DarkLyricsApi

    api = DarkLyricsApi()

Retrieve the lyrics given a song and the corresponding artist
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    song = 'under grey skies'
    artist = 'kamelot'
    lyrics = api.get_lyrics_by_song(song=song, artist=artist)

    print(lyrics)

Get all the songs of a specific album
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    artist = 'pantera'
    album = 'vulgar display of power'
    songs_only = True
    songs_list = api.get_songs(artist, songs_only, album)

    print(songs_list)

Get all the albums of a specific artist
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    artist = 'iron maiden'
    albums_list = api.get_albums(artist=artist)

    print(albums_list)

Support
-------

Currently the following python versions are supported - 3.5 - 3.6 - 3.7

Thanks to
---------

-  res0nance and his `darklyrics
   project <https://github.com/res0nance/darklyrics>`__ for inspiration;

