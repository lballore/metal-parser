# coding: utf-8
import string

from metalparser.libs.darklyrics_utils import DarkLyricsHelper
from metalparser.common.exceptions import MetalParserException


class DarkLyricsApi():
    """
    A class with APIs for scraping DarkLyrics.com website.

    Attributes
    ----------
    helper : DarkLyricsHelper
        Object containing helpers for DarkLyrics.com APIs

    Methods
    -------
    get_songs(self, artist, songs_only=True, album=None)
        Returns a list containing the songs titles (and other info when specified) related to a single artist or album (when specified).

    get_albums(self, artist)
        Returns a list containing all the albums titles related to an artist.

    get_artists(self, initial_letter=None)
        Returns a list with all the artists registered on DarkLyrics.com.
        When specified, it returns a list of artists starting with an initial.

    get_lyrics_by_artist(self, artist)
        Returns a list of dict containing name, title, album, track number and lyrics of all the songs related to an artist on DarkLyrics.com.

    get_lyrics_by_album(self, album, artist)
        Returns a list of dict containing name, title, album, track number and lyrics of all the songs related to an album on DarkLyrics.com.

    def get_lyrics_by_song(self, song, artist)
        Returns a str containing the lyrics of the specified song.
    """

    def __init__(self, use_cache=True):
        self.helper = DarkLyricsHelper(use_cache)

    def get_songs(self, artist, songs_only=True, album=None):
        """
        Returns a list containing the songs titles related to a single artist or album (when specified).

        Arguments:
            artist {str} -- The artist's name

        Keyword Arguments:
            songs_only {bool} --
            album {str} -- The album name (optional) (default: {None})

        Returns:
            [list] -- A list of str containing the songs titles related to a single artist or album (when specified)
        """

        links = self.helper.get_songs_links_from_artist(artist, album)
        songs_list = []

        for link in links:
            if '/lyrics' not in link.attrs['href']:
                continue
            if songs_only:
                songs_list.append(link.text)
            else:
                link_href = link.attrs['href'].replace('../', self.helper.get_base_url())
                songs_list.append({
                    "title": link.text,
                    "song_link": link_href,
                    "album_link": link_href.split('#')[0],
                    "album_track": link_href.split('#')[1]
                })

        return songs_list

    def get_albums(self, artist):
        """
        Returns a list containing all the albums titles related to an artist.

        Arguments:
            artist {str} -- The artist's name

        Returns:
            [list] -- A list of str containing all the albums titles related to an artist
        """

        artist_page = self.helper.get_artist_page(artist)
        album_headlines = artist_page.find_all('h2')
        albums_list = []
        for line in album_headlines:
            if(len(line.text.split('"')) > 1 and any(elem in line.text.lower() for elem in ['album', 'ep'])):
                albums_list.append(line.text.split('"')[1])

        return albums_list

    def get_artists(self, initial_letter=None):
        """
        Returns a list with all the artists registered on DarkLyrics.com.
        When specified, it returns a list of artists starting with an initial.

        Keyword Arguments:
            initial_letter {str} -- The initial letter of The artist's name (optional) (default: {None})

        Raises:
            ValueError: Exception raised when the argument initial_letter is longer than 1 (when specified)

        Returns:
            [list] -- An alphabetically ordered list of str containing all the artists found according to the arguments
        """

        artists = []
        if initial_letter:
            if len(initial_letter) > 1:
                raise ValueError("Initial letter must be a string with length = 1")
            artist_indexes = [initial_letter.lower()]
        else:
            artist_indexes = list(string.ascii_lowercase) + ['19']

        for index in artist_indexes:
            url = self.helper.get_base_url() + index + '.html'
            index_page = self.helper.scraping_agent.get_page_from_url(url)
            artists_tags = index_page.select('div.artists > a')
            for tag in artists_tags:
                artist = tag.text.title()
                artists.append(artist)

        return sorted(artists)

    def get_lyrics_by_artist(self, artist):
        """
        Returns a list of dict containing name, title, album, track number and lyrics of all the songs related to an artist on DarkLyrics.com.

        Arguments:
            artist {str} -- The artist's name

        Returns:
            [list] -- A list of dict containing name, title, album, track number and lyrics of all the songs related to the specified artist
        """

        albums = self.get_albums(artist)
        lyrics_list = []

        for album in albums:
            album_lyrics = self.get_lyrics_by_album(album, artist)
            for lyrics in album_lyrics:
                lyrics_list.append(lyrics)

        return lyrics_list

    def get_lyrics_by_album(self, album, artist):
        """
        Returns a list of dict containing name, title, album, track number and lyrics of all the songs related to an album on DarkLyrics.com.

        Arguments:
            album {str} -- The title of the album
            artist {str} -- The artist's name

        Returns:
            [list] -- A list of dict containing name, title, album, track number and lyrics of all the songs related to the specified album
        """

        lyrics_list = []
        songs_links = self.helper.get_songs_links_from_artist(artist, album)

        try:
            for song_link in songs_links:
                url = self.helper.get_lyrics_url_by_tag(song_link)
                index = int(url.split('#')[1])
                lyrics_list.append({
                    "album": album.title(),
                    "title": song_link.text,
                    "track_no": index,
                    "lyrics": self.helper.get_lyrics_by_url(url)
                })
        except MetalParserException as e:
            print(str(e))

        return lyrics_list

    def get_lyrics_by_song(self, song, artist):
        """
        Returns a str containing the lyrics of the specified song.

        Arguments:
            song {str} -- The title of the song
            artist {str} -- The artist's name

        Returns:
            [str] --  A str containing the lyrics of the specified song.
        """

        lyrics_url = self.helper.get_lyrics_url_by_song(song, artist)
        song_lyrics = self.helper.get_lyrics_by_url(lyrics_url)

        return song_lyrics
