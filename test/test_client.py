import pytest
import yelp
import urllib

class TestYelpAPIClient(object):


    def test_yelp(self, key, secret, token, token_secret):
        client = yelp.Api(consumer_key=key,
                          consumer_secret=secret,
                          access_token_key=token,
                          access_token_secret=token_secret)

        assert isinstance(client, yelp.Api)


    def test_business(self, key, secret, token, token_secret):
        client = yelp.Api(consumer_key=key,
                          consumer_secret=secret,
                          access_token_key=token,
                          access_token_secret=token_secret)


        business = client.GetBusiness('post-no-bills-brooklyn')
        assert business.name == 'Post No Bills'

    def test_business_unicode(self, key, secret, token, token_secret):
        client = yelp.Api(consumer_key=key,
                          consumer_secret=secret,
                          access_token_key=token,
                          access_token_secret=token_secret)


        business = client.GetBusiness(u'red-cat-jazz-caf\xe9-houston-3')
        assert business.name == u'Red Cat Jazz Caf\xe9'

    def test_business_utf8(self, key, secret, token, token_secret):
        client = yelp.Api(consumer_key=key,
                          consumer_secret=secret,
                          access_token_key=token,
                          access_token_secret=token_secret)


        business = client.GetBusiness(
            u'red-cat-jazz-caf\xe9-houston-3'.encode('utf-8'))
        assert business.name == u'Red Cat Jazz Caf\xe9'

    def test_business_quoted(self, key, secret, token, token_secret):
        client = yelp.Api(consumer_key=key,
                          consumer_secret=secret,
                          access_token_key=token,
                          access_token_secret=token_secret)


        business = client.GetBusiness(
            urllib.quote(u'red-cat-jazz-caf\xe9-houston-3'.encode('utf-8')))
        assert business.name == u'Red Cat Jazz Caf\xe9'

    def test_required_location(self, key, secret, token, token_secret):
        client = yelp.Api(consumer_key=key,
                          consumer_secret=secret,
                          access_token_key=token,
                          access_token_secret=token_secret)


        search_results = None
        try:
            search_results = client.Search(term="bar")
        except Exception, e:
            assert Exception

        assert search_results == None


    def test_search(self, key, secret, token, token_secret):
        client = yelp.Api(consumer_key=key,
                          consumer_secret=secret,
                          access_token_key=token,
                          access_token_secret=token_secret)


        search_results = client.Search(term="bar", location="bushwick")
        assert isinstance(search_results.businesses, list)

