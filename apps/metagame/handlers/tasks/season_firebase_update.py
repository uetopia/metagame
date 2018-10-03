import endpoints
import logging
import uuid
import urllib
import json
from httplib2 import Http
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
from protorpc import remote
from protorpc import message_types
from google.appengine.datastore.datastore_query import Cursor
from oauth2client.contrib.appengine import AppAssertionCredentials
from oauth2client.client import GoogleCredentials
from protorpc import remote
from google.appengine.api import taskqueue

from apps.handlers import BaseHandler

from apps.metagame.controllers.seasons import SeasonsController

from configuration import *

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']

class SeasonUpdateFirebaseHandler(BaseHandler):
    def post(self):
        logging.info("[TASK] SeasonUpdateFirebaseHandler")

        key_id = self.request.get('key_id')

        season = SeasonsController().get_by_key_id(int(key_id))
        if not season:
            logging.error('Season not found')
            return

        season_json = json.dumps(season.to_json() )

        credentials = GoogleCredentials.get_application_default().create_scoped(_FIREBASE_SCOPES)
        http_auth = credentials.authorize(Http())

        headers = {"Content-Type": "application/json"}
        URL = "%s/active_season.json" %FIREBASE_DATABASE_ROOT
        resp, content = http_auth.request(URL,
                            "PUT",
                          ##"PUT", ## Write or replace data to a defined path,
                          season_json,
                          headers=headers)

        logging.info(resp)
        logging.info(content)
