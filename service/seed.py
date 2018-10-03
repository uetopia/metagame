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

from apps.metagame.models.model import *

from apps.metagame.controllers.model import ModelController

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

class ClientConnectResponse(messages.Message):
    """ a client's data """
    user_id = messages.StringField(1)
    refresh_token = messages.BooleanField(2) ## should we do a refresh and try again?
    response_message = messages.StringField(4)
    response_successful = messages.BooleanField(50)

WEB_CLIENT_ID = '104772747241-h9shfplrpu9sktif9tauph2vn3jhu0ca.apps.googleusercontent.com'

@endpoints.api(name="seed", version="v1", description="Seed API",
               allowed_client_ids=[endpoints.API_EXPLORER_CLIENT_ID, WEB_CLIENT_ID])
class Api(remote.Service):
    @endpoints.method(MODEL_RESOURCE, ModelResponse, path='modelCreate', http_method='POST', name='model.create')
    def model_create(self, request):
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

        model=ModelController().create(
        description = request.description,
        name = request.name,
        user_id = claims['user_id']
        )

        credentials = AppAssertionCredentials(
            'https://www.googleapis.com/auth/sqlservice.admin')

        http_auth = credentials.authorize(Http())

        model_json = json.dumps(model.to_json())

        #logging.info(model_json)
        headers = {"Content-Type": "application/json"}

        URL = "https://ue4topia.firebaseio.com/model/%s.json" % model.key.id()
        resp, content = http_auth.request(URL,
                          "PUT", ## Write or replace data to a defined path,
                          model_json,
                          headers=headers)

        #logging.info(resp)
        #logging.info(content)

        return ModelResponse(response_message="Model Created")

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
