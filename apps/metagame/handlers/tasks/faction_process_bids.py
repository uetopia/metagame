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
from apps.metagame.controllers.seasons import SeasonsController
from apps.metagame.controllers.regions import RegionsController
from apps.metagame.controllers.users import UsersController
from apps.metagame.controllers.bids import BidsController
from apps.metagame.controllers.factions import FactionsController

from configuration import *

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']

class FactionProcessBidsHandler(BaseHandler):
    def post(self):
        logging.info("[TASK] FactionProcessBidsHandler")

        key_id = self.request.get('key_id')

        mapController = MapsController()
        zoneController = ZonesController()
        bidController = BidsController()
        seasonController = SeasonsController()
        factionsController = FactionsController()

        faction = factionsController.get_by_key_id(int(key_id))
        if not faction:
            logging.error('faction not found')
            return


        # get the bids
        actionable_bids = bidController.list_processed_by_factionKeyId(faction.key.id())

        if len(actionable_bids) > 0:
            logging.info('found %s bids' % len(actionable_bids) )

            amount = 0

            for bid in actionable_bids:
                logging.info('processing bid')

                if bid.highBid:
                    logging.info('high bid - just removing it')
                else:
                    logging.info('not high bid - returning the amount')

                    amount = amount + bid.bidAmount

                bidController.delete(bid)

            faction.energy = faction.energy + amount
            factionsController.update(faction)

        ## TODO - task to update faction firebase

        return
