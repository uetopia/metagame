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
from httplib2 import Http
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
from protorpc import remote
from protorpc import message_types
from google.appengine.datastore.datastore_query import Cursor
from oauth2client.contrib.appengine import AppAssertionCredentials
from oauth2client.client import GoogleCredentials
from protorpc import remote
from google.appengine.api import taskqueue

from apps.handlers import BaseHandler

from apps.metagame.controllers.users import UsersController
from apps.metagame.controllers.seasons import SeasonsController
from apps.metagame.controllers.characters import CharactersController
from apps.metagame.controllers.season_characters import SeasonCharactersController
from apps.metagame.controllers.mm_match_character import MMMatchCharacterController
from apps.metagame.controllers.mm_match import MMMatchController
from apps.metagame.controllers.achievements import AchievementsController
from apps.metagame.controllers.achievement_progress import AchievementProgressController
from apps.metagame.controllers.season_achievement_progress import SeasonAchievementProgressController

from apps.metagame.calculations.achievement_match import *

from configuration import *

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']

class AchievementEarnedProcessHandler(BaseHandler):
    """ /task/character/achievement/process """

    def get(self):
        return self.post()

    def post(self):
        logging.info("[TASK] AchievementEarnedProcessHandler")

        key_id = self.request.get('key_id') ## this is a characterKeyId

        seasonsController = SeasonsController()
        ucontroller = UsersController()
        mmmatchController = MMMatchController()
        characterController = CharactersController()
        seasonCharacterController = SeasonCharactersController()
        mMMatchCharacterController = MMMatchCharacterController()
        achievementController = AchievementsController()
        achievementProgressController = AchievementProgressController()
        seasonAchievementProgressController = SeasonAchievementProgressController()

        character = characterController.get_by_key_id(int(key_id))
        if not character:
            logging.error('character not found')
            return

        ## get the active season
        active_season = seasonsController.get_active()
        if not active_season:
            logging.info('active_season was not found.')
            return self.render_json_response(
                authorization = True,
                request_successful = False
            )

        ## get the non-seasonal achievement progress for this char
        ## we want only earned but not awarded
        achievement_progresses = achievementProgressController.list_by_characterKeyId_earned(character.key.id())

        for achievement in achievement_progresses:
            logging.info('checking regular achievement')

            achievement.awarded = True


            # get the achievement record
            ach = achievementController.get_by_key_id(achievement.achievementKeyId)

            if ach:
                if ach.do_drop:
                    logging.info('doing drop')

                    uri = "/api/v1/game/player/%s/drops/create" % character.uetopia_playerKeyId

                    json_values = ({
                        u'nonce': time.time(),
                        u'encryption': "sha512",
                        u'title': ach.title,
                        u'description': ach.description,
                        u'uiIcon': ach.iconUrl,
                        # u'data': json.dumps(json.load(ach.drop_json)), # do we need the load/dump?
                        u'data': ach.drop_json,
                        u'Tier': ach.drop_tier
                        })

                    entity_json = json.dumps(json_values)


                    # Hash the params string to produce the Sign header value
                    H = hmac.new(UETOPIA_ASSIGNED_GAME_API_SECRET, digestmod=hashlib.sha512)
                    H.update(entity_json)
                    sign = H.hexdigest()

                    headers = {"Content-type": "application/x-www-form-urlencoded",
                                       "Key":UETOPIA_ASSIGNED_GAME_API_KEY,
                                       "Sign":sign}

                    conn = httplib.HTTPSConnection(UETOPIA_API_URL)

                    conn.request("POST", uri, entity_json, headers)
                    response = conn.getresponse()

                    #logging.info(response.read())

                    ## parse the response
                    jsonstring = str(response.read())
                    logging.info(jsonstring)
                    jsonobject = json.loads(jsonstring)

                    # do something with the response?
                    if not jsonobject['request_successful']:
                        logging.info('the request was unsuccessful')

                    logging.info('request was successful')

            achievementProgressController.update(achievement)

            # push a chat out to discord - only if not hidden
            ## TODO Customize this for your game and community
            if not achievement.hidden:
                http_auth = Http()
                headers = {"Content-Type": "application/json"}
                URL = ACHIEVEMENT_DISCORD_WEBHOOK
                message = "%s : %s " % (character.title, achievement.description)
                url = "https://uetopia-metagame.appspot.com/#/characters/%s" % (character.key.id())

                if achievement.first:
                    msg_title = "WORLD FIRST: " + achievement.title
                elif achievement.season_first:
                    msg_title = "SEASON FIRST: " + achievement.title
                else:
                    msg_title = achievement.title

                discord_data = { "embeds": [{"title": msg_title, "url": url, "description": message}] }
                data=json.dumps(discord_data)
                resp, content = http_auth.request(URL,
                                  "POST",
                                  data,
                                  headers=headers)



        ## Get the active season character
        season_character = seasonCharacterController.get_by_characterKeyId_seasonKeyId(character.key.id(), active_season.key.id())

        if season_character:
            logging.info('season character found')

            ## get the seasonal achievement progress for this SEASON char
            ## only get earned.
            season_achievement_progresses = seasonAchievementProgressController.list_by_characterKeyId_seasonKeyId_earned(character.key.id(), active_season.key.id())


            for achievement in season_achievement_progresses:
                logging.info('checking seasonal achievement')


                achievement.awarded = True
                seasonAchievementProgressController.update(achievement)

                # get the achievement record
                ach = achievementController.get_by_key_id(achievement.achievementKeyId)

                if ach:
                    if ach.do_drop:
                        logging.info('doing drop')

                        uri = "/api/v1/game/player/%s/drops/create" % character.uetopia_playerKeyId

                        json_values = ({
                            u'nonce': time.time(),
                            u'encryption': "sha512",
                            u'title': achievement.title,
                            u'description': achievement.description,
                            u'uiIcon': ach.iconUrl,
                            u'data': json.dumps(ach.drop_json),
                            u'Tier': ach.drop_tier
                            })

                        entity_json = json.dumps(json_values)


                        # Hash the params string to produce the Sign header value
                        H = hmac.new(UETOPIA_ASSIGNED_GAME_API_SECRET, digestmod=hashlib.sha512)
                        H.update(entity_json)
                        sign = H.hexdigest()

                        headers = {"Content-type": "application/x-www-form-urlencoded",
                                           "Key":UETOPIA_ASSIGNED_GAME_API_KEY,
                                           "Sign":sign}

                        conn = httplib.HTTPSConnection(UETOPIA_API_URL)

                        conn.request("POST", uri, entity_json, headers)
                        response = conn.getresponse()

                        #logging.info(response.read())

                        ## parse the response
                        jsonstring = str(response.read())
                        logging.info(jsonstring)
                        jsonobject = json.loads(jsonstring)

                        # do something with the response?
                        if not jsonobject['request_successful']:
                            logging.info('the request was unsuccessful')

                        logging.info('request was successful')

                # push a chat out to discord - only if not hidden
                ## TODO Customize this for your game and community
                if not achievement.hidden:
                    http_auth = Http()
                    headers = {"Content-Type": "application/json"}
                    URL = ACHIEVEMENT_DISCORD_WEBHOOK
                    message = "%s : %s " % (character.title, achievement.description)
                    url = "https://uetopia-metagame.appspot.com/#/characters/%s" % (character.key.id())

                    if achievement.first:
                        msg_title = "WORLD FIRST: " + achievement.title
                    elif achievement.season_first:
                        msg_title = "SEASON FIRST: " + achievement.title
                    else:
                        msg_title = achievement.title

                    discord_data = { "embeds": [{"title": msg_title, "url": url, "description": message}] }
                    data=json.dumps(discord_data)
                    resp, content = http_auth.request(URL,
                                      "POST",
                                      data,
                                      headers=headers)
