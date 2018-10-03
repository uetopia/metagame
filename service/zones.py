import endpoints
import logging
import urllib
import json
import random
import dateutil.parser
from httplib2 import Http
from google.appengine.api import urlfetch
from google.appengine.api import taskqueue
from google.appengine.ext import ndb
from protorpc import remote
from protorpc import message_types
from google.appengine.datastore.datastore_query import Cursor
#from oauth2client.contrib.appengine import AppAssertionCredentials
from oauth2client.client import GoogleCredentials
from protorpc import remote

import google.auth.transport.requests
import google.oauth2.id_token
import requests_toolbelt.adapters.appengine

##from apps.metagame.utilities import firebase_helper

from apps.metagame.models.zones import *
from apps.metagame.models.bids import *

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

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

@endpoints.api(name="zones", version="v1", description="Zones API",
               allowed_client_ids=[endpoints.API_EXPLORER_CLIENT_ID, WEB_CLIENT_ID])
class ZonesApi(remote.Service):
    @endpoints.method(ZONE_RESOURCE, ZoneResponse, path='fill', http_method='POST', name='fill')
    def fill(self, request):
        # Verify Firebase auth.
        #claims = firebase_helper.verify_auth_token(self.request_state)
        id_token = self.request_state.headers['x-metagame-auth'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            ## TODO make this more modular, somehow.  We have no idea who this user is at this point, so can't write to the firebase user record.
            logging.error('Firebase Unauth')
            response = ZoneResponse(
                response_message='Firebase Unauth.',
                response_successful=False
            )
            return response

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return ZoneResponse(response_message='Error: No User Record Found. ', response_successful=False)

        if not authorized_user.admin:
            logging.info('no admin record found')
            return ZoneResponse(response_message='Error: No Admin Record Found. ', response_successful=False)


        ## Look up the map
        mapController = MapsController()
        zoneController = ZonesController()

        map = mapController.get_by_key_id(request.mapKeyId)
        if not map:
            logging.info('map not found by key')
            return ZoneResponse(response_message='Error: No map Found. ', response_successful=False)

        ## keep track of the results so we can push the whole json struct to firebase all at once.
        map_json = {}

        vertical_rows = []

        # loop over the horizontal
        for verticalIndex in range(map.zoneCountVertical):

            logging.info('filling verticalIndex: %s' % verticalIndex)
            horizontal_row = []

            for horizontalIndex in range(map.zoneCountHorizontal):

                logging.info('filling horizontalIndex')

                ## Roll to see which zone should fill here (defined in configuration.py)
                zoneToUse = random.randint(1,100)
                logging.info('random roll: %s' % zoneToUse)

                ## loop over the zonetypes
                for zone_type in ZONE_TYPES:
                    if zone_type['probability'] >= zoneToUse:
                        logging.info('found zone')


                        ## roll for energy, materials, control based on the zone type
                        rand_energy = random.randint(zone_type['energyMin'], zone_type['energyMax'])
                        rand_materials = random.randint(zone_type['materialsMin'], zone_type['materialsMax'])
                        rand_control = random.randint(zone_type['controlMin'], zone_type['controlMax'])

                        zone=zoneController.create(
                            engine_travel_url = zone_type['engine_travel_url'],
                            title = zone_type['title'],
                            mapKeyId = map.key.id(),
                            mapTitle = map.title,
                            seasonKeyId = map.seasonKeyId,
                            seasonTitle = map.seasonTitle,
                            seasonActive = map.seasonActive,
                            regionKeyId = map.regionKeyId,
                            regionTitle = map.regionTitle,
                            regionDatacenterLocation = map.regionDatacenterLocation,
                            horizontalIndex = horizontalIndex,
                            verticalIndex = verticalIndex,
                            energy = rand_energy,
                            materials = rand_materials,
                            control = rand_control,
                            validZone =  zone_type['validZone']
                        )

                        horizontal_row.append(zone.to_json())

                        break

            vertical_rows.append(horizontal_row)


        #credentials = AppAssertionCredentials('https://www.googleapis.com/auth/sqlservice.admin')
        credentials = GoogleCredentials.get_application_default().create_scoped(_FIREBASE_SCOPES)

        http_auth = credentials.authorize(Http())

        map.zones = vertical_rows
        map_json = map.to_json()

        model_json = json.dumps(map_json)

        #logging.info(model_json)
        headers = {"Content-Type": "application/json"}

        URL = "%s/regions/%s/maps/%s.json" % (FIREBASE_DATABASE_ROOT, map.regionKeyId, map.key.id() )
        logging.info(URL)
        resp, content = http_auth.request(URL,
                          "PUT", ## Write or replace data to a defined path,
                          model_json,
                          headers=headers)


        #logging.info(resp)
        #logging.info(content)

        return ZoneResponse(response_message="Map Filled",response_successful=True)

    @endpoints.method(ZONE_COLLECTION_PAGE_RESOURCE, ZoneCollection, path='zoneCollectionGet', http_method='POST', name='collection.get')
    def zoneCollectionGet(self, request):
        """ Get a collection of zones """
        logging.info("zoneCollectionGet")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-metagame-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return ZoneCollection(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return ZoneCollection(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return ZoneCollection(response_message='Error: No User Record Found. ', response_successful=False)

        if not authorized_user.admin:
            logging.info('no admin record found')
            return ZoneCollection(response_message='Error: No Admin Record Found. ', response_successful=False)

        zoneController = ZonesController()

        entities = zoneController.list_by_mapKeyId(request.mapKeyId)
        entity_list = []

        for entity in entities:
            entity_list.append(ZoneResponse(
                key_id = entity.key.id(),
                title = entity.title,
                created = entity.created.isoformat()
            ))

        response = ZoneCollection(
            zones = entity_list,
            response_successful=True
        )

        return response

    @endpoints.method(BID_RESOURCE, BidResponse, path='zoneBid', http_method='POST', name='bid')
    def zoneBid(self, request):
        """ Bid to attack a zone """
        logging.info("zoneBid")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-metagame-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return BidResponse(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return BidResponse(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        userController = UsersController()

        authorized_user = userController.get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return BidResponse(response_message='Error: No User Record Found. ', response_successful=False)

        if not authorized_user.currentFactionTeamLead:
            logging.info('User does not have currentFactionTeamLead permission')
            return BidResponse(response_message='Error: You do not have the Team Lead permission. ', response_successful=False)

        if authorized_user.roundActionUsed:
            logging.info('User has already taken an action this round')
            return BidResponse(response_message='Error: You have already taken an action this round. ', response_successful=False)

        zoneController = ZonesController()
        bidController = BidsController()
        seasonController = SeasonsController()
        factionsController = FactionsController()

        ## check season - make sure positioning is set to true.
        season = seasonController.get_active()
        if not season:
            logging.info('No Active season found')
            return BidResponse(response_message='Error: The active season was not found. ', response_successful=False)

        if not season.currentRoundPositioning:
            logging.info('Positioning is not currently enabled - cannot bid')
            return BidResponse(response_message='Error: Positioning round is not active.  Cannot bid.', response_successful=False)

        zone = zoneController.get_by_key_id(request.zoneKeyId)
        if not zone:
            logging.info('the zone was not found')
            return BidResponse(response_message='Error: The zone was not found. ', response_successful=False)

        ## check min/max
        if request.bidAmount < MINIMUM_BID:
            logging.info('bid below minimum')
            return BidResponse(response_message='Error: The bid was too low. ', response_successful=False)

        if request.bidAmount > MAXIMUM_BID:
            logging.info('bid above maximum')
            return BidResponse(response_message='Error: The bid was too high. ', response_successful=False)

        ## make sure the faction can afford it

        faction = factionsController.get_by_key_id(authorized_user.currentFactionKeyId)
        if not faction:
            logging.info('the faction was not found')
            return BidResponse(response_message='Error: The faction was not found. ', response_successful=False)

        if faction.energy < request.bidAmount:
            logging.info('the faction cannot afford this bid')
            return BidResponse(response_message='Error: The faction cannot afford this bid. ', response_successful=False)

        ## Check to see if this team was previously defending.  If they were, we need to remove them from the defending zone immediately.
        defending_zone = zoneController.get_controlled_by_userCaptainKeyId(authorized_user.key.id())
        if defending_zone:
            logging.info('found a zone that this user/team is defending')
            if defending_zone.key.id() == zone.key.id():
                logging.info('it is the same zone.  This should not happen.  Ignoring')
                return BidResponse(response_message='Error: Cannot bid on a zone that is currently being defended.', response_successful=False)
            else:
                logging.info('This is a different zone.  Moving the team out of the defended zone.')
                defending_zone.controlled = False
                defending_zone.factionKeyId = None
                defending_zone.factionTag = None
                defending_zone.userCaptainKeyId = None
                defending_zone.userCaptainTitle = None
                defending_zone.teamTitle = None

                #save
                zoneController.update(defending_zone)

                ## firebase update?  Can just leave it for the next push I think....


        ## Remove the amount from the faction
        ## TODO - use a more fault tolerant approach for serious projects.
        ## for now just subtracting
        faction.energy = faction.energy - request.bidAmount
        # and since we're about to update the faction anyway, make sure it has the current season key
        faction.activeSeasonKeyId = season.key.id()
        factionsController.update(faction)

        ## record the bid
        bidController.create(
            zoneKeyId = zone.key.id(),
            zoneTitle = zone.title,
            mapKeyId = zone.mapKeyId,
            mapTitle = zone.mapTitle,
            seasonKeyId = season.key.id(),
            seasonTitle = season.title,
            seasonActive = season.active,
            regionKeyId = zone.regionKeyId,
            regionTitle = zone.regionTitle,

            # connections to the user, party and faction
            #teamKeyId = ndb.IntegerProperty(indexed=False)
            #teamTitle = ndb.StringProperty(indexed=False)
            factionKeyId = faction.key.id(),
            factionTitle = faction.tag,
            factionTag = faction.tag,
            userKeyId = authorized_user.key.id(),
            userTitle = authorized_user.title,
            uetopiaGamePlayerKeyId = authorized_user.uetopia_playerKeyId,
            roundIndex = season.currentRound,
            bidAmount = request.bidAmount,
            highBid = False,
            bidProcessed = False,
            bidReturned = False,
        )

        ## update the player - make the bid buttons and "waiting for move" dissapear

        authorized_user.roundActionUsed = True
        userController.update(authorized_user)

        taskUrl='/task/user/firebase/update'
        taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': authorized_user.key.id()}, countdown = 2,)



        response = BidResponse(
            response_message="Bid placed.",
            response_successful=True
        )

        return response


"""
    @endpoints.method(MODEL_RESOURCE, ModelResponse, path='modelUpdate', http_method='POST', name='model.update')
    def modelUpdate(self, request):
        logging.info('modelUpdate')
        # Verify Firebase auth.
        #claims = firebase_helper.verify_auth_token(self.request_state)
        id_token = self.request_state.headers['x-metagame-auth'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            ## TODO make this more modular, somehow.  We have no idea who this user is at this point, so can't write to the firebase user record.
            logging.error('Firebase Unauth')
            response = ModelResponse(
                response_message='Firebase Unauth.',
                response_successful=False
            )
            return response

        ## get the model

        modelController = ModelController()

        model=modelController.get_by_key_id(int(request.key_id))
        if not model:
            logging.error('model not found')
            return ModelResponse(response_message="Model Not Found", response_successful=False)

        model.name = request.name
        model.description = request.description
        modelController.update(model)

        credentials = AppAssertionCredentials(
            'https://www.googleapis.com/auth/sqlservice.admin')

        http_auth = credentials.authorize(Http())

        model_json = json.dumps(model.to_json())

        logging.info(model_json)
        headers = {"Content-Type": "application/json"}

        URL = "https://ue4topia.firebaseio.com/model/%s.json" % model.key.id()
        resp, content = http_auth.request(URL,
                          "PUT", ## Write or replace data to a defined path,
                          model_json,
                          headers=headers)

        logging.info(resp)
        logging.info(content)

        return ModelResponse(response_message="Model Updated")

    @endpoints.method(MODEL_RESOURCE, ModelResponse, path='modelDelete', http_method='POST', name='model.delete')
    def modelDelete(self, request):
        logging.info('modelDelete')
        # Verify Firebase auth.
        #claims = firebase_helper.verify_auth_token(self.request_state)
        id_token = self.request_state.headers['x-metagame-auth'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            ## TODO make this more modular, somehow.  We have no idea who this user is at this point, so can't write to the firebase user record.
            logging.error('Firebase Unauth')
            response = ModelResponse(
                #models = None,
                more = None,
                cursor = None,
                response_message='Firebase Unauth.',
                response_successful=False
            )
            return response

        ## get the model

        modelController = ModelController()

        model=modelController.get_by_key_id(int(request.key_id))
        if not model:
            logging.error('model not found')
            return ModelResponse(response_message="Model Not Found", response_successful=False)

        modelController.delete(model)

        credentials = AppAssertionCredentials(
            'https://www.googleapis.com/auth/sqlservice.admin')

        http_auth = credentials.authorize(Http())

        model_json = json.dumps(model.to_json())

        logging.info(model_json)
        headers = {"Content-Type": "application/json"}

        URL = "https://ue4topia.firebaseio.com/model/%s.json" % model.key.id()
        resp, content = http_auth.request(URL,
                          "DELETE", ## We can delete data with a DELETE request
                          model_json,
                          headers=headers)

        logging.info(resp)
        logging.info(content)

        return ModelResponse(response_message="Model Deleted")
"""
