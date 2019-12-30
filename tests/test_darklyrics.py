import pytest

from metalparser.darklyrics import DarkLyricsApi
from metalparser.common.exceptions import ArtistNotFoundException, LyricsNotFoundException, SongsNotFoundException


@pytest.fixture
def create_api_object():
    def _create_api_object(use_cache=True):
        return DarkLyricsApi(use_cache=use_cache)

    return _create_api_object


# -------------------------- API OBJECT ------------------------------ #


def test_create_api_object_with_cached_session(create_api_object):
    api = create_api_object()

    assert api.helper.scraping_agent.get_cached_session() is not None


def test_create_api_object_without_cached_session(create_api_object):
    api = create_api_object(use_cache=False)

    assert api.helper.scraping_agent.get_cached_session() is None


def test_cached_request_with_cached_session(create_api_object):
    api = create_api_object()
    api.helper.scraping_agent.get_cached_session().cache.clear()

    api.get_lyrics_by_song(song='another day', artist='dream theater')
    # This request is about a song from the same album, which page should now be cached
    api.get_lyrics_by_song(song='take the time', artist='dream theater')

    last_response = api.helper.scraping_agent.get_last_response()

    assert hasattr(last_response, 'from_cache') and last_response.from_cache is True


def test_not_cached_request_with_cached_session(create_api_object):
    api = create_api_object()
    api.helper.scraping_agent.get_cached_session().cache.clear()

    api.get_lyrics_by_song(song='somewhere', artist='within temptation')
    last_response = api.helper.scraping_agent.get_last_response()

    assert hasattr(last_response, 'from_cache') and last_response.from_cache is False


def test_request_without_cached_session(create_api_object):
    api = create_api_object(use_cache=False)

    api.get_lyrics_by_song(song='somewhere', artist='within temptation')
    last_response = api.helper.scraping_agent.get_last_response()

    assert hasattr(last_response, 'from_cache') is False


# ------------------------- get_songs() API -------------------------- #


def test_get_songs_list_from_artist_album(create_api_object):
    api = create_api_object()
    artist = 'pantera'
    album = 'vulgar display of power'
    songs_only = True
    songs_list = api.get_songs(artist, songs_only, album)

    assert 'Fucking Hostile' in songs_list


def test_get_songs_list_from_artist_album_artist_negative(create_api_object):
    with pytest.raises(ArtistNotFoundException) as e:
        api = create_api_object()
        artist = 'unexisting band'
        album = 'vulgar display of power'
        songs_only = True
        api.get_songs(artist, songs_only, album)

    assert 'Artist page for "{}" not found'.format(artist.title()) in str(e.value)


def test_get_songs_list_from_artist_album_album_negative(create_api_object):
    with pytest.raises(SongsNotFoundException) as e:
        api = create_api_object()
        artist = 'pantera'
        album = 'live in nowhere'
        songs_only = True
        api.get_songs(artist, songs_only, album)

    assert 'Songs not found for the artist "{}" and the album "{}".'.format(artist.title(), album.title()) in str(e.value)


def test_get_songs_list_from_artist_album_song_negative(create_api_object):
    api = create_api_object()
    artist = 'pantera'
    album = 'vulgar display of power'
    songs_only = True
    songs_list = api.get_songs(artist, songs_only, album)

    assert 'Cemetery Gates' not in songs_list


def test_get_songs_and_info_list_from_artist_album(create_api_object):
    api = create_api_object()
    artist = 'pantera'
    album = 'cowboys from hell'
    songs_only = False
    songs_list = api.get_songs(artist, songs_only, album)

    assert songs_list[4]['title'] == 'Cemetery Gates' and songs_list[4]['album_track'] == '5'


def test_get_songs_and_info_list_from_artist_album_song_negative(create_api_object):
    api = create_api_object()
    artist = 'pantera'
    album = 'cowboys from hell'
    songs_only = False
    songs_list = api.get_songs(artist, songs_only, album)

    assert songs_list[4]['title'] != 'Shattered' and songs_list[4]['album_track'] != '9'


def test_get_songs_list_from_artist(create_api_object):
    api = create_api_object()
    artist = 'dream theater'
    songs_only = True
    songs_list = api.get_songs(artist, songs_only)

    assert '6:00' in songs_list


def test_get_songs_list_from_artist_song_negative(create_api_object):
    api = create_api_object()
    artist = 'dream theater'
    songs_only = True
    songs_list = api.get_songs(artist, songs_only)

    assert 'unexisting song' not in songs_list


# ------------------------ get_albums() API -------------------------- #


def test_get_albums_list_from_artist(create_api_object):
    api = create_api_object()
    artist = 'iron maiden'
    albums_list = api.get_albums(artist=artist)

    assert 'Killers' in albums_list


def test_get_albums_list_from_artist_negative(create_api_object):
    with pytest.raises(ArtistNotFoundException) as e:
        api = create_api_object()
        artist = 'unexistent band'
        api.get_albums(artist=artist)

    assert 'Artist page for "{}" not found'.format(artist.title()) in str(e.value)


def test_get_albums_list_from_artist_value_negative(create_api_object):
    api = create_api_object()
    artist = 'iron maiden'
    albums_list = api.get_albums(artist=artist)

    assert 'Reign In Blood' not in albums_list


def test_get_albums_list_from_artist_having_ep(create_api_object):
    api = create_api_object()
    artist = "[,SILU:'ET]"
    albums_list = api.get_albums(artist=artist)

    assert 'Theory Of Dream' in albums_list


# ------------------------ get_artists() API ------------------------- #


def test_get_artists_list_given_initial_letter(create_api_object):
    api = create_api_object()
    artists_list = api.get_artists(initial_letter='d')

    assert 'Dimmu Borgir' in artists_list


def test_get_artists_list_given_initial_letter_value_negative(create_api_object):
    with pytest.raises(ValueError) as e:
        api = create_api_object()
        api.get_artists(initial_letter='qwerty')

    assert 'Initial letter must be a string with length = 1' in str(e.value)


def test_get_artists_list_given_initial_letter_artist_negative(create_api_object):
    api = create_api_object()
    artists_list = api.get_artists(initial_letter='e')

    assert 'Dimmu Borgir' not in artists_list


def test_get_all_artists_on_darklyrics(create_api_object):
    api = create_api_object()
    artists_list = api.get_artists()

    assert 'Dissection' in artists_list
    assert 'Sepultura' in artists_list
    assert 'Testament' in artists_list


# ------------------- get_lyrics_by_artists() API -------------------- #


def test_get_lyrics_by_artist(create_api_object):
    api = create_api_object()
    artist = 'blind guardian'
    lyrics_list = api.get_lyrics_by_artist(artist=artist)
    found_lyrics = None

    for lyrics in lyrics_list:
        if lyrics['album'] == 'Nightfall In Middle-Earth' and lyrics['title'] == 'Captured':
            found_lyrics = lyrics
            break

    assert found_lyrics is not None and 'you are now my guest' in found_lyrics['lyrics'].lower()


def test_get_lyrics_by_artist_negative(create_api_object):
    with pytest.raises(ArtistNotFoundException) as e:
        api = create_api_object()
        artist = 'unexisting band'
        api.get_lyrics_by_artist(artist=artist)

    assert 'Artist page for "{}" not found'.format(artist.title()) in str(e.value)


# -------------------- get_lyrics_by_album() API --------------------- #


def test_get_lyrics_by_album(create_api_object):
    api = create_api_object()
    artist = 'slayer'
    album = 'reign in blood'
    lyrics_list = api.get_lyrics_by_album(album=album, artist=artist)
    found_lyrics = None

    for lyrics in lyrics_list:
        if lyrics['title'] == 'Postmortem' and lyrics['track_no'] == 9:
            found_lyrics = lyrics
            break

    assert found_lyrics is not None and 'chanting lines of blind witchery' in found_lyrics['lyrics'].lower()


def test_get_lyrics_by_album_negative(create_api_object):
    with pytest.raises(SongsNotFoundException) as e:
        api = create_api_object()
        artist = 'slayer'
        album = 'ride the lightning'
        api.get_lyrics_by_album(album=album, artist=artist)

    assert 'Songs not found for the artist "{}" and the album "{}".'.format(artist.title(), album.title()) in str(e.value)


def test_get_lyrics_by_album_artist_negative(create_api_object):
    with pytest.raises(ArtistNotFoundException) as e:
        api = create_api_object()
        artist = 'unexistent band'
        album = 'ride the lightning'
        api.get_lyrics_by_album(album=album, artist=artist)

    assert 'Artist page for "{}" not found'.format(artist.title()) in str(e.value)


# -------------------- get_lyrics_by_song() API ---------------------- #


def test_get_lyrics_by_song(create_api_object):
    api = create_api_object()
    song = 'under grey skies'
    artist = 'kamelot'
    lyrics = api.get_lyrics_by_song(song=song, artist=artist)

    assert 'in the age of confusion' in lyrics.lower()


def test_get_lyrics_by_song_with_special_chars(create_api_object):
    api = create_api_object()
    song = 'stovi stovi berželis'
    artist = 'žalvarinis'
    lyrics = api.get_lyrics_by_song(song=song, artist=artist)

    assert 'ir atjojo bernelis prie' in lyrics.lower()


def test_get_lyrics_by_song_negative(create_api_object):
    with pytest.raises(LyricsNotFoundException) as e:
        api = create_api_object()
        song = 'under grey skies'
        artist = 'dismember'
        api.get_lyrics_by_song(song=song, artist=artist)

    assert 'Lyrics for "{}" not found'.format(song) in str(e.value)
