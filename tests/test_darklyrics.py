import os
import pytest

from metalparser.darklyrics import DarkLyricsApi
from metalparser.common.exceptions import ArtistNotFoundException, LyricsNotFoundException, SongsNotFoundException


# -------------------------- API OBJECT ------------------------------ #


SKIP_ON_TRAVIS = "Skipping this test on Travis CI. Could fail in case of ban by DarkLyrics.com."


def test__with_cached_session():
    api = DarkLyricsApi()

    assert api.helper.scraping_agent.get_cached_session() is not None


def test__without_cached_session():
    api = DarkLyricsApi(use_cache=False)

    assert api.helper.scraping_agent.get_cached_session() is None


def test_cached_request_with_cached_session():
    api = DarkLyricsApi()
    api.helper.scraping_agent.get_cached_session().cache.clear()

    api.get_song_info_and_lyrics(song='another day', artist='dream theater')
    # This request is about a song from the same album, which page should now be cached
    api.get_song_info_and_lyrics(song='take the time', artist='dream theater')

    last_response = api.helper.scraping_agent.get_last_response()

    assert hasattr(last_response, 'from_cache') and last_response.from_cache is True


def test_not_cached_request_with_cached_session():
    api = DarkLyricsApi()
    api.helper.scraping_agent.get_cached_session().cache.clear()

    api.get_song_info_and_lyrics(song='somewhere', artist='within temptation')
    last_response = api.helper.scraping_agent.get_last_response()

    assert hasattr(last_response, 'from_cache') and last_response.from_cache is False


def test_request_without_cached_session():
    api = DarkLyricsApi(use_cache=False)

    api.get_song_info_and_lyrics(song='somewhere', artist='within temptation')
    last_response = api.helper.scraping_agent.get_last_response()

    assert hasattr(last_response, 'from_cache') is False


# ------------------------ get_artists_list() API ------------------------- #


def test_get_artists_list_given_initial_letter():
    api = DarkLyricsApi()
    artists_list = api.get_artists_list(initial_letter='d')

    assert 'Dimmu Borgir' in artists_list


def test_get_artists_list_given_initial_letter_value_negative():
    with pytest.raises(ValueError) as e:
        api = DarkLyricsApi()
        api.get_artists_list(initial_letter='qwerty')

    assert 'Initial letter must be a string with length = 1' in str(e.value)


def test_get_artists_list_given_initial_letter_artist_negative():
    api = DarkLyricsApi()
    artists_list = api.get_artists_list(initial_letter='e')

    assert 'Dimmu Borgir' not in artists_list


@pytest.mark.skipif(os.environ.get('TRAVIS') == 'true', reason=SKIP_ON_TRAVIS)
def test_get_all_artists_on_darklyrics():
    api = DarkLyricsApi()
    artists_list = api.get_artists_list()

    assert 'Dissection' in artists_list
    assert 'Sepultura' in artists_list
    assert 'Testament' in artists_list


# ------------------------ get_albums_info() API -------------------------- #


def test_get_albums_list_from_artist():
    api = DarkLyricsApi()
    artist = 'iron maiden'
    albums_list = api.get_albums_info(artist=artist, title_only=True)

    assert 'Killers' in albums_list


def test_get_albums_list_with_info_from_artist():
    api = DarkLyricsApi()
    artist = 'iron maiden'
    albums_list = api.get_albums_info(artist=artist)
    test_album = albums_list[3]

    assert test_album['title'] == 'Piece Of Mind' and test_album['type'] == 'album' and test_album['release_year'] == '1983'


def test_get_albums_list_from_artist_negative():
    with pytest.raises(ArtistNotFoundException) as e:
        api = DarkLyricsApi()
        artist = 'unexistent band'
        api.get_albums_info(artist=artist, title_only=True)

    assert 'Artist page for "{}" not found'.format(artist.title()) in str(e.value)


def test_get_albums_list_from_artist_value_negative():
    api = DarkLyricsApi()
    artist = 'iron maiden'
    albums_list = api.get_albums_info(artist=artist, title_only=True)

    assert 'Reign In Blood' not in albums_list


def test_get_albums_list_from_artist_having_ep():
    api = DarkLyricsApi()
    artist = "[,SILU:'ET]"
    albums_list = api.get_albums_info(artist=artist, title_only=True)

    assert 'Theory Of Dream' in albums_list


# ------------------------- get_songs_info() API -------------------------- #


def test_get_songs_list_from_artist_album():
    api = DarkLyricsApi()
    artist = 'pantera'
    album = 'vulgar display of power'
    songs_list = api.get_songs_info(artist, album=album, title_only=True)

    assert 'Fucking Hostile' in songs_list


def test_get_songs_list_from_artist_album_artist_negative():
    with pytest.raises(ArtistNotFoundException) as e:
        api = DarkLyricsApi()
        artist = 'unexisting band'
        album = 'vulgar display of power'
        api.get_songs_info(artist, album, title_only=True)

    assert 'Artist page for "{}" not found'.format(artist.title()) in str(e.value)


def test_get_songs_list_from_artist_album_album_negative():
    with pytest.raises(SongsNotFoundException) as e:
        api = DarkLyricsApi()
        artist = 'pantera'
        album = 'live in nowhere'
        api.get_songs_info(artist, album, title_only=True)

    assert 'Songs not found for the artist "{}" and the album "{}".'.format(artist.title(), album.title()) in str(e.value)


def test_get_songs_list_from_artist_album_song_negative():
    api = DarkLyricsApi()
    artist = 'pantera'
    album = 'vulgar display of power'
    songs_list = api.get_songs_info(artist, album, title_only=True)

    assert 'Cemetery Gates' not in songs_list


@pytest.mark.skipif(os.environ.get('TRAVIS') == 'true', reason=SKIP_ON_TRAVIS)
def test_get_songs_and_info_list_from_artist_album():
    api = DarkLyricsApi()
    artist = 'pantera'
    album = 'cowboys from hell'
    songs_list = api.get_songs_info(artist, album, title_only=False)

    assert songs_list[4]['title'] == 'Cemetery Gates' and songs_list[4]['album_track'] == '5'


@pytest.mark.skipif(os.environ.get('TRAVIS') == 'true', reason=SKIP_ON_TRAVIS)
def test_get_songs_and_info_list_from_artist_album_song_negative():
    api = DarkLyricsApi()
    artist = 'pantera'
    album = 'cowboys from hell'
    songs_list = api.get_songs_info(artist, album, title_only=False)

    assert songs_list[4]['title'] != 'Shattered' and songs_list[4]['album_track'] != '9'


def test_get_songs_list_from_artist():
    api = DarkLyricsApi()
    artist = 'dream theater'
    songs_list = api.get_songs_info(artist, album=None, title_only=True)

    assert '6:00' in songs_list


def test_get_songs_list_from_artist_song_negative():
    api = DarkLyricsApi()
    artist = 'dream theater'
    songs_list = api.get_songs_info(artist, album=None, title_only=True)

    assert 'unexisting song' not in songs_list


# -------------------- get_album_info_and_lyrics() API --------------------- #


@pytest.mark.skipif(os.environ.get('TRAVIS') == 'true', reason=SKIP_ON_TRAVIS)
def test_get_album_info_and_lyrics():
    api = DarkLyricsApi()
    artist = 'slayer'
    album = 'reign in blood'
    info_lyrics_list = api.get_album_info_and_lyrics(album=album, artist=artist)
    found_lyrics = None

    for info_lyrics in info_lyrics_list:
        if info_lyrics['title'] == 'Postmortem' and info_lyrics['track_no'] == 9:
            found_lyrics = info_lyrics
            break

    assert found_lyrics is not None and 'chanting lines of blind witchery' in found_lyrics['lyrics'].lower()


def test_get_album_info_and_lyrics_negative():
    with pytest.raises(SongsNotFoundException) as e:
        api = DarkLyricsApi()
        artist = 'slayer'
        album = 'ride the lightning'
        api.get_album_info_and_lyrics(album=album, artist=artist)

    assert 'Songs not found for the artist "{}" and the album "{}".'.format(artist.title(), album.title()) in str(e.value)


def test_get_album_info_and_lyrics_artist_negative():
    with pytest.raises(ArtistNotFoundException) as e:
        api = DarkLyricsApi()
        artist = 'unexistent band'
        album = 'ride the lightning'
        api.get_album_info_and_lyrics(album=album, artist=artist)

    assert 'Artist page for "{}" not found'.format(artist.title()) in str(e.value)


# ------------------- get_albums_info_and_lyrics_by_artist() API -------------------- #


@pytest.mark.skipif(os.environ.get('TRAVIS') == 'true', reason=SKIP_ON_TRAVIS)
def test_get_albums_info_and_lyrics_by_artist():
    api = DarkLyricsApi()
    artist = 'blind guardian'
    lyrics_list = api.get_albums_info_and_lyrics_by_artist(artist=artist)
    found_lyrics = None

    for lyrics in lyrics_list:
        if lyrics['album'] == 'Nightfall In Middle-Earth' and lyrics['title'] == 'Captured':
            found_lyrics = lyrics
            break

    assert found_lyrics is not None and 'you are now my guest' in found_lyrics['lyrics'].lower()


def test_get_albums_info_and_lyrics_by_artist_negative():
    with pytest.raises(ArtistNotFoundException) as e:
        api = DarkLyricsApi()
        artist = 'unexisting band'
        api.get_albums_info_and_lyrics_by_artist(artist=artist)

    assert 'Artist page for "{}" not found'.format(artist.title()) in str(e.value)


# -------------------- get_song_info_and_lyrics() API ---------------------- #


@pytest.mark.skipif(os.environ.get('TRAVIS') == 'true', reason=SKIP_ON_TRAVIS)
def test_get_song_info_and_lyrics():
    api = DarkLyricsApi()
    song = 'under grey skies'
    artist = 'kamelot'
    song_info = api.get_song_info_and_lyrics(song=song, artist=artist)

    assert 'in the age of confusion' in song_info['lyrics'].lower()
    assert song_info['album'] == 'Haven' and song_info['release_year'] == '2015' and song_info['track_no'] == 5


@pytest.mark.skipif(os.environ.get('TRAVIS') == 'true', reason=SKIP_ON_TRAVIS)
def test_get_song_lyrics_only():
    api = DarkLyricsApi()
    song = 'under grey skies'
    artist = 'kamelot'
    lyrics = api.get_song_info_and_lyrics(song=song, artist=artist, lyrics_only=True)

    assert 'in the age of confusion' in lyrics.lower()


@pytest.mark.skipif(os.environ.get('TRAVIS') == 'true', reason=SKIP_ON_TRAVIS)
def test_get_song_lyrics_with_special_chars():
    api = DarkLyricsApi()
    song = 'stovi stovi berželis'
    artist = 'žalvarinis'
    lyrics = api.get_song_info_and_lyrics(song=song, artist=artist, lyrics_only=True)

    assert 'ir atjojo bernelis prie' in lyrics.lower()


@pytest.mark.skipif(os.environ.get('TRAVIS') == 'true', reason=SKIP_ON_TRAVIS)
def test_get_song_info_and_lyrics_negative():
    with pytest.raises(LyricsNotFoundException) as e:
        api = DarkLyricsApi()
        song = 'under grey skies'
        artist = 'dismember'
        api.get_song_info_and_lyrics(song=song, artist=artist)

    assert 'Lyrics for "{}" not found'.format(song) in str(e.value)
