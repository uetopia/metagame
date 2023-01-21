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

from apps.metagame.models.characters import *

from apps.metagame.controllers.characters import CharactersController
from apps.metagame.controllers.season_characters import SeasonCharactersController
from apps.metagame.controllers.users import UsersController
from apps.metagame.controllers.seasons import SeasonsController

from configuration import *

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

@endpoints.api(name="characters", version="v1", description="Characters API",
               allowed_client_ids=[endpoints.API_EXPLORER_CLIENT_ID, WEB_CLIENT_ID])
class CharactersApi(remote.Service):
    @endpoints.method(CHARACTER_RESOURCE, CharacterResponse, path='get', http_method='POST', name='get')
    def get(self, request):
        logging.info('get')

        ## get the model
        characterController = CharactersController()
        seasonsController = SeasonsController()
        seasonCharacterController = SeasonCharactersController()

        character=characterController.get_by_key_id(int(request.key_id))
        if not character:
            logging.error('character not found')
            return CharacterResponse(response_message="Character Not Found", response_successful=False)

        ## get the active season
        active_season = seasonsController.get_active()
        if not active_season:
            logging.info('active_season was not found.')
            return self.render_json_response(
                authorization = True,
                request_successful = False
            )

        ## also send an array with the seasonCharacterKeyIds
        season_character_list = seasonCharacterController.list_by_characterKeyId(character.key.id())

        sc_list = []

        for season_character in season_character_list:
            logging.info('season_character found')
            sc_list.append(SeasonCharacterResponse(
                key_id = season_character.key.id(),
                title = season_character.title,
                seasonKeyId = season_character.seasonKeyId,
                seasonTitle = season_character.seasonTitle,
                damage_dealt = season_character.damage_dealt,
                ## TODO: Insert all of your custom variables.
                damage_received = season_character.damage_received,
                kills = season_character.kills,
                assists = season_character.assists,
                deaths = season_character.deaths,
                rank = season_character.rank,
                score = season_character.score,
                level = season_character.level,
                matches_played = season_character.matches_played,
                mm1v1_played = season_character.mm1v1_played,
                mm2v2_played = season_character.mm2v2_played,
                mm3v3_played = season_character.mm3v3_played,
                mm4v4_played = season_character.mm4v4_played,
                matches_won = season_character.matches_won,
                mm1v1_won = season_character.mm1v1_won,
                mm2v2_won = season_character.mm2v2_won,
                mm3v3_won = season_character.mm3v3_won,
                mm4v4_won = season_character.mm4v4_won
            ))

        return CharacterResponse(
            key_id = character.key.id(),
            title = character.title,
            description = character.description,
            season_characters = sc_list,
            damage_dealt = character.damage_dealt,
            ## TODO: Insert all of your custom variables.
            damage_received = character.damage_received,
            kills = character.kills,
            assists = character.assists,
            deaths = character.deaths,
            rank = character.rank,
            score = character.score,
            level = character.level,
            matches_played = character.matches_played,
            mm1v1_played = character.mm1v1_played,
            mm2v2_played = character.mm2v2_played,
            mm3v3_played = character.mm3v3_played,
            mm4v4_played = character.mm4v4_played,
            matches_won = character.matches_won,
            mm1v1_won = character.mm1v1_won,
            mm2v2_won = character.mm2v2_won,
            mm3v3_won = character.mm3v3_won,
            mm4v4_won = character.mm4v4_won,
            active_season_key_id = active_season.key.id(),
            response_message="Success")
