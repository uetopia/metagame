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
from google.appengine.api import taskqueue

import google.auth.transport.requests
import google.oauth2.id_token
import requests_toolbelt.adapters.appengine

##from apps.metagame.utilities import firebase_helper

from apps.metagame.models.mm_match import *
from apps.metagame.models.mm_match_character import *

from apps.metagame.controllers.mm_match import MMMatchController
from apps.metagame.controllers.users import UsersController
from apps.metagame.controllers.mm_match_character import MMMatchCharacterController

from configuration import *

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

@endpoints.api(name="matches", version="v1", description="Matches API",
               allowed_client_ids=[endpoints.API_EXPLORER_CLIENT_ID, WEB_CLIENT_ID])
class MatchesApi(remote.Service):
    @endpoints.method(MMMATCH_COLLECTION_PAGE_RESOURCE, MMMatchCollection, path='mmmatchCollectionGet', http_method='POST', name='collection.get')
    def mmmatchCollectionGet(self, request):
        """ Get a collection of mmmatches """
        logging.info("mmmatchCollectionGet")

        matchController = MMMatchController()

        entities = matchController.list()
        entity_list = []

        for entity in entities:
            entity_list.append(MMMatchResponse(
                key_id = entity.key.id(),
                title = entity.title,
                winningTeamTitle = entity.winningTeamTitle,
                losingTeamTitle = entity.losingTeamTitle,
                regionDatacenterLocation = entity.regionDatacenterLocation
            ))

        response = MMMatchCollection(
            mm_matches = entity_list,
            response_successful=True
        )

        return response


    @endpoints.method(MMMATCH_RESOURCE, MMMatchResponse, path='get', http_method='POST', name='get')
    def get(self, request):
        logging.info('get')

        ## No auth required

        ## get the model

        matchController = MMMatchController()
        mm_MatchCharacterController = MMMatchCharacterController()

        match=matchController.get_by_key_id(int(request.key_id))
        if not match:
            logging.error('match not found')
            return MMMatchResponse(response_message="Match Not Found", response_successful=False)

        ## get the mm_match_characters too
        characterList = mm_MatchCharacterController.list_by_mmmatchKeyId(match.key.id())

        winningTeam = []
        losingTeam = []

        for character in characterList:
            logging.info('found character')
            # build the response
            tempCharResponse = MMMatchCharacterResponse(
                key_id = character.key.id(),
                characterKeyId = character.characterKeyId,
                title = character.title,
                damage_dealt = character.damage_dealt,
                damage_received = character.damage_received,
                kills = character.kills,
                assists = character.assists,
                deaths = character.deaths,
                rank = character.rank,
                score = character.score,
                level = character.level
            )
            if character.matches_won:
                logging.info('winner')
                winningTeam.append(tempCharResponse)
            else:
                logging.info('loser')
                losingTeam.append(tempCharResponse)


        return MMMatchResponse(
            key_id = match.key.id(),
            title = match.title,
            description = match.description,
            matchType = match.matchType,
            mapTitle = match.mapTitle,
            uetopiaMatchKeyId = match.uetopiaMatchKeyId,
            seasonKeyId = match.seasonKeyId,
            seasonTitle = match.seasonTitle,
            regionDatacenterLocation = match.regionDatacenterLocation,
            winningTeamTitle = match.winningTeamTitle,
            losingTeamTitle = match.losingTeamTitle,
            created = match.created.isoformat(),
            winningTeam = winningTeam,
            losingTeam = losingTeam,
            response_message="Match Found")

    @endpoints.method(MMMATCH_CHARACTER_COLLECTION_PAGE_RESOURCE, MMMatchCharacterCollection, path='mmmatchCharacterCollectionGet', http_method='POST', name='collection.character.get')
    def mmmatchCharacterCollectionGet(self, request):
        """ Get a collection of mmmatch characters """
        logging.info("mmmatchCharacterCollectionGet")

        mm_MatchCharacterController = MMMatchCharacterController()

        entities = mm_MatchCharacterController.list_recent_by_characterKeyId(int(request.characterKeyId))
        entity_list = []

        for entity in entities:
            entity_list.append(MMMatchCharacterResponse(
                key_id = entity.key.id(),
                title = entity.title,
                mapTitle = entity.mapTitle,
                matchType = entity.matchType,
                mmmatchKeyId = entity.mmmatchKeyId,
                mmmatchTitle = entity.mmmatchTitle,
                matches_won = entity.matches_won
            ))

        response = MMMatchCharacterCollection(
            mm_match_characters = entity_list,
            response_successful=True
        )

        return response
