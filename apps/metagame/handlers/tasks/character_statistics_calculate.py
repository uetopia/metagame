import endpoints
import logging
import uuid
import urllib
import json
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

class CharacterStatisticsCalculateHandler(BaseHandler):
    """ /task/character/statistics/calculate """

    def achievementProgressExists(self, achievement, achievement_progresses):
        for achievement_progress in achievement_progresses:
            if achievement.key.id() == achievement_progress.achievementKeyId:
                return True
        return False

    def getRegularAchievementByKeyId(self, achievementKeyId):
        for regular_achievement in self.regular_achievements:
            if regular_achievement.key.id() == achievementKeyId:
                return regular_achievement
        return None

    def getSeasonalAchievementByKeyId(self, achievementKeyId):
        for seasonal_achievement in self.seasonal_achievements:
            if seasonal_achievement.key.id() == achievementKeyId:
                return seasonal_achievement
        return None

    def post(self):
        logging.info("[TASK] CharacterStatisticsCalculateHandler")

        key_id = self.request.get('key_id')

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

        ## Get the list of achievements
        achievements = achievementController.list()
        self.regular_achievements = []
        self.seasonal_achievements = []


        ## keep a list of the seasonal ones seperate
        for achievement in achievements:
            if achievement.seasonal:
                self.seasonal_achievements.append(achievement)
            else:
                self.regular_achievements.append(achievement)



        logging.info('found character')

        ## keep track if any achievements were earned
        achievement_earned = False

        ## get the non-seasonal achievement progress for this char
        achievement_progresses = achievementProgressController.list_by_characterKeyId(character.key.id())

        if len(self.regular_achievements) != len(achievement_progresses):
            logging.info('achievement mismatch')
            for achievement in self.regular_achievements:
                logging.info('checking regular achievement')

                if not self.achievementProgressExists(achievement, achievement_progresses):
                    logging.info('achievement progress not found.  Adding. ')
                    achievement_progress = achievementProgressController.create(
                        achievementKeyId = achievement.key.id(),
                        title = achievement.title,
                        description = achievement.description,
                        iconUrl = achievement.iconUrl,
                        calculation = achievement.calculation,
                        calculation_int = achievement.calculation_int,
                        unknown = achievement.unknown,
                        hidden = achievement.hidden,
                        progressInt = 0,
                        progressFloat = 0.0,
                        userKeyId = character.userKeyId,
                        characterKeyId = character.key.id(),
                        characterTitle = character.title,
                        execute_per_match = achievement.execute_per_match,
                        execute_all_matches = achievement.execute_all_matches,
                        earned = False,
                        awarded = False,
                        first = False,
                        season_first = False
                        )

                    ## add it to the existing array
                    achievement_progresses.append(achievement_progress)



        ## Get the active season character
        season_character = seasonCharacterController.get_by_characterKeyId_seasonKeyId(character.key.id(), active_season.key.id())

        if season_character:
            logging.info('season character found')

            ## reset season character values
            season_character.damage_dealt = 0
            ## TODO: Insert all of your custom variables.
            season_character.damage_received = 0
            season_character.kills = 0
            season_character.assists = 0
            season_character.deaths = 0
            season_character.matches_played = 0
            season_character.mm1v1_played = 0
            season_character.mm2v2_played = 0
            season_character.mm3v3_played = 0
            season_character.mm4v4_played = 0
            season_character.matches_won = 0
            season_character.mm1v1_won = 0
            season_character.mm2v2_won = 0
            season_character.mm3v3_won = 0
            season_character.mm4v4_won = 0

            ## reset character values
            character.damage_dealt = 0
            ## TODO: Insert all of your custom variables.
            character.damage_received = 0
            character.kills = 0
            character.assists = 0
            character.deaths = 0
            character.matches_played = 0
            character.mm1v1_played = 0
            character.mm2v2_played = 0
            character.mm3v3_played = 0
            character.mm4v4_played = 0
            character.matches_won = 0
            character.mm1v1_won = 0
            character.mm2v2_won = 0
            character.mm3v3_won = 0
            character.mm4v4_won = 0


            ## get the seasonal achievement progress for this SEASON char
            season_achievement_progresses = seasonAchievementProgressController.list_by_characterKeyId_seasonKeyId(character.key.id(), active_season.key.id())

            if len(self.seasonal_achievements) != len(season_achievement_progresses):
                logging.info('season achievement mismatch')
                for achievement in self.seasonal_achievements:
                    logging.info('checking seasonal achievement')


                    if not self.achievementProgressExists(achievement, season_achievement_progresses):
                        logging.info('season achievement progress not found.  Adding. ')
                        season_achievement_progress = seasonAchievementProgressController.create(
                            achievementKeyId = achievement.key.id(),
                            title = achievement.title,
                            description = achievement.description,
                            iconUrl = achievement.iconUrl,
                            calculation = achievement.calculation,
                            calculation_int = achievement.calculation_int,
                            unknown = achievement.unknown,
                            hidden = achievement.hidden,
                            progressInt = 0,
                            progressFloat = 0.0,
                            userKeyId = character.userKeyId,
                            characterKeyId = character.key.id(),
                            characterTitle = character.title,
                            seasonKeyId = active_season.key.id(),
                            seasonTitle = active_season.title,
                            execute_per_match = achievement.execute_per_match,
                            execute_all_matches = achievement.execute_all_matches,
                            earned = False,
                            awarded = False,
                            first = False,
                            season_first = False
                            )

                        ## add it to the existing array
                        season_achievement_progresses.append(season_achievement_progress)

            ## Now we have the season achievement progress records, and can process them .



            ## Get all of the mmmatch character data
            ## there could be more than 1000 records here...  TODO batch this properly
            matches = mMMatchCharacterController.list_by_seasonKeyId_seasonCharacterKeyId(active_season.key.id(), season_character.key.id() )
            logging.info(len(matches))

            for match in matches:
                season_character.title = match.title # we are in chronological order, so the most recent match should have the latest title with faction tag.
                season_character.damage_dealt = season_character.damage_dealt + match.damage_dealt
                ## TODO: Insert all of your custom variables.
                season_character.damage_received = season_character.damage_received + match.damage_received
                season_character.kills = season_character.kills + match.kills
                season_character.assists = season_character.assists + match.assists
                season_character.deaths = season_character.deaths + match.deaths
                season_character.rank = match.rank
                season_character.score = match.score
                season_character.level = match.level
                season_character.matches_played = season_character.matches_played + match.matches_played
                season_character.mm1v1_played = season_character.mm1v1_played + match.mm1v1_played
                season_character.mm2v2_played = season_character.mm2v2_played + match.mm2v2_played
                season_character.mm3v3_played = season_character.mm3v3_played + match.mm3v3_played
                season_character.mm4v4_played = season_character.mm4v4_played +match.mm4v4_played
                season_character.matches_won = season_character.matches_won + match.matches_won
                season_character.mm1v1_won = season_character.mm1v1_won + match.mm1v1_won
                season_character.mm2v2_won = season_character.mm2v2_won + match.mm2v2_won
                season_character.mm3v3_won = season_character.mm3v3_won + match.mm3v3_won
                season_character.mm4v4_won = season_character.mm4v4_won + match.mm4v4_won

                character.title = match.title # we are in chronological order, so the most recent match should have the latest title with faction tag.
                character.damage_dealt = character.damage_dealt + match.damage_dealt
                ## TODO: Insert all of your custom variables.
                character.damage_received = character.damage_received + match.damage_received
                character.kills = character.kills + match.kills
                character.assists = character.assists + match.assists
                character.deaths = character.deaths + match.deaths
                character.rank = match.rank
                character.score = match.score
                character.level = match.level
                character.matches_played = character.matches_played + match.matches_played
                character.mm1v1_played = character.mm1v1_played + match.mm1v1_played
                character.mm2v2_played = character.mm2v2_played + match.mm2v2_played
                character.mm3v3_played = character.mm3v3_played + match.mm3v3_played
                character.mm4v4_played = character.mm4v4_played +match.mm4v4_played
                character.matches_won = character.matches_won + match.matches_won
                character.mm1v1_won = character.mm1v1_won + match.mm1v1_won
                character.mm2v2_won = character.mm2v2_won + match.mm2v2_won
                character.mm3v3_won = character.mm3v3_won + match.mm3v3_won
                character.mm4v4_won = character.mm4v4_won + match.mm4v4_won


                ## do per match achievements

                logging.info('checking regular match achievements')
                for achievement_progress in achievement_progresses:
                    if not achievement_progress.earned:
                        #logging.info('this achievement has not been earned')
                        if achievement_progress.execute_per_match:
                            #logging.info('execution set to match')

                            ## run the calculation
                            if achievement_progress.calculation == 'damage_done':
                                achievement_progress = calc_damage_done(character, achievement_progress, achievement_progress.calculation_int)


                            ## check for earned
                            if achievement_progress.earned:
                                achievement_earned = True

                                ## check for firsts
                                reg_achievement = self.getRegularAchievementByKeyId(achievement_progress.achievementKeyId)

                                if reg_achievement:
                                    #logging.info('got reg achievement')
                                    if not reg_achievement.world_first_awarded:
                                        #logging.info('world first has not been awarded')
                                        achievement_progress.first = True

                                        ## update the achievement
                                        reg_achievement.world_first_awarded = True
                                        achievementController.update(reg_achievement)


                            ## save the progress
                            achievementProgressController.update(achievement_progress)

                logging.info('checking seasonal match achievements')
                for season_achievement_progress in season_achievement_progresses:
                    if not season_achievement_progress.earned:
                        #logging.info('this achievement has not been earned')
                        if season_achievement_progress.execute_per_match:
                            #logging.info('execution set to match')

                            ## run the calculation
                            if season_achievement_progress.calculation == 'damage_done':
                                season_achievement_progress = calc_damage_done(character, season_achievement_progress, season_achievement_progress.calculation_int)

                            ## check for earned
                            if season_achievement_progress.earned:
                                achievement_earned = True

                                ## check for firsts
                                season_achievement = self.getSeasonalAchievementByKeyId(season_achievement_progress.achievementKeyId)

                                if season_achievement:
                                    #logging.info('got season achievement')
                                    if not season_achievement.season_first_awarded:
                                        #logging.info('season_first_awarded has not been awarded')
                                        achievement_progress.season_first = True

                                        ## update the achievement
                                        season_achievement.season_first_awarded = True
                                        achievementController.update(season_achievement)

                            ## save the progress
                            seasonAchievementProgressController.update(season_achievement_progress)




            seasonCharacterController.update(season_character)
            characterController.update(character)

            ## TODO - do all match achievements
            logging.info('checking regular all match achievements')
            for achievement_progress in achievement_progresses:
                if not achievement_progress.earned:
                    #logging.info('this achievement has not been earned')
                    if achievement_progress.execute_all_matches:
                        #logging.info('execution set to all matches')

                        ## run the calculation
                        if achievement_progress.calculation == 'damage_done':
                            achievement_progress = calc_damage_done(character, achievement_progress, achievement_progress.calculation_int)

                        ## check for earned
                        if achievement_progress.earned:
                            achievement_earned = True

                            ## check for firsts
                            reg_achievement = self.getRegularAchievementByKeyId(achievement_progress.achievementKeyId)

                            if reg_achievement:
                                #logging.info('got reg achievement')
                                if not reg_achievement.world_first_awarded:
                                    #logging.info('world first has not been awarded')
                                    achievement_progress.first = True

                                    ## update the achievement
                                    reg_achievement.world_first_awarded = True
                                    achievementController.update(reg_achievement)

                        ## save the progress
                        achievementProgressController.update(achievement_progress)

            logging.info('checking seasonal all match achievements')
            for season_achievement_progress in season_achievement_progresses:
                if not season_achievement_progress.earned:
                    #logging.info('this achievement has not been earned')
                    if season_achievement_progress.execute_all_matches:
                        #logging.info('execution set to all matches')

                        ## run the calculation
                        if season_achievement_progress.calculation == 'damage_done':
                            season_achievement_progress = calc_damage_done(character, season_achievement_progress, season_achievement_progress.calculation_int)

                        ## check for earned
                        if season_achievement_progress.earned:
                            achievement_earned = True

                            ## check for firsts
                            season_achievement = self.getSeasonalAchievementByKeyId(season_achievement_progress.achievementKeyId)

                            if season_achievement:
                                #logging.info('got season achievement')
                                if not season_achievement.season_first_awarded:
                                    #logging.info('season_first_awarded has not been awarded')
                                    season_achievement_progress.season_first = True

                                    ## update the achievement
                                    season_achievement.season_first_awarded = True
                                    achievementController.update(season_achievement)


                        ## save the progress
                        seasonAchievementProgressController.update(season_achievement_progress)



            ## start up a task to process earned achievements
            if achievement_earned:
                logging.info('one or more achievements was earned - starting up task to process them.')

                ##      Start a task to process the character record.
                taskUrl='/task/character/achievement/process'
                taskqueue.add(url=taskUrl, queue_name='UserStatisticsCalculate', params={'key_id': character.key.id()}, countdown = 2,)
