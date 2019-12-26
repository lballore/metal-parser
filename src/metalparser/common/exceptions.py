class MetalParserException(Exception):
    def __init__(self, message='Error'):
        super().__init__(message)


class LyricsNotFoundException(MetalParserException):
    def __init__(self, message='Error'):
        super().__init__(message)


class ArtistNotFoundException(MetalParserException):
    def __init__(self, message='Error'):
        super().__init__(message)


class SongsNotFoundException(MetalParserException):
    def __init__(self, message='Error'):
        super().__init__(message)
