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

from apps.metagame.controllers.factions import FactionsController
from apps.metagame.controllers.zones import ZonesController

from configuration import *

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']

class FactionUpdateFirebaseHandler(BaseHandler):
    def post(self):
        logging.info("[TASK] FactionUpdateFirebaseHandler")

        key_id = self.request.get('key_id')

        faction = FactionsController().get_by_key_id(int(key_id))
        if not faction:
            logging.error('faction not found')
            return

        ## get the zones that this faction currently controls?
        ## link back to the region/map in html

        zoneController = ZonesController()

        zones_json = []

        zones = zoneController.list_by_factionKeyId(faction.key.id())
        for zone in zones:
            zones_json.append(zone.to_json())

        faction.zones = zones_json
        faction_json = json.dumps(faction.to_json_with_zones() )

        credentials = GoogleCredentials.get_application_default().create_scoped(_FIREBASE_SCOPES)
        http_auth = credentials.authorize(Http())

        headers = {"Content-Type": "application/json"}
        URL = "%s/factions/%s.json" % (FIREBASE_DATABASE_ROOT, faction.key.id())
        resp, content = http_auth.request(URL,
                            "PUT",
                          ##"PUT", ## Write or replace data to a defined path,
                          faction_json,
                          headers=headers)

        logging.info(resp)
        logging.info(content)
