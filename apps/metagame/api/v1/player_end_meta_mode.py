import logging
import datetime
import string
import json
import hashlib
import hmac
import urllib
import httplib
from google.appengine.api import taskqueue
from apps.handlers import BaseHandler
from apps.metagame.controllers.users import UsersController
from apps.metagame.controllers.seasons import SeasonsController
from apps.metagame.controllers.factions import FactionsController
from apps.metagame.controllers.zones import ZonesController
from apps.metagame.controllers.bids import BidsController

from configuration import *

class playerEndMetaGameHandler(BaseHandler):
    def post(self):
        """
        Recieve Notification when a player stops meta game mode
        Requires http headers:  Key, Sign
        Requires POST parameters:  nonce
        """

        ucontroller = UsersController()
        seasonsController = SeasonsController()
        factionController = FactionsController()
        zoneController = ZonesController()
        bidController = BidsController()

        ## make sure the API key matches first
        incomingApiKey = self.request.headers['Key']
        if incomingApiKey != UETOPIA_ASSIGNED_GAME_API_KEY:
            logging.info('API key mismatch')
            return self.render_json_response(
                authorization = False,
                request_successful = False
            )

        signature = self.request.headers['Sign']

        logging.info("request.body: %s" % self.request.body)
        logging.info("params: ")
        logging.info(self.request.arguments())
        logging.info("Headers: %s" %self.request.headers)

        sorted_params = self.request.body

        # Hash the params string to produce the Sign header value
        H = hmac.new(UETOPIA_ASSIGNED_GAME_API_SECRET, digestmod=hashlib.sha512)
        H.update(sorted_params)
        sign = H.hexdigest()

        logging.info("sign: %s" %sign)
        logging.info("Hsig: %s" %signature )

        if sign != signature:
            logging.info('signature mismatch')
            return self.render_json_response(
                authorization = False,
                request_successful = False
            )

        ## At this point, authorization was successful.  Continue with the call.
        logging.info('auth success')

        ## parse the json out of the body.
        jsonstring = self.request.body
        logging.info(jsonstring)
        jsonobject = json.loads(jsonstring)

        ## make sure we have the player, and that it matches one we have already connected
        if 'player_key_id' not in jsonobject:
            logging.info('Did not find player_key_id in json')

            return self.render_json_response(
                authorization = True,
                request_successful = False
            )

        user = ucontroller.get_by_uetopia_playerKeyId(jsonobject['player_key_id'])
        if not user:
            logging.info('user was not found.  make sure they connect to metagame first.')
            return self.render_json_response(
                authorization = True,
                request_successful = False
            )

        user.currentFactionKeyId = None
        user.currentFactionTag = None
        user.currentFactionLead = False
        user.currentFactionTeamLead = False

        ## update the user record.
        user.metaGameActive = False
        ucontroller.update(user)

        ## push out to firebase
        taskUrl='/task/user/firebase/update'
        taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': user.key.id()}, countdown = 2,)

        ## also update the zone if this user was controlling one.
        controlled_zone = zoneController.get_controlled_by_userCaptainKeyId(user.key.id())
        if controlled_zone:
            logging.info('found a zone this user was controlling')

            controlled_zone.controlled = False
            controlled_zone.factionKeyId = None
            controlled_zone.factionTag = None
            controlled_zone.userCaptainKeyId = None
            controlled_zone.userCaptainTitle = None
            controlled_zone.uetopiaGamePlayerKeyId = None
            controlled_zone.teamTitle = None

            zoneController.update(controlled_zone)

            ## don't bother updating the map here.

        ## also check for any bids that are pending.
        pending_bid = bidController.get_unprocessed_by_userKeyId(user.key.id())
        if pending_bid:
            logging.info('found a pending bid')

            ## maybe make it inactive or something more fancy if you want.  Just deleting it for now.
            bidController.delete(pending_bid)


        ## return status success so that uetopia knows the call worked.

        return self.render_json_response(
            authorization = True,
            request_successful=True
        )
