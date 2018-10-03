import endpoints
import logging
import urllib
import json
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

from apps.metagame.models.regions import *

from apps.metagame.controllers.regions import RegionsController
from apps.metagame.controllers.users import UsersController

from configuration import *

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

@endpoints.api(name="regions", version="v1", description="Regions API",
               allowed_client_ids=[endpoints.API_EXPLORER_CLIENT_ID, WEB_CLIENT_ID])
class RegionsApi(remote.Service):
    @endpoints.method(REGION_RESOURCE, RegionResponse, path='create', http_method='POST', name='create')
    def create(self, request):
        # Verify Firebase auth.
        #claims = firebase_helper.verify_auth_token(self.request_state)
        id_token = self.request_state.headers['x-metagame-auth'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            ## TODO make this more modular, somehow.  We have no idea who this user is at this point, so can't write to the firebase user record.
            logging.error('Firebase Unauth')
            response = RegionResponse(
                response_message='Firebase Unauth.',
                response_successful=False
            )
            return response

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return SeasonResponse(response_message='Error: No User Record Found. ', response_successful=False)

        if not authorized_user.admin:
            logging.info('no admin record found')
            return SeasonResponse(response_message='Error: No Admin Record Found. ', response_successful=False)


        region=RegionsController().create(
            description = request.description,
            title = request.title,
            datacenter_location = request.datacenter_location
        )

        """
        credentials = AppAssertionCredentials(
            'https://www.googleapis.com/auth/sqlservice.admin')

        http_auth = credentials.authorize(Http())

        model_json = json.dumps(region.to_json())

        #logging.info(model_json)
        headers = {"Content-Type": "application/json"}

        URL = "%s/regions/%s.json" % (FIREBASE_DATABASE_ROOT, region.key.id() )
        logging.info(URL)
        resp, content = http_auth.request(URL,
                          "PUT", ## Write or replace data to a defined path,
                          model_json,
                          headers=headers)
        """

        #logging.info(resp)
        #logging.info(content)

        return RegionResponse(response_message="Region Created",response_successful=True)

    @endpoints.method(REGION_COLLECTION_PAGE_RESOURCE, RegionCollection, path='regionCollectionGet', http_method='POST', name='collection.get')
    def regionCollectionGet(self, request):
        """ Get a collection of regions """
        logging.info("regionCollectionGet")

        """
        ## No auth needed for this.

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-metagame-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return RegionCollection(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return RegionCollection(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return RegionCollection(response_message='Error: No User Record Found. ', response_successful=False)

        if not authorized_user.admin:
            logging.info('no admin record found')
            return RegionCollection(response_message='Error: No Admin Record Found. ', response_successful=False)

        """

        regionController = RegionsController()

        entities = regionController.list()
        entity_list = []

        for entity in entities:
            entity_list.append(RegionResponse(
                key_id = entity.key.id(),
                title = entity.title
            ))

        response = RegionCollection(
            regions = entity_list,
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
