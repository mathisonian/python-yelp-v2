#!/usr/bin/env python


'''A python wrapper for the Yelp API v2'''


__author__ = "Matthew Conlen"
__maintainer__ = "Matthew Conlen"
__email__ = "github@mathisonian.com"

__copyright__ = "Copyright 2012, 2013, Mattew Conlen"
__license__ = "APACHE 2.0"
__version__ = "0.5.7"
__status__ = "Development"


import oauth2 as oauth
import json
import urllib
import urllib2
import time
from filecache import FileCache


# A singleton representing a lazily instantiated FileCache.
DEFAULT_CACHE = object()

# cache for 1 minute
DEFAULT_CACHE_TIMEOUT = 60


def clean_url_component(s):
    if isinstance(s, unicode):
        # hashlib.md5() in FileCache does not accept unicode objects.
        s = s.encode('utf-8')
    try:
        s.decode('ascii')
    except UnicodeError:
        # urllib only accepts ASCII in urls.
        s = urllib.quote(s)
    return s


class Api(object):
    '''
    A python interface to the yelp API v2
    '''

    def __init__(self,
                 consumer_key=None,
                 consumer_secret=None,
                 access_token_key=None,
                 access_token_secret=None,
                 cache=DEFAULT_CACHE,
                 cache_timeout=DEFAULT_CACHE_TIMEOUT
                 ):

        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token_key = access_token_key
        self.access_token_secret = access_token_secret
        self.host = "api.yelp.com"
        self.SetCache(cache)
        self.SetCacheTimeout(cache_timeout)

        if consumer_key is not None \
            and consumer_secret is not None \
            and access_token_key is not None \
            and access_token_secret is not None:

            self._signature_method_plaintext = oauth.SignatureMethod_PLAINTEXT()
            self._signature_method_hmac_sha1 = oauth.SignatureMethod_HMAC_SHA1()

        self._oauth_token = oauth.Token(key=access_token_key, secret=access_token_secret)
        self._oauth_consumer = oauth.Consumer(key=consumer_key, secret=consumer_secret)

    def SetCacheTimeout(self, cache_timeout):
        '''Override the default cache timeout.

        Args:
          cache_timeout:
            Time, in seconds, that responses should be reused.
        '''
        self._cache_timeout = cache_timeout

    def SetCache(self, cache):
        '''Override the default cache.  Set to None to prevent caching.

        Args:
          cache:
            An instance that supports the same API as the FileCache
        '''

        if cache == DEFAULT_CACHE:
            self._cache = FileCache()
        else:
            self._cache = cache

    def GetBusiness(self, id):
        id = clean_url_component(id)
        url = "http://" + self.host + "/v2/business/" + id

        response = self._FetchUrl(url=url)
        response = json.loads(response)
        if "error" in response:
            raise Exception(response["error"])
        return Business.NewFromJsonDict(response)

    def Search(self,
               #term=None,
               #limit=None,
               #offset=None,
               #sort=None,
               #category_filter=None,
               #radius_filter=None,
               #deals_filter=None,
               #location=None,
               **kwargs):

        if not kwargs.get('location'):
            raise Exception('Location parameter is required when searching. e.g. client.Search(term="restaurant", location="detroit")')

        response = self._FetchUrl(url="http://" + self.host + '/v2/search?' +urllib.urlencode(kwargs))
        response = json.loads(response)
        if "error" in response:
            raise Exception(response["error"])
        return SearchResultSet.NewFromJsonDict(response)

    def _FetchUrl(self,
                  url,
                  post_data=None,
                  no_cache=None,
                  use_gzip_compression=None):
        '''Fetch a URL, optionally caching for a specified time.

        Args:
          url:
            The URL to retrieve
          post_data:
            A dict of (str, unicode) key/value pairs.
            If set, POST will be used.
          no_cache:
            If true, overrides the cache on the current request
          use_gzip_compression:
            If True, tells the server to gzip-compress the response.
            It does not apply to POST requests.
            Defaults to None, which will get the value to use from
            the instance variable self._use_gzip [Optional]

        Returns:
          A string containing the body of the response.
        '''

        if post_data:
            http_method = "POST"
        else:
            http_method = "GET"

        # if use_gzip_compression is None:
        #     use_gzip = self._use_gzip
        # else:
        #     use_gzip = use_gzip_compression

        # # Set up compression
        # if use_gzip and not post_data:
        #     opener.addheaders.append(('Accept-Encoding', 'gzip'))

        oauth_request = oauth.Request(http_method, url, {})
        oauth_request.update({'oauth_nonce': oauth.generate_nonce(),
                              'oauth_timestamp': oauth.generate_timestamp(),
                              'oauth_token': self.access_token_key,
                              'oauth_consumer_key': self.consumer_key})

        oauth_request.sign_request(oauth.SignatureMethod_HMAC_SHA1(), self._oauth_consumer, self._oauth_token)
        signed_url = oauth_request.to_url()

        # Unique keys are a combination of the url and the oAuth Consumer Key
        if self.consumer_key:
            key = self.consumer_key + ':' + url
        else:
            key = url

        # See if it has been cached before
        last_cached = self._cache.GetCachedTime(key)

        # If the cached version is outdated then fetch another and store it
        if not last_cached or time.time() >= last_cached + self._cache_timeout:
            # Connect
            try:
                conn = urllib.urlopen(signed_url, None)
            except urllib2.HTTPError, error:
                raise Exception("Error accessing yelp api " + error.read())
            else:
                try:
                    response = conn.read()
                    self._cache.Set(key, response)
                finally:
                    conn.close()
        else:
            response = self._cache.Get(key)

        # Always return the latest version
        return response

class SearchResultSet(object):

    """ TODO make iterable, subscriptable """

    def __init__(self,
                 region=None,
                 total=None,
                 businesses=None):
        self.region = region
        self.total = total
        self.businesses = businesses

    @staticmethod
    def NewFromJsonDict(data):
        return SearchResultSet(region=data.get('region', None),
                               total=data.get('total', 0),
                               businesses=map(Business.NewFromJsonDict, data.get('businesses', [])))


class Business(object):

    def __init__(self,
                 categories=None,
                 deals=None,
                 display_phone=None,
                 id=None,
                 image_url=None,
                 is_claimed=None,
                 is_closed=None,
                 location=None,
                 mobile_url=None,
                 name=None,
                 phone=None,
                 rating=None,
                 rating_img_url=None,
                 rating_img_large=None,
                 rating_img_small=None,
                 review_count=None,
                 reviews=None,
                 snippet_image_url=None,
                 snippet_text=None,
                 url=None):

        self.categories = categories
        self.deals = deals
        self.display_phone = display_phone
        self.id = id
        self.image_url = image_url
        self.is_claimed = is_claimed
        self.is_closed = is_closed
        self.location = location
        self.mobile_url = mobile_url
        self.name = name
        self.phone = phone
        self.rating = rating
        self.rating_img_url = rating_img_url
        self.rating_img_large = rating_img_large
        self.rating_img_small = rating_img_small
        self.review_count = review_count
        self.reviews = reviews
        self.snippet_image_url = snippet_image_url
        self.snippet_text = snippet_text
        self.url = url

    @staticmethod
    def NewFromJsonDict(data):
        return Business(categories=data.get("categories", None),
                        deals=data.get("deals", None),
                        display_phone=data.get("display_phone", None),
                        id=data.get("id", None),
                        image_url=data.get("image_url", None),
                        is_claimed=data.get("is_claimed", None),
                        is_closed=data.get("is_closed", None),
                        location=Location.NewFromJsonDict(data.get("location", None)),
                        mobile_url=data.get("mobile_url", None),
                        name=data.get("name", None),
                        phone=data.get("phone", None),
                        rating=data.get("rating", None),
                        rating_img_url=data.get("rating_img_url", None),
                        rating_img_large=data.get("rating_img_large", None),
                        rating_img_small=data.get("rating_img_small", None),
                        review_count=data.get("review_count", None),
                        reviews=map(Review.NewFromJsonDict, data.get('reviews', [])),
                        snippet_image_url=data.get("snippet_image_url", None),
                        snippet_text=data.get("snippet_text", None),
                        url=data.get("url", None))


class Review(object):
    def __init__(self,
                 excerpt=None,
                 id=None,
                 rating=None,
                 rating_image_large_url=None,
                 rating_image_small_url=None,
                 rating_image_url=None,
                 time_created=None,
                 user=None):
        self.excerpt = excerpt
        self.id = id
        self.rating = rating
        self.rating_image_large_url = rating_image_large_url
        self.rating_image_small_url = rating_image_small_url
        self.rating_image_url = rating_image_url
        self.time_created = time_created
        self.user = user

    @staticmethod
    def NewFromJsonDict(data):
        return Review(excerpt=data.get("excerpt", None),
                      id=data.get("id", None),
                      rating=data.get("rating", None),
                      rating_image_large_url=data.get("rating_image_large_url", None),
                      rating_image_small_url=data.get("rating_image_small_url", None),
                      rating_image_url=data.get("rating_image_url", None),
                      time_created=data.get("time_created", None),
                      user=User.NewFromJsonDict(data.get("user", None)))


class User(object):
    def __init__(self,
                 id=None,
                 image_url=None,
                 name=None):
        self.id = id
        self.image_url = image_url
        self.name = name

    @staticmethod
    def NewFromJsonDict(data):
        return User(id=data.get("id", None),
                    image_url=data.get("image_url", None),
                    name=data.get("name", None))


class Location(object):
    def __init__(self,
                 address=None,
                 city=None,
                 coordinate=None,
                 country_code=None,
                 cross_streets=None,
                 display_address=None,
                 geo_accuracy=None,
                 neighborhoods=None,
                 postal_code=None,
                 state_code=None):
        self.address = address
        self.city = city
        self.coordinate = coordinate
        self.country_code = country_code
        self.cross_streets = cross_streets
        self.display_address = display_address
        self.geo_accuracy = geo_accuracy
        self.neighborhoods = neighborhoods
        self.postal_code = postal_code
        self.state_code = state_code

    @staticmethod
    def NewFromJsonDict(data):
        return Location(address=data.get("address", None),
                        city=data.get("city", None),
                        coordinate=data.get("coordinate", None),
                        country_code=data.get("country_code", None),
                        cross_streets=data.get("cross_streets", None),
                        display_address=data.get("display_address", None),
                        geo_accuracy=data.get("geo_accuracy", None),
                        neighborhoods=data.get("neighborhoods", None),
                        postal_code=data.get("postal_code", None),
                        state_code=data.get("state_code", None))


class Deal(object):
    def __init__(self,
                 id=None,
                 title=None,
                 url=None,
                 currency_code=None,
                 time_start=None,
                 time_end=None,
                 is_popular=None,
                 what_you_get=None,
                 important_restrictions=None,
                 additional_restrictions=None,
                 options=None):
        self.id = id
        self.title = title
        self.url = url
        self.currency_code = currency_code
        self.time_start = time_start
        self.time_end = time_end
        self.is_popular = is_popular
        self.what_you_get = what_you_get
        self.important_restrictions = important_restrictions
        self.additional_restrictions = additional_restrictions
        self.options = options

    @staticmethod
    def NewFromJsonDict(data):
      return Deal(id=data.get("id", None),
                  title=data.get("title", None),
                  url=data.get("url", None),
                  currency_code=data.get("currency_code", None),
                  time_start=data.get("time_start", None),
                  time_end=data.get("time_end", None),
                  is_popular=data.get("is_popular", None),
                  what_you_get=data.get("what_you_get", None),
                  important_restrictions=data.get("what_you_get", None),
                  additional_restrictions=data.get("additional_restrictions", None),
                  options=data.get("options", []))
