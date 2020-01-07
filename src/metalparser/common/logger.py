import logging


class MetalParserLogger:
    """
    Instantiate a logging.Logger object.

    Parameters
    ----------
    debug_mode : bool
        Boolean defining if the logging level (DEBUG if True, ERROR if False).

    Attributes
    ----------
    logger : Logger
        The logging.Logger object initialized.

    Methods
    -------
    get_logger(self)
        Returns the logger attribute.

    """
    def __init__(self, debug_mode):
        self.logger = None

        if debug_mode is True:
            self.__set_debug_mode_logger()
        else:
            self.__set_error_mode_logger()

    def get_logger(self):
        """
        Returns the logger attribute.

        Returns:
            [Logger] -- The logging.Logger object initialized.
        """

        return self.logger

    def __set_debug_mode_logger(self):
        """
        Set logger level to DEBUG and only display error messages on a log file and on console.
        It creates the log file in the folder from where the script is called.
        """

        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s %(levelname)-- 8s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            filename='metalparser.log',
            filemode='w'
        )
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        self.logger = logging.getLogger('metalparser')
        self.logger.addHandler(console_handler)

    def __set_error_mode_logger(self):
        """Set logger level to ERROR and only display error messages on console."""

        ch = logging.StreamHandler()
        ch.setLevel(logging.ERROR)

        self.logger = logging.getLogger('metalparser_console_only')
        self.logger.addHandler(ch)
