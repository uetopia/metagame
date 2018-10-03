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

from configuration import *

class playerStartMetaGameHandler(BaseHandler):
    def post(self):
        """
        Recieve Notification when a player starts meta game mode
        Requires http headers:  Key, Sign
        Requires POST parameters:  nonce, securityCode
        """

        ucontroller = UsersController()
        seasonsController = SeasonsController()
        factionController = FactionsController()


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

        ## we need the active season too
        active_season = seasonsController.get_active()
        if not active_season:
            logging.info('active_season was not found.')
            return self.render_json_response(
                authorization = True,
                request_successful = False
            )

        ## grab information about the group and team
        if 'group_key_id' in jsonobject:
            logging.info('Found group_key_id in json')

            ## make sure we have this group/faction in the database already.
            faction = factionController.get_by_uetopia_groupKeyId(jsonobject['group_key_id'])
            if faction:
                logging.info('found an existing faction')

                ## check to see if the faction is in the active semester
                if not faction.activeSeasonKeyId:
                    logging.info('this faction has not been active in the current semester yet.  Setting defaults')

                    faction.activeSeasonKeyId = active_season.key.id()
                    faction.energy = FACTION_STARTING_ENERGY
                    faction.materials = FACTION_STARTING_MATERIALS
                    faction.control = FACTION_STARTING_CONTROL

                    factionController.update(faction)


                if faction.activeSeasonKeyId != active_season.key.id():
                    ## this should hopefully not happen, keeping it here just in case
                    logging.error('this faction has the wrong season applied.  This should not happen.  Make sure this gets cleared out on season change.')

                    faction.activeSeasonKeyId = active_season.key.id()
                    faction.energy = FACTION_STARTING_ENERGY
                    faction.materials = FACTION_STARTING_MATERIALS
                    faction.control = FACTION_STARTING_CONTROL

                    factionController.update(faction)

            else:
                logging.info('faction not found - adding it')

                faction = factionController.create(
                    tag = jsonobject['group_tag'],
                    #title = ndb.StringProperty(indexed=False)
                    #description = ndb.TextProperty(indexed=False)
                    uetopia_groupKeyId = jsonobject['group_key_id'],
                    activeSeasonKeyId = active_season.key.id(),
                    energy = FACTION_STARTING_ENERGY,
                    materials = FACTION_STARTING_MATERIALS,
                    control = FACTION_STARTING_CONTROL
                )

            ## with a faction, make sure the user has this faction selected, and there were no changes to the users permissions

            user.currentFactionKeyId = faction.key.id()
            user.currentFactionTag = jsonobject['group_tag']
            user.currentFactionLead = jsonobject['metagame_faction_lead']
            user.currentFactionTeamLead = jsonobject['metagame_team_lead']

        if 'team_key_id' in jsonobject:
            logging.info('Found team_key_id in json')

            user.currentTeamKeyId = jsonobject['team_key_id']
            user.currentTeamCaptain = jsonobject['team_captain']

        ## update the user record.
        user.metaGameActive = True
        ucontroller.update(user)

        ## push out to firebase
        taskUrl='/task/user/firebase/update'
        taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': user.key.id()}, countdown = 2,)

        ## return status success so that uetopia knows the call worked.

        ## TODO - anything else we need to send back to the uetopia backend at this stage?
        ## custom json probably...

        return self.render_json_response(
            authorization = True,
            request_successful=True
        )
