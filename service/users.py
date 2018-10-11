import endpoints
import logging
import uuid
import urllib
import time
import json
import hashlib
import hmac
import urllib
import httplib
#import httplib2
import datetime
import google.oauth2.id_token
import google.auth.transport.requests
from collections import OrderedDict
from httplib2 import Http
from google.appengine.api import urlfetch
from google.appengine.api import taskqueue
from google.appengine.ext import ndb
from protorpc import remote
from protorpc import messages
from protorpc import message_types
from google.appengine.datastore.datastore_query import Cursor
from oauth2client.contrib.appengine import AppAssertionCredentials
from oauth2client.client import GoogleCredentials
from protorpc import remote
from google.appengine.api import taskqueue

import google.auth.transport.requests
import google.oauth2.id_token
import requests_toolbelt.adapters.appengine

## endpoints v2 wants a "collection" so it can build the openapi files
from api_collection import api_collection

from apps.metagame.controllers.users import UsersController
from apps.metagame.controllers.factions import FactionsController
from apps.metagame.controllers.seasons import SeasonsController
from apps.metagame.models.users import USER_RESOURCE

from configuration import *

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']

class ClientConnectResponse(messages.Message):
    """ a client's data """
    user_id = messages.StringField(1)
    refresh_token = messages.BooleanField(2) ## should we do a refresh and try again?
    response_message = messages.StringField(4)
    custom_title = messages.StringField(5)
    access_token = messages.StringField(6)
    uetopia_connected = messages.BooleanField(7)
    response_successful = messages.BooleanField(50)


@endpoints.api(name="users", version="v1", description="Users API",
               allowed_client_ids=[endpoints.API_EXPLORER_CLIENT_ID, WEB_CLIENT_ID, WEB_CLIENT_AUTOCREATED_BY_GOOGLE],
#               issuers={'firebase': endpoints.Issuer(
#        'https://securetoken.google.com/ue4topia-metagame',
#        'https://www.googleapis.com/service_accounts/v1/metadata/x509/securetoken@system.gserviceaccount.com')}
        )
class UsersApi(remote.Service):
    @endpoints.method(USER_RESOURCE, ClientConnectResponse, path='clientSignIn', http_method='POST', name='client.signin')
    def clientSignIn(self, request):
        """ Connect and verify a user's login token - This is called when a user signs in. """
        logging.info('clientSignIn')

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-metagame-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return ClientConnectResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            response = ClientConnectResponse(
                user_id = None,
                refresh_token = True,
                response_message='Firebase Unauth.',
                response_successful=False
            )
            return response
        else:
            logging.info('claims verified')


            try:
                name = claims['name']
            except:
                name = claims['email']

            ## get this user or create if needed
            uController = UsersController()

            authorized_user = uController.get_by_firebaseUser(claims['user_id'])
            if not authorized_user:
                logging.info('no user record found')

                logging.info('creating new user')

                authorized_user = uController.create(firebaseUser=claims['user_id'],
                                            title = name,
                                            uetopia_connected = False,
                                            admin = False,
                                            metaGameActive = False,
                                            roundActionUsed = False,
                                            currentFactionKeyId = None,
                                            currentFactionTag = None,
                                            currentFactionLead = False,
                                            currentFactionTeamLead = False,
                                            currentTeamKeyId = None,
                                            currentTeamCaptain = False,
                                            holdingZoneKeyId = None,
                                            holdingZone = False,
                                            holdingZoneTitle = None
                                            )

                # push a chat out to discord
                http_auth = Http()
                headers = {"Content-Type": "application/json"}
                URL = ADMIN_DISCORD_WEBHOOK
                message = "%s | %s " % (name, claims['email'])
                discord_data = { "embeds": [{"title": "New User", "url": "https://example.com", "description": message}] }
                data=json.dumps(discord_data)
                resp, content = http_auth.request(URL,
                                  "POST",
                                  data,
                                  headers=headers)

            else:
                logging.info('user found')

            #taskUrl='/task/user/firebase/update'
            #taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': authorized_user.key.id()}, countdown = 2,)

        response = ClientConnectResponse(
            user_id = claims['user_id'],
            uetopia_connected = authorized_user.uetopia_connected,
            response_message='Connected successfully.',
            response_successful=True
        )

        return response

    @endpoints.method(USER_RESOURCE, ClientConnectResponse, path='clientConnect', http_method='POST', name='client.connect')
    def clientConnect(self, request):
        """ Connect and verify a user's login token - This is called when a user loads the website and is already logged in. also sometimes after signing in."""
        logging.info('clientConnect')

        #user = endpoints.get_current_user()
        #logging.info(user)

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-metagame-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return ClientConnectResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            response = ClientConnectResponse(
                user_id = None,
                refresh_token = True,
                response_message='Firebase Unauth.',
                response_successful=False
            )
            return response
        else:
            logging.info('claims verified')


            try:
                name = claims['name']
            except:
                name = claims['email']

            ## get this user
            uController = UsersController()

            authorized_user = uController.get_by_firebaseUser(claims['user_id'])
            if not authorized_user:
                logging.warning('no user record found - this can happen on first sign in')

                response = ClientConnectResponse(
                    user_id = claims['user_id'],
                    uetopia_connected = False,
                    response_message='No user record found',
                    response_successful=False
                )
                ## Users do not get created in this call ever.  It causes occasional duplicates because of the way firebase spams refreshes on the login screen.
                return response
            else:
                logging.info('user found')

        taskUrl='/task/user/firebase/update'
        taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': authorized_user.key.id()}, countdown = 2,)



        response = ClientConnectResponse(
            user_id = claims['user_id'],
            uetopia_connected = authorized_user.uetopia_connected,
            refresh_token = False,
            response_message='Connected successfully.',
            response_successful=True
        )

        return response

    @endpoints.method(USER_RESOURCE, ClientConnectResponse, path='uetopiaValidate', http_method='POST', name='uetopia.validate')
    def uetopiaValidate(self, request):
        """ Validate a user's uetopia security code and connect thier account."""
        logging.info('uetopiaValidate')

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-metagame-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return ClientConnectResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            response = ClientConnectResponse(
                user_id = None,
                refresh_token = True,
                response_message='Firebase Unauth.',
                response_successful=False
            )
            return response

        logging.info('claims verified')


        try:
            name = claims['name']
        except:
            name = claims['email']

        ## get this user
        uController = UsersController()
        factionController = FactionsController()
        seasonController = SeasonsController()

        authorized_user = uController.get_by_firebaseUser(claims['user_id'])
        if not authorized_user:
            logging.warning('no user record found - this can happen on first sign in')

            response = ClientConnectResponse(
                user_id = claims['user_id'],
                uetopia_connected = False,
                response_message='No user record found',
                response_successful=False
            )
            ## Users do not get created in this call ever.  It causes occasional duplicates because of the way firebase spams refreshes on the login screen.
            return response


        logging.info('user found')

        #Set up an API request to the uetopia backend to check this security code
        # we'll be sending the gameKeyId, and the user's security code
        # this security code will be erased regardless of the results of this request, so if it failed, the user must start over with a new code.


        uri = "/api/v1/game/metagame/verify"

        params = OrderedDict([
                  ("nonce", time.time()),
                  ("encryption", "sha512"),
                  ("securityCode", request.security_code )
                  ])

        params = urllib.urlencode(params)

        # Hash the params string to produce the Sign header value
        H = hmac.new(UETOPIA_ASSIGNED_GAME_API_SECRET, digestmod=hashlib.sha512)
        H.update(params)
        sign = H.hexdigest()

        headers = {"Content-type": "application/x-www-form-urlencoded",
                           "Key":UETOPIA_ASSIGNED_GAME_API_KEY,
                           "Sign":sign}

        conn = httplib.HTTPSConnection(UETOPIA_API_URL)

        conn.request("POST", uri, params, headers)
        response = conn.getresponse()

        #logging.info(response.read())

        ## parse the response
        jsonstring = str(response.read())
        logging.info(jsonstring)
        jsonobject = json.loads(jsonstring)

        # do something with the response
        if not jsonobject['request_successful']:
            logging.info('the validation request was unsuccessful')

            response = ClientConnectResponse(
                user_id = claims['user_id'],
                uetopia_connected = False,
                response_message='Verification failed.  %s' %jsonobject['error'],
                response_successful=False
            )

            return response

        logging.info('validation was successful')

        authorized_user.uetopia_connected = True
        authorized_user.uetopia_playerKeyId = jsonobject['player_key_id']

        active_season_key = None
        active_season = seasonController.get_active()
        if active_season:
            logging.info('Active season found')
            active_season_key = active_season.key.id()

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

                    faction.activeSeasonKeyId = active_season_key
                    faction.energy = FACTION_STARTING_ENERGY
                    faction.materials = FACTION_STARTING_MATERIALS
                    faction.control = FACTION_STARTING_CONTROL

                    factionController.update(faction)


                if faction.activeSeasonKeyId != active_season.key.id():
                    ## this should hopefully not happen, keeping it here just in case
                    logging.error('this faction has the wrong season applied.  This should not happen.  Make sure this gets cleared out on season change.')

                    faction.activeSeasonKeyId = active_season_key
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
                    activeSeasonKeyId = active_season_key,
                    energy = FACTION_STARTING_ENERGY,
                    materials = FACTION_STARTING_MATERIALS,
                    control = FACTION_STARTING_CONTROL
                )

            ## with a faction, make sure the user has this faction selected, and there were no changes to the users permissions

            authorized_user.currentFactionKeyId = faction.key.id()
            authorized_user.currentFactionTag = jsonobject['group_tag']
            try:
                authorized_user.currentFactionLead = jsonobject['metagame_faction_lead']
            except:
                authorized_user.currentFactionLead = False

            try:
                authorized_user.currentFactionTeamLead = jsonobject['metagame_team_lead']
            except:
                authorized_user.currentFactionTeamLead = False


        uController.update(authorized_user)

        ## check for team
        if jsonobject['team_key_id']:
            logging.info('found a team')

            ## we want to be able to send back the team captain status so that the JS client can prompt the user to take appropriate actions

        taskUrl='/task/user/firebase/update'
        taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': authorized_user.key.id()}, countdown = 2,)

        response = ClientConnectResponse(
            response_message='Connected successfully.',
            response_successful=True
        )

        return response
