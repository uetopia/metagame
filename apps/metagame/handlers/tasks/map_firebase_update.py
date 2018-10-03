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

from apps.metagame.controllers.maps import MapsController
from apps.metagame.controllers.zones import ZonesController

from configuration import *

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']

class MapUpdateFirebaseHandler(BaseHandler):
    def post(self):
        logging.info("[TASK] MapUpdateFirebaseHandler")

        key_id = self.request.get('key_id')

        map = MapsController().get_by_key_id(int(key_id))
        if not map:
            logging.error('map not found')
            return

        zoneController = ZonesController()

        ## get all of the zones in this map
        ## these are in order, so long as the count has not changed we can rebuild with indexes
        zones = zoneController.list_ordered_by_mapKeyId(map.key.id())

        logging.info('found %s zones' % len(zones))

        vertical_rows = []

        current_zone_index = 0

        # loop over the horizontal
        for verticalIndex in range(map.zoneCountVertical):
            horizontal_row = []
            for horizontalIndex in range(map.zoneCountHorizontal):
            #for verticalIndex in range(map.zoneCountVertical):
                horizontal_row.append(zones[current_zone_index].to_json())
                current_zone_index = current_zone_index +1

            vertical_rows.append(horizontal_row)

        #credentials = AppAssertionCredentials(
        #    'https://www.googleapis.com/auth/sqlservice.admin')
        credentials = GoogleCredentials.get_application_default().create_scoped(_FIREBASE_SCOPES)

        http_auth = credentials.authorize(Http())

        map.zones = vertical_rows
        map_json = map.to_json()

        model_json = json.dumps(map_json)

        #logging.info(model_json)
        headers = {"Content-Type": "application/json"}

        URL = "%s/regions/%s/maps/%s.json" % (FIREBASE_DATABASE_ROOT, map.regionKeyId, map.key.id() )
        resp, content = http_auth.request(URL,
                          "PUT", ## Write or replace data to a defined path,
                          model_json,
                          headers=headers)
