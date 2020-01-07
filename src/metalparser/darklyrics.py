# coding: utf-8
import string

from metalparser.libs.darklyrics_utils import DarkLyricsHelper
from metalparser.common.exceptions import MetalParserException
from metalparser.common.logger import MetalParserLogger


class DarkLyricsApi():
    """
    A class with APIs for scraping DarkLyrics.com website.

    Parameters
    ----------
    use_cache : bool
        Boolean defining if a cached session will be created or not.

    debug_mode : bool
        Boolean defining when to save debug info on a log file.

    Attributes
    ----------
    helper : DarkLyricsHelper
        Object containing helpers for DarkLyrics.com APIs.

    Methods
    -------
    get_artists_list(self, initial_letter=None)
        Returns a list with all the artists registered on DarkLyrics.com.
        When specified, it returns a list of artists starting with an initial.

    get_albums_info(self, artist, title_only=False)
        Returns a list containing all the albums titles related to an artist.

    get_songs_info(self, artist, album=None, title_only=False)
        Returns a list containing the songs titles (and other info when specified) related to a single artist or album (when specified).

    get_album_info_and_lyrics(self, album, artist)
        Returns a list of dict containing name, title, album, track number and lyrics of all the songs related to an album on DarkLyrics.com.

    get_albums_info_and_lyrics_by_artist(self, artist)
        Returns a list of dict containing name, title, album, track number and lyrics of all the songs related to an artist on DarkLyrics.com.

    def get_song_info_and_lyrics(self, song, artist)
        Returns a str containing the lyrics of the specified song.
    """

    def __init__(self, use_cache=True, debug_mode=False):
        self.helper = DarkLyricsHelper(use_cache)
        self.logger = MetalParserLogger(debug_mode).get_logger()

    def get_artists_list(self, initial_letter=None):
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
            artist_indexes = [initial_letter.lower().replace('#', '19')]
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

    def get_albums_info(self, artist, title_only=False):
        """
        Returns a list containing all the albums titles related to an artist.

        Arguments:
            artist {str} -- The artist's name

        Returns:
            [list] -- A list of str containing all the albums titles related to an artist
        """

        artist_page = self.helper.get_artist_page(artist)
        albums_list = self.helper.get_albums_info_from_artist_page(artist_page, title_only=title_only)

        return albums_list

    def get_songs_info(self, artist, album=None, title_only=False):
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
            elif title_only:
                songs_list.append(link.text)
            else:
                link_href = link.attrs['href'].replace('../', self.helper.get_base_url())
                album_info = self.helper.get_albums_info_from_url(link_href.split('#')[0])
                songs_list.append({
                    "title": link.text,
                    "song_link": link_href,
                    "album": album_info["title"],
                    "album_track": link_href.split('#')[1],
                    "release_year": album_info["release_year"]
                })

        return songs_list

    def get_album_info_and_lyrics(self, album, artist, lyrics_only=False):
        """
        Returns a list of dict containing info and lyrics of all the songs related to an album on DarkLyrics.com.

        Arguments:
            album {str} -- The title of the album
            artist {str} -- The artist's name

        Returns:
            [list] -- A list of dict containing info and lyrics about of all the songs related to the specified album or
                      a list of str containing only the lyrics of the specified album, depending on the lyrics_only flag.
        """

        lyrics_list = []
        songs_links = self.helper.get_songs_links_from_artist(artist, album=album)
        album_url = self.helper.get_lyrics_url_by_tag(songs_links[0])
        album_info = self.helper.get_albums_info_from_url(album_url)

        for song_link in songs_links:
            self.logger.debug('\t\tProcessing song "{}" ...'.format(song_link.text))
            # Don't break the entire job because of a single song
            try:
                url = self.helper.get_lyrics_url_by_tag(song_link)
                if lyrics_only is True:
                    lyrics_list.append(self.helper.get_lyrics_by_url(url))
                else:
                    lyrics_list.append({
                        "artist": artist.title(),
                        "album": album_info['title'],
                        "album_type": album_info["type"],
                        "release_year": album_info['release_year'],
                        "title": song_link.text,
                        "track_no": int(url.split('#')[1]),
                        "lyrics": self.helper.get_lyrics_by_url(url)
                    })
            except (MetalParserException, Exception) as e:
                self.logger.error('Error while processing the song "{}": {}'.format(song_link.text, str(e)))
                continue

        return lyrics_list

    def get_albums_info_and_lyrics_by_artist(self, artist):
        """
        Returns a list of dict containing name, title, album, track number and lyrics of all the songs related to an artist on DarkLyrics.com.

        Arguments:
            artist {str} -- The artist's name

        Returns:
            [list] -- A list of dict containing info and lyrics of all the songs related to the specified artist.
        """

        self.logger.debug('Processing artist "{}" ...'.format(artist.title()))
        albums = self.get_albums_info(artist, title_only=True)
        albums_info_lyrics = []

        for album in albums:
            self.logger.debug('\tProcessing album "{}" ...'.format(album))
            # Don't break the entire job because of a single album
            try:
                album_info_lyrics = self.get_album_info_and_lyrics(album, artist)
                albums_info_lyrics += album_info_lyrics
            except Exception as e:
                self.logger.error('Error while processing the album "{}" by "{}": {}'.format(album, artist, str(e)))
                continue

        return albums_info_lyrics

    def get_song_info_and_lyrics(self, song, artist, lyrics_only=False):
        """
        Returns a str containing the lyrics of the specified song.

        Arguments:
            song {str} -- The title of the song
            artist {str} -- The artist's name

        Returns:
            [dict or str] -- A dict containing info and lyrics about a song of a certain artist or
                             a str containing only the lyrics of the specified song, depending on the lyrics_only flag.
        """

        lyrics_url = self.helper.get_lyrics_url_by_song(song, artist)
        album_info = self.helper.get_albums_info_from_url(lyrics_url)  # a lyrics url is in fact an album url with a bookmark

        if lyrics_only is True:
            return self.helper.get_lyrics_by_url(lyrics_url)
        else:
            return {
                "artist": artist.title(),
                "album": album_info['title'],
                "release_year": album_info['release_year'],
                "title": song,
                "track_no": int(lyrics_url.split('#')[1]),
                "lyrics": self.helper.get_lyrics_by_url(lyrics_url)
            }
