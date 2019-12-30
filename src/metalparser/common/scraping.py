import json
import os
import random
import requests
import requests_cache
import time

from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from ratelimit import limits, sleep_and_retry


class ScrapingAgent:
    """
    Instantiate an object with cached and uncached web crawling functions.

    Parameters
    ----------
    use_cache : bool
        Boolean defining if a cached session will be created or not

    Attributes
    ----------
    cache_expires_after : int
        Expiring time for cached contents
    cached_session : CachedSession
        Object instantiating a cached session for requests

    Methods
    -------
    get_page_from_url(self, url)
        Returns a DarkLyrics.com page related to an artist in form of a BeautifulSoup object.

    get_cached_session(self)
        Returns the cached_session attribute.
    """

    def __init__(self, use_cache=True):
        self.cache_validity = 7200
        self.cached_session = self.__create_cached_session() if use_cache is True else None

        if self.cached_session:
            self.__remove_expired_entries()

    def get_page_from_url(self, url):
        """
        Returns a DarkLyrics.com page related to an artist in form of a BeautifulSoup object.

        Arguments:
            url {str} -- A string containing an URL

        Returns:
            [BeautifulSoup] -- An HTML page related to the specified URL in form of a BeautifulSoup object
        """

        if self.__is_cached(url):
            response = self.__get_response_without_limiter(url)
        else:
            response = self.__get_response_with_limiter(url)

        page = BeautifulSoup(response.content, 'html.parser')

        return page

    def get_cached_session(self):
        """
        Returns the cached_session attribute.

        Returns:
            [CachedSession or None] -- The CachedSession object instantiated when initializing the object class.
        """

        return self.cached_session

    def __remove_expired_entries(self):
        """Removes expired entries from cache storage."""

        if not self.cache_validity:
            return

        expires_after = timedelta(seconds=self.cache_validity)
        self.cached_session.cache.remove_old_entries(datetime.utcnow() - expires_after)

    def __create_cached_session(self):
        """Initialize a cached session for requests."""

        cached_session = requests_cache.CachedSession(
            'metalparser_cache',
            backend='sqlite',
            expire_after=self.cache_validity
        )

        return cached_session

    @sleep_and_retry
    @limits(calls=60, period=60)
    def __get_response_with_limiter(self, url):
        """Make an HTTP request to darklyrics.com with a limited amount of calls per minute."""

        headers = self.__get_headers()

        response = requests.get(url, headers=headers)
        print('HERE')
        time.sleep(2)  # Avoid too many reqs per second, which can lead to a blacklist

        return response

    def __get_response_without_limiter(self, url):
        """Retrieve the response from cache, given that the URL is cached."""

        headers = self.__get_headers()
        response = self.cached_session.get(url, headers=headers)

        return response

    def __get_headers(self):
        """
        Make an HTTP request and returns the response.
        If the URL is cached, then returns a response from the persistent sqlite cache.
        """

        user_agent = random.choice(self.__get_user_agents_list())
        headers = {
            'User-Agent': user_agent
        }

        return headers

    def __is_cached(self, url):
        """Check if an URL is already cached."""

        if not self.cached_session:
            return False

        return self.cached_session.cache.has_url(url)

    def __get_user_agents_list(self):
        """Creates a list of user agents from the corresponding JSON file."""

        file_path = os.path.dirname(os.path.realpath(__file__)) + '/resources/user_agents.json'
        with open(file_path, 'r') as f:
            user_agents_list = [ua['user_agent'] for ua in json.loads(f.read())]

        return user_agents_list
