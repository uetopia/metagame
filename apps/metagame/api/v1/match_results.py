import logging
import datetime
import string
import json
import hashlib
import hmac
import urllib
import httplib
from httplib2 import Http
from google.appengine.api import urlfetch
from google.appengine.api import taskqueue
from apps.handlers import BaseHandler
from apps.metagame.controllers.users import UsersController
from apps.metagame.controllers.seasons import SeasonsController
from apps.metagame.controllers.factions import FactionsController
from apps.metagame.controllers.mm_match import MMMatchController
from apps.metagame.controllers.zones import ZonesController
from apps.metagame.controllers.characters import CharactersController
from apps.metagame.controllers.season_characters import SeasonCharactersController
from apps.metagame.controllers.mm_match_character import MMMatchCharacterController


from configuration import *

class matchResultsHandler(BaseHandler):
    def post(self):
        """
        URL: /api/v1/matchmaker/match_results

        Recieve notification when a regular matchmaker match is complete.
        Requires http headers:  Key, Sign
        Requires POST parameters:  nonce
        """

        ucontroller = UsersController()
        seasonsController = SeasonsController()
        factionController = FactionsController()
        mmmatchController = MMMatchController()
        zonesController = ZonesController()
        characterController = CharactersController()
        seasonCharacterController = SeasonCharactersController()
        mMMatchCharacterController = MMMatchCharacterController()

        ## make sure the API key matches first
        incomingApiKey = self.request.headers['Key']
        if incomingApiKey != UETOPIA_ASSIGNED_GAME_API_KEY:
            logging.info('API key mismatch')
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

        ## make sure we have the match
        if 'matchKeyId' not in jsonobject:
            logging.info('Did not find matchKeyId in json')

            return self.render_json_response(
                authorization = True,
                request_successful = False
            )

        mmmatch = mmmatchController.get_by_uetopiaMatchKeyId(int(jsonobject['matchKeyId'])) #this comes in as a string
        if mmmatch:
            logging.info('mmmatch was found. This means we have a duplicate.  Rejecting it')
            # this can sometimes happen in dev situations where a game does not complete fully
            return self.render_json_response(
                authorization = True,
                request_successful = False
            )

        ## we need the active season too
        ## TODO - maybe let this through for games that have periods with no active season.
        active_season = seasonsController.get_active()
        if not active_season:
            logging.info('active_season was not found.')
            return self.render_json_response(
                authorization = True,
                request_successful = False
            )

        matchstory = ""
        for matchstoryline in jsonobject['matchStoryReadable']:
            matchstory = matchstory + matchstoryline + "<br/>"

        ## we need to create the mmmatch record.
        mmmatch = mmmatchController.create(uetopiaMatchKeyId=int(jsonobject['matchKeyId']),
                                            title = jsonobject['title'],
                                            description = matchstory,
                                            raw_json = jsonstring,
                                            regionDatacenterLocation = jsonobject['region'],
                                            winningTeamTitle = jsonobject['winningTeamTitle'],
                                            losingTeamTitle = jsonobject['losingTeamTitle'],
                                            matchType = jsonobject['gameModeTitle'] or "default",
                                            mapTitle = jsonobject['mapTitle'] or "default",
                                            seasonKeyId = active_season.key.id(),
                                            seasonTitle = active_season.title
                                            )
        ## figure out which kind of match it was

        matches_played = 0
        mm1v1_played = 0
        mm2v2_played = 0
        mm3v3_played = 0
        mm4v4_played = 0

        if jsonobject['gameModeTitle'] == "1v1":
            matches_played = 1
            mm1v1_played = 1
        elif jsonobject['gameModeTitle'] == "2v2":
            matches_played = 1
            mm2v2_played = 1
        elif jsonobject['gameModeTitle'] == "3v3":
            matches_played = 1
            mm3v3_played = 1
        elif jsonobject['gameModeTitle'] == "4v4":
            matches_played = 1
            mm4v4_played = 1

        ## Next parse through the player list data
        ## WE have a list of players, each with it's own statistics for the match.
        for player in jsonobject['players']:
            logging.info('parsing player data')

            ##      Verify user exists, if not...  discard?
            ##          - Since it's not associated with a firebase user, we have no way to keep track of it.
            ##          - maybe send them a drop or something to let them know they need to signup here.

            existing_user = ucontroller.get_by_uetopia_playerKeyId(int(player['gamePlayerKeyId']))
            if existing_user:
                logging.info('found existing user')

                ##      Verify Character exists.  If not create it
                existing_character = characterController.get_by_uetopia_characterKeyId(int(player['characterCurrentKeyId']))

                if not existing_character:
                    logging.info('character was not found - creating it')

                    ## initialize all statistics values.  these will get calculated later in the uer process task
                    existing_character = characterController.create(
                        title = player['characterCurrentTitle'],
                        userKeyId = existing_user.key.id(),
                        uetopia_playerKeyId = int(player['gamePlayerKeyId']),
                        uetopia_characterKeyId = int(player['characterCurrentKeyId']),
                        damage_dealt = 0,
                        ## TODO: Insert all of your custom variables.
                        damage_received = 0,
                        kills = 0,
                        assists = 0,
                        deaths = 0,
                        rank = player['rank'],
                        score = player['score'],
                        level = player['level'],
                        matches_played = 0,
                        mm1v1_played = 0,
                        mm2v2_played = 0,
                        mm3v3_played = 0,
                        mm4v4_played = 0,
                        matches_won = 0,
                        mm1v1_won = 0,
                        mm2v2_won = 0,
                        mm3v3_won = 0,
                        mm4v4_won = 0
                    )

                ##      Verify seasonCharacter exists.  If not create it
                existing_season_character = seasonCharacterController.get_by_characterKeyId_seasonKeyId(existing_character.key.id(), active_season.key.id())

                if not existing_season_character:
                    logging.info('season character was not found - creating it')

                    ## initialize all statistics values.  these will get calculated later in the uer process task
                    existing_season_character = seasonCharacterController.create(
                        title = player['characterCurrentTitle'],
                        userKeyId = existing_user.key.id(),
                        uetopia_playerKeyId = int(player['gamePlayerKeyId']),
                        uetopia_characterKeyId = int(player['characterCurrentKeyId']),
                        characterKeyId = existing_character.key.id(),
                        seasonKeyId = active_season.key.id(),
                        seasonTitle = active_season.title,
                        damage_dealt = 0,
                        ## TODO: Insert all of your custom variables.
                        damage_received = 0,
                        kills = 0,
                        assists = 0,
                        deaths = 0,
                        rank = player['rank'],
                        score = player['score'],
                        level = player['level'],
                        matches_played = 0,
                        mm1v1_played = 0,
                        mm2v2_played = 0,
                        mm3v3_played = 0,
                        mm4v4_played = 0,
                        matches_won = 0,
                        mm1v1_won = 0,
                        mm2v2_won = 0,
                        mm3v3_won = 0,
                        mm4v4_won = 0
                    )




                ##      Save all stats for this seasonCharacter

                ## determine which matchtype if a win
                matches_won = 0
                mm1v1_won = 0
                mm2v2_won = 0
                mm3v3_won = 0
                mm4v4_won = 0

                if player['win']:
                    logging.info('found winning player')

                    matches_won = 1
                    if mm1v1_played:
                        mm1v1_won = 1
                    elif mm2v2_played:
                        mm2v2_won = 1
                    elif mm3v3_played:
                        mm3v3_won = 1
                    elif mm4v4_played:
                        mm4v4_won = 1

                mMMatchCharacterController.create(
                    title = player['userTitle'],
                    userKeyId = existing_user.key.id(),
                    uetopia_playerKeyId = int(player['gamePlayerKeyId']),
                    uetopia_characterKeyId = int(player['characterCurrentKeyId']),
                    characterKeyId = existing_character.key.id(),
                    mmmatchKeyId = mmmatch.key.id(),
                    mmmatchTitle = mmmatch.title,
                    mapTitle = mmmatch.mapTitle,
                    matchType = mmmatch.matchType,
                    seasonKeyId = active_season.key.id(),
                    seasonCharacterKeyId = existing_season_character.key.id(),
                    damage_dealt = int(player['damageDealt']),
                    ## TODO: Insert all of your custom variables.
                    damage_received = int(player['damageRecieved']),
                    kills = player['kills'],
                    assists = player['assists'],
                    deaths = player['deaths'],
                    rank = player['rank'],
                    score = player['score'],
                    level = player['level'],
                    matches_played = matches_played,
                    mm1v1_played = mm1v1_played,
                    mm2v2_played = mm2v2_played,
                    mm3v3_played = mm3v3_played,
                    mm4v4_played = mm4v4_played,
                    matches_won = matches_won,
                    mm1v1_won = mm1v1_won,
                    mm2v2_won = mm2v2_won,
                    mm3v3_won = mm3v3_won,
                    mm4v4_won = mm4v4_won
                )

                ## Start a task to process the character record.
                taskUrl='/task/character/statistics/calculate'
                taskqueue.add(url=taskUrl, queue_name='UserStatisticsCalculate', params={'key_id': existing_character.key.id()}, countdown = 2,)

        else:
            logging.info('Did not find user.  ')


        ##      Start a task to update firebase chars
        ## TODO - put this on a cron job or something.
        taskUrl='/task/characters/firebase/update'
        taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', countdown = 15,)

        ## post a message to discord
        ## TODO customize this for your game and community

        if mmmatch:
            http_auth = Http()
            headers = {"Content-Type": "application/json"}
            URL = MATCH_RESULTS_DISCORD_WEBHOOK
            customTitle = "%s beat %s " % (mmmatch.winningTeamTitle, mmmatch.losingTeamTitle)
            customDescription = "%s : %s : %s" % (mmmatch.matchType, mmmatch.mapTitle, mmmatch.regionDatacenterLocation)

            url = "https://uetopia-metagame.appspot.com/#/matches/%s" % (mmmatch.key.id())

            discord_data = { "embeds": [{"title": customTitle, "url": url, "description": customDescription}] }
            data=json.dumps(discord_data)
            resp, content = http_auth.request(URL,
                              "POST",
                              data,
                              headers=headers)

        return self.render_json_response(
            authorization = True,
            request_successful=True
        )
