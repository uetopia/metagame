import endpoints
import logging
import urllib
import json
import dateutil.parser
from httplib2 import Http
from google.appengine.api import urlfetch
from google.appengine.api import taskqueue
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

from apps.metagame.models.seasons import *

from apps.metagame.controllers.seasons import SeasonsController
from apps.metagame.controllers.users import UsersController

from configuration import *

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

@endpoints.api(name="seasons", version="v1", description="Seasons API",
               allowed_client_ids=[endpoints.API_EXPLORER_CLIENT_ID, WEB_CLIENT_ID])
class SeasonsApi(remote.Service):
    @endpoints.method(SEASON_RESOURCE, SeasonResponse, path='create', http_method='POST', name='create')
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
            return SeasonResponse(response_message='Error: No User Record Found. ', response_successful=False)

        if not authorized_user.admin:
            logging.info('no admin record found')
            return SeasonResponse(response_message='Error: No Admin Record Found. ', response_successful=False)


        startdate = dateutil.parser.parse(request.starts)
        enddate = dateutil.parser.parse(request.ends)

        season=SeasonsController().create(
            description = request.description,
            title = request.title,
            starts = startdate,
            ends = enddate,
            active = request.active,
            currentRound = 0,
            currentRoundPositioning = True,
            currentRoundCombat = False,
            currentRoundResults = False
        )

        ## we need this on firebase to show the current state of the season.
        if request.active:
            taskUrl='/task/season/firebase/update'
            taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': season.key.id()}, countdown = 2,)


            if AUTOMATIC_PHASE_CHANGE:
                ## requeue the task based on settings in config
                logging.info('starting phase change task')

                taskUrl='/task/season/stage_change'
                taskqueue.add(url=taskUrl, queue_name='seasonStageChange', countdown = ROUND_DURATION_POSITIONING,)

        return SeasonResponse(response_message="Season Created",response_successful=True)

    @endpoints.method(SEASON_COLLECTION_PAGE_RESOURCE, SeasonCollection, path='collectionGet', http_method='POST', name='collection.get')
    def collectionGet(self, request):
        """ Get a collection of zones """
        logging.info("season CollectionGet")

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

        seasonController = SeasonsController()

        entities = seasonController.list()
        entity_list = []

        for entity in entities:
            entity_list.append(SeasonResponse(
                key_id = entity.key.id(),
                title = entity.title,
                created = entity.created.isoformat()
            ))

        response = SeasonCollection(
            seasons = entity_list,
            response_successful=True
        )

        return response

    @endpoints.method(SEASON_RESOURCE, SeasonResponse, path='get', http_method='POST', name='get')
    def get(self, request):
        logging.info('get')
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
            return SeasonResponse(response_message='Error: No User Record Found. ', response_successful=False)

        if not authorized_user.admin:
            logging.info('no admin record found')
            return SeasonResponse(response_message='Error: No Admin Record Found. ', response_successful=False)

        ## get the model

        seasonController = SeasonsController()

        season=seasonController.get_by_key_id(int(request.key_id))
        if not season:
            logging.error('season not found')
            return SeasonResponse(response_message="Season Not Found", response_successful=False)

        return SeasonResponse(
            key_id = season.key.id(),
            title = season.title,
            description = season.description,
            starts = season.starts.isoformat(),
            ends = season.ends.isoformat(),
            active = season.active,
            closing = season.closing,
            next = season.next,
            currentRound = season.currentRound,
            currentRoundPositioning = season.currentRoundPositioning,
            currentRoundCombat = season.currentRoundCombat,
            currentRoundResults = season.currentRoundResults,
            response_message="Season Updated")


    @endpoints.method(SEASON_RESOURCE, SeasonResponse, path='update', http_method='POST', name='update')
    def update(self, request):
        logging.info('update')
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
            return SeasonResponse(response_message='Error: No User Record Found. ', response_successful=False)

        if not authorized_user.admin:
            logging.info('no admin record found')
            return SeasonResponse(response_message='Error: No Admin Record Found. ', response_successful=False)

        startdate = dateutil.parser.parse(request.starts)
        enddate = dateutil.parser.parse(request.ends)

        ## get the model

        seasonController = SeasonsController()

        season=seasonController.get_by_key_id(int(request.key_id))
        if not season:
            logging.error('season not found')
            return SeasonResponse(response_message="Season Not Found", response_successful=False)

        season.description = request.description
        season.title = request.title
        season.starts = startdate
        season.ends = enddate
        season.active = request.active
        season.closing = request.closing
        season.next = request.next
        season.currentRound = request.currentRound
        season.currentRoundPositioning = request.currentRoundPositioning
        season.currentRoundCombat = request.currentRoundCombat
        season.currentRoundResults = request.currentRoundResults

        seasonController.update(season)

        if request.active:
            taskUrl='/task/season/firebase/update'
            taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': season.key.id()}, countdown = 2,)

        return SeasonResponse(response_message="Season Updated")
"""
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
