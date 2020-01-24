import re
import string

from bs4 import BeautifulSoup
from metalparser.common.scraping import ScrapingAgent
from metalparser.common.exceptions import ArtistNotFoundException, LyricsNotFoundException, SongsNotFoundException


class DarkLyricsHelper:
    """
    A class with helpers for DarkLyricsApi

    Attributes
    ----------
    BASE_URL : str
        DarkLyrics.com base URL

    scraping_agent : ScrapingAgent
        The agent taking hand of HTTP requests

    Methods
    -------
    get_base_url(self)
        Returns DarkLyrics.com base URL.

    get_artist_page(self, artist)
        Returns a DarkLyrics.com page related to an artist in form of a BeautifulSoup object.

    get_songs_links_from_artist(self, artist, album=None)
        Returns a links list containing all the lyrics URLs related to an artist or an album.

    get_albums_info_from_artist_page(self, artist_page, all_info=False):
        Given the artist page, returns infos about the albums.

    get_albums_info_from_url(self, url):
        Returns album info given the album's URL.

    get_lyrics_url_by_song(self, song, artist)
        Given a song title and the artist, returns the link related to the lyrics.

    get_lyrics_url_by_tag(self, link_tag)
        Given an <a> HTML tag related to a song's lyrics, returns the related URL.

    get_lyrics_by_url(self, url)
        Given an URL related to a song, returns the lyrics.
    """

    def __init__(self, use_cache):
        self.BASE_URL = 'http://www.darklyrics.com/'
        self.scraping_agent = ScrapingAgent(use_cache=use_cache)

    def get_base_url(self):
        """
        Returns DarkLyrics.com base URL.

        Returns:
            [str] -- DarkLyrics.com base URL
        """

        return self.BASE_URL

    def get_artist_page(self, artist):
        """
        Returns a DarkLyrics.com page related to an artist in form of a BeautifulSoup object.

        Arguments:
            artist {str} -- The artist's name

        Raises:
            ArtistNotFoundException: Exception raised when the URL is not found on DarkLyrics.com

        Returns:
            [BeautifulSoup] -- Page related to an artist in form of a BeautifulSoup object
        """

        url = self.__get_artist_url(artist)
        artist_page = self.scraping_agent.get_page_from_url(url)

        if 'not Found' in artist_page.title.string:
            raise ArtistNotFoundException(
                'Artist page for "{}" not found at URL: {}. Is it on darklyrics.com?'.format(artist.title(), url)
            )
        else:
            return artist_page

    def get_songs_links_from_artist(self, artist, album=None):
        """
        Returns a links list containing all the lyrics URLs related to an artist or an album.

        Arguments:
            artist {str} -- The artist's name

        Keyword Arguments:
            album {str} -- The title of the album (optional) (default: {None})

        Raises:
            SongsNotFoundException: Exception raised when no songs related to an artist or album are found

        Returns:
            [list] -- List of strings containing all the lyrics URLs related to an artist or an album
        """

        links = None
        artist_page = self.get_artist_page(artist)

        if album is not None:
            album_string = album.lower().replace('&', '&amp;')
            album_list = artist_page.find_all("div", class_="album")
            for album_tag in album_list:
                stew_str = str(album_tag.strong).lower()
                if stew_str.find('"' + album_string + '"') != -1:
                    album_section = BeautifulSoup(str(album_tag), 'html.parser')
                    links = album_section.find_all('a')
        else:
            links = artist_page.find_all('a')

        if links is None:
            raise SongsNotFoundException('Songs not found for the artist "{}" and the album "{}".'.format(artist.title(), album.title()))

        return links

    def get_albums_info_from_artist_page(self, artist_page, title_only=False):
        """
        Given the artist page, retrieve infos about the albums.

        Arguments:
            artist_page {BeautifulSoup} -- The artist page in BeautifulSoup format.

        Keyword Arguments:
            all_info {bool} -- Flag to determinate if returning all albums info or title only (default: {False})

        Returns:
            [list] -- List of albums (str list or dict list, depending on all_info)
        """

        album_headlines = artist_page.find_all('h2')
        albums_list = []

        for line in album_headlines:
            album_line_parts = line.text.split('"')
            is_valid_album_type = any(elem in album_line_parts[0].lower() for elem in ['album', 'ep', 'demo'])
            if(len(album_line_parts) > 1 and is_valid_album_type):
                if title_only is False:
                    albums_list.append({
                        'title': album_line_parts[1],
                        'type': album_line_parts[0].replace(':', '').strip(),
                        'release_year': line.text.split('"')[2].replace(')', '').replace('(', '').strip()
                    })
                else:
                    albums_list.append(line.text.split('"')[1])

        return albums_list

    def get_albums_info_from_url(self, url):
        """
        Returns album info given the album's URL.

        Arguments:
            url {str} -- The album's URL

        Returns:
            [dict] -- A dict with the following album info: title, release year and type (album, EP).
        """

        if '../lyrics' in url:
            url = url.replace('../', self.BASE_URL)

        album_page = self.scraping_agent.get_page_from_url(url)
        album_info_text = album_page.select_one('div.albumlyrics > h2').text

        if 'non-album' in album_info_text:
            return {
                'title': '',
                'release_year': '',
                'type': 'non-album songs'
            }
        else:
            return {
                'title': album_info_text.split('"')[1],
                'release_year': album_info_text.split('"')[2].replace(')', '').replace('(', '').strip(),
                'type': album_info_text.split('"')[0].replace(':', '').strip()
            }

    def get_lyrics_url_by_song(self, song, artist):
        """
        Given a song title and the artist, returns the link related to the lyrics.

        Arguments:
            song {str} -- The title of the song
            artist {str} -- The artist's name

        Raises:
            LyricsNotFoundException: Exception raised when no link is found

        Returns:
            [str] -- The link related to the lyrics of the specified song
        """

        url = self.__get_search_url(song, artist)
        search_page = self.scraping_agent.get_page_from_url(url)
        sens = search_page.find_all('div', class_='sen')

        for sen in sens:
            a = sen.find('a')
            if a:
                link = self.BASE_URL + a.get('href')
                if link.find('#') != -1:
                    return link

        raise LyricsNotFoundException('Lyrics for "{}" not found at URL: {}'.format(song, url))

    def get_lyrics_url_by_tag(self, link_tag):
        """
        Given an <a> HTML tag related to a song's lyrics, returns the related URL.

        Arguments:
            link_tag {BeautifulSoup} -- <a> tag which is supposed to contain an URL related to lyrics

        Raises:
            LyricsNotFoundException: Exception raised when no link or invalid link is found

        Returns:
            [str] -- URL string contained in the specified <a> tag, leading to lyrics.
        """

        if '/lyrics' in link_tag.attrs['href']:
            url = link_tag.attrs['href']

            return url
        else:
            raise LyricsNotFoundException('Lyrics URL for the song "{}" not found.'.format(link_tag.text))

    def get_lyrics_by_url(self, url):
        """
        Given an URL related to a song, returns the lyrics.

        Arguments:
            url {str} -- URL leading to the lyrics of a certain song

        Raises:
            LyricsNotFoundException: Exception raised when no lyrics div is found

        Returns:
            [str] -- A string with the lyrics related to the specified URL
        """

        if '../lyrics' in url:
            url = url.replace('../', self.BASE_URL)

        song_number = int(url.split('#')[1])
        url = url.split('#')[0]
        lyrics_page = self.scraping_agent.get_page_from_url(url)
        lyrics_div = lyrics_page.find('div', class_='lyrics')

        if lyrics_div is None:
            raise LyricsNotFoundException('No lyrics found at URL: {}. Check if URL exists or try to clean the cache.'.format(url))

        song_lyrics = lyrics_div.prettify().split('</h3>')[song_number]

        return self.__sanitize_lyrics(song_lyrics)

    def __sanitize_lyrics(self, lyrics):
        """Clean the lyrics string."""

        # remove tail
        sanitized_lyrics = lyrics[:lyrics.find('<h3>')]
        # Set linebreaks
        sanitized_lyrics = sanitized_lyrics.replace('<br/>', '')
        # Remove italic
        sanitized_lyrics = sanitized_lyrics.replace('</i>', '').replace('<i>', '')
        # Remove trailing divs
        sanitized_lyrics = sanitized_lyrics.split('<div')[0]
        # Remove duplicate blank lines
        split_lyrics = sanitized_lyrics.splitlines()
        sanitized_lyrics = ''
        for line_number in range(len(split_lyrics) - 1):
            line = split_lyrics[line_number].rstrip()
            next_line = split_lyrics[line_number + 1].rstrip()
            last_line = split_lyrics[max(line_number - 1, 0)].rstrip()

            if line != '' or (line == '' and next_line == '' and last_line != ''):
                sanitized_lyrics = sanitized_lyrics + '\n' + line
        # Remove starting/ending newlines
        sanitized_lyrics = sanitized_lyrics[1:-1]
        # Remove space after newline
        sanitized_lyrics = sanitized_lyrics.replace('\n ', '\n')
        # Remove leading and trailing spaces
        sanitized_lyrics = sanitized_lyrics.strip()

        return sanitized_lyrics

    def __get_search_url(self, song, artist):
        """Build an URL with a query usable by DarkLyrics.com internal search engine."""

        query = self.__sanitize_search_query(artist + ' ' + song)
        url = self.BASE_URL + 'search?q=' + query

        return url

    def __get_artist_url(self, artist):
        """Build an URL leading to the page of the specified artist."""

        artist = self.__sanitize_artist_url(artist)
        if artist[0].isdigit():
            index = '19'
        else:
            index = artist[0]

        return self.BASE_URL + index + '/' + artist + '.html'

    def __sanitize_artist_url(self, artist):
        """Clean a string and make it compatible to a DarkLyrics.com artist URL"""

        # Lowercase
        artist = artist.lower()
        # Special cases
        artist = artist.replace('+\\-', '2').replace('vhäldemar', 'vhaldemar').replace('øscillatör', 'scillatr').replace('zamieć', 'zamiec')
        # Replace nordic chars with another letter
        artist = artist.replace('ø', 'o').replace('ö', 'o').replace('ü', 'u').replace('å', 'a').replace(u'æ', u'e')
        # Remove punctuation signs
        artist = re.sub(r'[' + re.escape(string.punctuation) + ']', '', artist)
        # Remove other special chars
        artist = re.sub(r'[äæøáéíóúýćïëöüêčďěňřšťžėūãõ]', '', artist)
        # Remove whitespaces
        artist = re.sub(r'[' + re.escape(string.whitespace) + ']', '', artist)

        return artist

    def __sanitize_search_query(self, query):
        """Clean a string and make it compatible to a DarkLyrics.com search engine query"""

        # Lowercase
        query = query.lower()
        # Special cases
        query.replace('+\\-', '2').replace('vhäldemar', 'vhaldemar').replace('øscillatör', 'scillatr').replace('zamieć', 'zamiec')
        # Replace nordic chars with another letter
        query.replace('ø', 'o').replace('ö', 'o').replace('ü', 'u').replace('å', 'a').replace(u'æ', u'e')
        # Remove punctuation signs
        query = re.sub(r'[' + re.escape(string.punctuation) + ']', '', query)
        # Remove other special chars
        query = re.sub(r'[äæøáéíóúýćïëöüêčďěňřšťžėūãõ]', '', query)
        # Replace whitespaces with '+'
        query = re.sub(r'[' + re.escape(string.whitespace) + ']', '+', query)

        return query
