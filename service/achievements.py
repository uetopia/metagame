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

from apps.metagame.models.achievements import *
from apps.metagame.models.achievement_progress import *
from apps.metagame.models.season_achievement_progress import *

from apps.metagame.controllers.achievements import AchievementsController
from apps.metagame.controllers.achievement_progress import AchievementProgressController
from apps.metagame.controllers.season_achievement_progress import SeasonAchievementProgressController
from apps.metagame.controllers.users import UsersController

from configuration import *

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

@endpoints.api(name="achievements", version="v1", description="Achievements API",
               allowed_client_ids=[endpoints.API_EXPLORER_CLIENT_ID, WEB_CLIENT_ID])
class AchievementsApi(remote.Service):
    @endpoints.method(ACHIEVEMENT_RESOURCE, AchievementResponse, path='create', http_method='POST', name='create')
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
            return AchievementResponse(response_message='Error: No User Record Found. ', response_successful=False)

        if not authorized_user.admin:
            logging.info('no admin record found')
            return AchievementResponse(response_message='Error: No Admin Record Found. ', response_successful=False)

        ## hidden setting to null instead of false
        if request.hidden:
            ach_hidden = True
        else:
            ach_hidden = False

        achievement=AchievementsController().create(
            description = request.description,
            title = request.title,
            iconUrl = request.iconUrl,
            drop_json = request.drop_json,
            drop_tier = request.drop_tier,
            calculation = request.calculation,
            calculation_int = request.calculation_int,
            seasonal = request.seasonal,
            unknown = request.unknown,
            hidden = ach_hidden,
            do_drop = request.do_drop,
            world_first_awarded = False,
            execute_per_match = request.execute_per_match,
            execute_all_matches = request.execute_all_matches
        )

        ## TODO we need this on firebase to show the current state of the season.
        #if request.active:
        #    taskUrl='/task/season/firebase/update'
        #    taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': season.key.id()}, countdown = 2,)

        return AchievementResponse(response_message="Achievement Created",response_successful=True)

    @endpoints.method(ACHIEVEMENT_COLLECTION_PAGE_RESOURCE, AchievementCollection, path='collectionGet', http_method='POST', name='collection.get')
    def collectionGet(self, request):
        """ Get a collection of Achievements """
        logging.info("Achievement CollectionGet")

        # Verify Firebase auth.
        #logging.info(self.request_state)
        try:
            id_token = self.request_state.headers['x-metagame-auth'].split(' ').pop()
        except:
            logging.error('Missing JWT')
            return AchievementCollection(response_message='Error: Authentication Token Missing.', response_successful=False)

        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            logging.error('Firebase Unauth')
            return AchievementCollection(response_message='Error: Firebase Authentication Missing.', response_successful=False)

        authorized_user = UsersController().get_by_firebaseUser(claims['user_id'])

        if not authorized_user:
            logging.info('no user record found')
            return AchievementCollection(response_message='Error: No User Record Found. ', response_successful=False)

        if not authorized_user.admin:
            logging.info('no admin record found')
            return AchievementCollection(response_message='Error: No Admin Record Found. ', response_successful=False)

        achievementController = AchievementsController()

        entities = achievementController.list()
        entity_list = []

        for entity in entities:
            entity_list.append(AchievementResponse(
                key_id = entity.key.id(),
                title = entity.title,
                iconUrl = entity.iconUrl,
                seasonal = entity.seasonal
            ))

        response = AchievementCollection(
            achievements = entity_list,
            response_successful=True
        )

        return response

    @endpoints.method(ACHIEVEMENT_RESOURCE, AchievementResponse, path='get', http_method='POST', name='get')
    def get(self, request):
        logging.info('Achievement get')
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

        achievementController = AchievementsController()

        achievement=achievementController.get_by_key_id(int(request.key_id))
        if not achievement:
            logging.error('achievement not found')
            return SeasonResponse(response_message="achievement Not Found", response_successful=False)

        ## hidden setting to null instead of false
        if achievement.hidden:
            ach_hidden = True
        else:
            ach_hidden = False

        return AchievementResponse(
            key_id = achievement.key.id(),
            title = achievement.title,
            description = achievement.description,
            iconUrl = achievement.iconUrl,
            drop_json = achievement.drop_json,
            drop_tier = achievement.drop_tier,
            calculation = achievement.calculation,
            calculation_int = achievement.calculation_int,
            seasonal = achievement.seasonal,
            unknown = achievement.unknown,
            hidden = ach_hidden,
            do_drop = achievement.do_drop,
            execute_per_match = achievement.execute_per_match,
            execute_all_matches = achievement.execute_all_matches,
            response_message="Achievement Found")


    @endpoints.method(ACHIEVEMENT_RESOURCE, AchievementResponse, path='update', http_method='POST', name='update')
    def update(self, request):
        logging.info('Achievement update')
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

        achievementController = AchievementsController()

        achievement=achievementController.get_by_key_id(int(request.key_id))
        if not achievement:
            logging.error('achievement not found')
            return SeasonResponse(response_message="achievement Not Found", response_successful=False)

        ## hidden setting to null instead of false
        if request.hidden:
            ach_hidden = True
        else:
            ach_hidden = False

        achievement.description = request.description
        achievement.title = request.title
        achievement.iconUrl = request.iconUrl
        achievement.drop_json = request.drop_json
        achievement.drop_tier = request.drop_tier
        achievement.calculation = request.calculation
        achievement.calculation_int = request.calculation_int
        achievement.seasonal = request.seasonal
        achievement.unknown = request.unknown
        achievement.hidden = ach_hidden
        achievement.do_drop = request.do_drop
        achievement.execute_per_match = request.execute_per_match
        achievement.execute_all_matches = request.execute_all_matches

        achievementController.update(achievement)

        ## do we want this on firebase?  Won't change all that much.
        #if request.active:
        #    taskUrl='/task/season/firebase/update'
        #    taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': season.key.id()}, countdown = 2,)

        return AchievementResponse(response_message="Achievement Updated")


    @endpoints.method(ACHIEVEMENT_PROGRESS_COLLECTION_PAGE_RESOURCE, AchievementProgressCollection, path='progressCollectionGet', http_method='POST', name='progress.collection.get')
    def progressCollectionGet(self, request):
        """ Get a collection of Achievement progresses """
        logging.info("Achievement progressCollectionGet")

        # Public - No auth

        #achievementController = AchievementsController()
        achievementProgressController = AchievementProgressController()
        #seasonAchievementProgressController = SeasonAchievementProgressController()

        if request.earned:
            entities = achievementProgressController.list_by_characterKeyId_earned_not_hidden(int(request.characterKeyId))
        elif request.awarded:
            entities = achievementProgressController.list_by_characterKeyId_awarded_not_hidden(int(request.characterKeyId))
        else:
            entities = achievementProgressController.list_by_characterKeyId(int(request.characterKeyId))

        entity_list = []

        for entity in entities:
            entity_list.append(AchievementProgressResponse(
                key_id = entity.key.id(),
                title = entity.title,
                iconUrl = entity.iconUrl,
                first = entity.first
            ))

        response = AchievementProgressCollection(
            achievement_progrogresses = entity_list,
            response_successful=True
        )

        return response

    @endpoints.method(ACHIEVEMENT_SEASON_PROGRESS_COLLECTION_PAGE_RESOURCE, AchievementSeasonProgressCollection, path='seasonProgressCollectionGet', http_method='POST', name='season.progress.collection.get')
    def seasonProgressCollectionGet(self, request):
        """ Get a collection of Season Achievement progresses """
        logging.info("Achievement seasonProgressCollectionGet")

        # Public - No auth

        #achievementController = AchievementsController()
        #achievementProgressController = AchievementProgressController()
        seasonAchievementProgressController = SeasonAchievementProgressController()

        if request.earned:
            entities = seasonAchievementProgressController.list_by_characterKeyId_seasonKeyId_earned_not_hidden(int(request.characterKeyId), int(request.seasonKeyId))
        elif request.awarded:
            entities = seasonAchievementProgressController.list_by_characterKeyId_seasonKeyId_awarded_not_hidden(int(request.characterKeyId), int(request.seasonKeyId))
        else:
            entities = seasonAchievementProgressController.list_by_characterKeyId_seasonKeyId(int(request.characterKeyId), int(request.seasonKeyId))

        entity_list = []

        for entity in entities:
            entity_list.append(AchievementSeasonProgressResponse(
                key_id = entity.key.id(),
                title = entity.title,
                iconUrl = entity.iconUrl,
                season_first = entity.season_first
            ))

        response = AchievementSeasonProgressCollection(
            achievement_progrogresses = entity_list,
            response_successful=True
        )

        return response
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
