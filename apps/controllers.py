import logging
import datetime
import string
import random
import hashlib
import hmac
import urllib
import md5
from google.appengine.ext import ndb
from collections import OrderedDict

class BaseController(object):
    """Base Controller Class - Provides basic database functionality. """
    def __init__(self):

        self._default_order = self.model.created
        self.model = None

    def create(self, **kwargs):
        """ creates a page """
        entity = self.model(**kwargs)
        entity.put()
        return entity

    def list(self):
        """ list all  """
        query = self.model.query()
        return query.fetch(1000)

    def list_page(self, page_size=20, batch_size=5, start_cursor=None, order=None):
        query = self.model.query()
        if order:
            query_forward = query.order(order)
        else:
            query_forward = query.order(self.model.key)
        entities, cursor, more = query_forward.fetch_page(page_size,start_cursor=start_cursor, batch_size=batch_size)

        return entities, cursor, more


    def get_by_key(self, key):
        """ get an entity by key """
        key = ndb.Key(urlsafe=key)
        return key.get()

    def get_by_key_id(self, key_id):
        """ get an entity by key_id """
        return self.model.get_by_id(key_id)

    def update(self, entity):
        """ update an entity """
        entity.put()

    def delete(self, entity):
        """Deletes the given entity """
        entity.key.delete()

    def verify_signed_auth(self, request):
        ## Incoming data:
        ######### API authentication ################
        ## API Key from the headers
        ## POST data (?param=val&param1=val1) signed by a shared secret key according to HMAC-SHA512 method;

        apiKey = request.headers['Key']

        ## Get the shared secret associated with this key
        model = self.get_by_api_key(apiKey)
        if model:
            apiSecret = str(model.apiSecret)
        else:
            return False

        signature = request.headers['Sign']

        logging.info("request.body: %s" % request.body)
        logging.info("params: ")
        logging.info(request.arguments())
        logging.info("Headers: %s" %request.headers)

        sorted_params = request.body

        encryption = request.get('encryption', 'sha512')
        logging.info("encryption: %s" % encryption)

        # Hash the params string to produce the Sign header value
        if encryption == 'off':
            sign = signature
        elif encryption == 'sha1':
            m = hashlib.sha1
            m.update()
            H = hmac.new(apiSecret, digestmod=hashlib.sha1)
        else:
            H = hmac.new(apiSecret, digestmod=hashlib.sha512)
            H.update(sorted_params)
            sign = H.hexdigest()
        logging.info("sign: %s" %sign)
        logging.info("Hsig: %s" %signature )

        if sign == signature:
            return model
        else:
            return False


    def verify_signed_auth_by_key(self, request):
        ## Incoming data:
        ######### API authentication ################
        ## API Key from the headers
        ## POST data (?param=val&param1=val1) signed by a shared secret key according to HMAC-SHA512 method;

        apiKey = request.headers['Key']

        ## Get the shared secret associated with this key
        model = self.get_by_key(apiKey)
        if model:
            apiSecret = str(model.apiSecret)
        else:
            return False

        signature = request.headers['Sign']
        logging.info("Hsig: %s" %signature )

        logging.info("request.body: %s" % request.body)
        logging.info("params: ")
        logging.info(request.arguments())

        sorted_params = request.body

        encryption = request.get('encryption', 'sha512')
        logging.info("encryption: %s" % encryption)

        # Hash the params string to produce the Sign header value
        if encryption == 'off':
            sign = signature
        elif encryption == 'sha1':
            m = hashlib.sha1
            m.update()
            H = hmac.new(apiSecret, digestmod=hashlib.sha1)
        else:
            H = hmac.new(apiSecret, digestmod=hashlib.sha512)
            H.update(sorted_params)
            sign = H.hexdigest()

        logging.info("sign: %s" %sign)
        logging.info("Hsig: %s" %signature )

        if sign == signature:
            return model
        else:
            return False
