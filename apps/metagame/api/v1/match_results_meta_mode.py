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
from apps.metagame.controllers.match import MatchController
from apps.metagame.controllers.zones import ZonesController

from configuration import *

class matchResultsMetaGameHandler(BaseHandler):
    def post(self):
        """
        Recieve notification when a match is complete.
        Requires http headers:  Key, Sign
        Requires POST parameters:  nonce
        """

        ucontroller = UsersController()
        seasonsController = SeasonsController()
        factionController = FactionsController()
        matchController = MatchController()
        zonesController = ZonesController()

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
        if 'match_key_id' not in jsonobject:
            logging.info('Did not find match_key_id in json')

            return self.render_json_response(
                authorization = True,
                request_successful = False
            )

        match = matchController.get_by_key_id(jsonobject['match_key_id'])
        if not match:
            logging.info('match was not found.')
            return self.render_json_response(
                authorization = True,
                request_successful = False
            )

        ## we need the active season too
        active_season = seasonsController.get_active()
        if not active_season:
            logging.info('active_season was not found.')
            return self.render_json_response(
                authorization = True,
                request_successful = False
            )

        ## grab information about the winner - this is a gameplayerkeyid
        if 'winning_user_key_id' in jsonobject:
            logging.info('Found winning_user_key_id in json')

            winning_user = ucontroller.get_by_uetopia_playerKeyId(jsonobject['winning_user_key_id'])
            if not winning_user:
                logging.info('winning user not found')
                return self.render_json_response(
                    authorization = True,
                    request_successful = False
                )

            ## make sure we have this group/faction in the database already.
            winning_faction = factionController.get_by_key_id(winning_user.currentFactionKeyId)
            if not winning_faction:
                logging.info('could not find the connected winning_faction')
                return self.render_json_response(
                    authorization = True,
                    request_successful = False
                )

        # get the zone associated with this match
        zone = zonesController.get_by_key_id(match.zoneKeyId)
        if not zone:
            logging.info('could not find the connected zone')
            return self.render_json_response(
                authorization = True,
                request_successful = False
            )

        ## was the winner the attacker or defender?
        if winning_user.key.id() == zone.userCaptainKeyId:
            logging.info('defender was the winner')

            ## get both users and set active to false.
            previous_defender = ucontroller.get_by_key_id(match.defenderUserKeyId)

            previous_defender.metaGameActive = False
            ucontroller.update(previous_defender)

            ## the attacker is not going to get picked up at the season round change step, so do it now.
            taskUrl='/task/user/firebase/update'
            taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': previous_defender.key.id()}, countdown = 2,)

            previous_attacker = ucontroller.get_by_key_id(match.attackerUserKeyId)

            previous_attacker.metaGameActive = False
            ucontroller.update(previous_attacker)

            ## the attacker is not going to get picked up at the season round change step, so do it now.
            taskUrl='/task/user/firebase/update'
            taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': previous_attacker.key.id()}, countdown = 2,)



        else:
            logging.info('attacker was the winner')

            ## change around the keys in the captain's user records.
            previous_controller_user = ucontroller.get_by_key_id(zone.userCaptainKeyId)
            if previous_controller_user:
                logging.info('found previous user record  - cleaning it out')
                previous_controller_user.holdingZoneKeyId = None
                previous_controller_user.holdingZone = False
                previous_controller_user.holdingZoneTitle = None
                ## also set active to false.  We need them to reenable meta mode in-game.
                previous_controller_user.metaGameActive = False
                ucontroller.update(previous_controller_user)

                ## the defender is not going to get picked up at the season round change step, so do it now.
                taskUrl='/task/user/firebase/update'
                taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': previous_controller_user.key.id()}, countdown = 2,)

            winning_user.holdingZoneKeyId = zone.key.id()
            winning_user.holdingZone = True
            winning_user.holdingZoneTitle = zone.title
            ## also set active to false.  We need them to reenable meta mode in-game.
            winning_user.metaGameActive = False
            ucontroller.update(winning_user)

            ## firebase? - just wait until the round is over and do them all




        ## in either case, just store the winning results in the match record so that we can process it when the round ends.
        match.winningUserKeyId = winning_user.key.id()
        match.winningUserTitle = winning_user.title
        match.winningTeamTitle = winning_user.currentTeamTitle
        match.winningFactionKeyId = winning_user.currentFactionKeyId
        match.winningFactionTitle = winning_user.currentFactionTag
        match.winningUetopiaGamePlayerKeyId = winning_user.uetopia_playerKeyId

        match.active = True
        match.verified = True
        match.expired = False

        # save match
        matchController.update(match)


        return self.render_json_response(
            authorization = True,
            request_successful=True
        )
