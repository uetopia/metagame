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
from apps.metagame.controllers.characters import CharactersController
from apps.metagame.controllers.season_characters import SeasonCharactersController

from configuration import *

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']

class CharactersUpdateFirebaseHandler(BaseHandler):
    """ /task/characters/firebase/update """
    def get(self):
        return self.post()

    def sortByRank(self, e):
        return e['rank']

    def post(self):
        logging.info("[TASK] CharactersUpdateFirebaseHandler")

        seasonController = SeasonsController()
        characterController = CharactersController()

        characters = characterController.list_by_top_rank()

        logging.info('found %s characters' % len(characters))

        character_list = []

        for character in characters:
            character_list.append(character.to_json_thin())

        characters_json = json.dumps(character_list)
        credentials = GoogleCredentials.get_application_default().create_scoped(_FIREBASE_SCOPES)
        http_auth = credentials.authorize(Http())

        #logging.info(model_json)
        headers = {"Content-Type": "application/json"}

        URL = "%s/characters.json" % (FIREBASE_DATABASE_ROOT )
        resp, content = http_auth.request(URL,
                          "PUT", ## Write or replace data to a defined path,
                          characters_json,
                          headers=headers)
