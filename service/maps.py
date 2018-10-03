import endpoints
import logging
import urllib
import json
import dateutil.parser
from httplib2 import Http
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
from protorpc import remote
from protorpc import message_types
from google.appengine.datastore.datastore_query import Cursor
from oauth2client.contrib.appengine import AppAssertionCredentials
from protorpc import remote

import google.auth.transport.requests
import google.oauth2.id_token
import requests_toolbelt.adapters.appengine

##from apps.metagame.utilities import firebase_helper

from apps.metagame.models.maps import *

from apps.metagame.controllers.maps import MapsController
from apps.metagame.controllers.seasons import SeasonsController
from apps.metagame.controllers.regions import RegionsController
from apps.metagame.controllers.users import UsersController

from configuration import *

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

@endpoints.api(name="maps", version="v1", description="Maps API",
               allowed_client_ids=[endpoints.API_EXPLORER_CLIENT_ID, WEB_CLIENT_ID])
class MapsApi(remote.Service):
    @endpoints.method(MAP_RESOURCE, MapResponse, path='create', http_method='POST', name='create')
    def create(self, request):
        # Verify Firebase auth.
        #claims = firebase_helper.verify_auth_token(self.request_state)
        id_token = self.request_state.headers['x-metagame-auth'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            ## TODO make this more modular, somehow.  We have no idea who this user is at this point, so can't write to the firebase user record.
            logging.error('Firebase Unauth')
            response = SeasonResponse(
                response_message='Firebase Unauth.',
                response_successful=False
            )
            return response

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return MapResponse(response_message='Error: No User Record Found. ', response_successful=False)

        if not authorized_user.admin:
            logging.info('no admin record found')
            return MapResponse(response_message='Error: No Admin Record Found. ', response_successful=False)

        ## Look up the season and region
        seasonController = SeasonsController()
        regionController = RegionsController()

        season = seasonController.get_by_key_id(request.seasonKeyId)
        if not season:
            logging.info('season not found by key')
            return MapResponse(response_message='Error: No Season Found. ', response_successful=False)

        region = regionController.get_by_key_id(request.regionKeyId)
        if not region:
            logging.info('region not found by key')
            return MapResponse(response_message='Error: No Region Found. ', response_successful=False)


        map=MapsController().create(
            description = request.description,
            title = request.title,
            seasonKeyId = season.key.id(),
            seasonTitle = season.title,
            seasonActive = season.active,
            regionKeyId = region.key.id(),
            regionTitle = region.title,
            regionDatacenterLocation = region.datacenter_location,
            zoneCountHorizontal = request.zoneCountHorizontal,
            zoneCountVertical = request.zoneCountVertical
        )

        """
        credentials = AppAssertionCredentials(
            'https://www.googleapis.com/auth/sqlservice.admin')

        http_auth = credentials.authorize(Http())

        model_json = json.dumps(model.to_json())

        #logging.info(model_json)
        headers = {"Content-Type": "application/json"}

        URL = "https://ue4topia.firebaseio.com/regions/%s.json" % model.key.id()
        resp, content = http_auth.request(URL,
                          "PUT", ## Write or replace data to a defined path,
                          model_json,
                          headers=headers)

        """
        #logging.info(resp)
        #logging.info(content)

        return MapResponse(response_message="Map Created",response_successful=True)

    @endpoints.method(MAP_COLLECTION_PAGE_RESOURCE, MapCollection, path='mapCollectionGet', http_method='POST', name='collection.get')
    def mapCollectionGet(self, request):
        """ Get a collection of maps """
        logging.info("mapCollectionGet")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-metagame-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return MapCollection(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return MapCollection(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return MapCollection(response_message='Error: No User Record Found. ', response_successful=False)

        if not authorized_user.admin:
            logging.info('no admin record found')
            return MapCollection(response_message='Error: No Admin Record Found. ', response_successful=False)

        mapController = MapsController()

        entities = mapController.list_by_regionKeyId(request.regionKeyId)
        entity_list = []

        for entity in entities:
            entity_list.append(MapResponse(
                key_id = entity.key.id(),
                title = entity.title,
                created = entity.created.isoformat()
            ))

        response = MapCollection(
            maps = entity_list,
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
