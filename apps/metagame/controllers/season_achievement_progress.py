import logging
from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.metagame.models.season_achievement_progress import SeasonAchievementProgress

class SeasonAchievementProgressController(BaseController):
    """SeasonAchievementProgress Controller"""
    def __init__(self):

        self._default_order = 'created'
        self.model = SeasonAchievementProgress

    def get_by_characterKeyId_achievementKeyId_seasonKeyId(self, characterKeyId, achievementKeyId, seasonKeyId):
        """ get a user """
        query = self.model.query()
        query = query.filter(self.model.characterKeyId == characterKeyId)
        query = query.filter(self.model.achievementKeyId == achievementKeyId)
        query = query.filter(self.model.seasonKeyId == seasonKeyId)
        return query.get()

    def list_by_characterKeyId_seasonKeyId(self, characterKeyId, seasonKeyId):
        """ get a list of progresses for a season character """
        query = self.model.query()
        query = query.filter(self.model.characterKeyId == characterKeyId)
        query = query.filter(self.model.seasonKeyId == seasonKeyId)
        return query.fetch(1000)

    def list_by_characterKeyId_seasonKeyId_earned(self, characterKeyId, seasonKeyId):
        """ get a list of progresses for a season character """
        query = self.model.query()
        query = query.filter(self.model.characterKeyId == characterKeyId)
        query = query.filter(self.model.seasonKeyId == seasonKeyId)
        query = query.filter(self.model.earned == True)
        query = query.filter(self.model.awarded == False)
        return query.fetch(1000)

    def list_by_characterKeyId_seasonKeyId_earned_not_hidden(self, characterKeyId, seasonKeyId):
        """ get a list of progresses for a season character """
        query = self.model.query()
        query = query.filter(self.model.characterKeyId == characterKeyId)
        query = query.filter(self.model.seasonKeyId == seasonKeyId)
        query = query.filter(self.model.earned == True)
        query = query.filter(self.model.awarded == False)
        query = query.filter(self.model.hidden == False)
        return query.fetch(1000)

    def list_by_characterKeyId_seasonKeyId_awarded_not_hidden(self, characterKeyId, seasonKeyId):
        """ get a list of progresses for a season character """
        query = self.model.query()
        query = query.filter(self.model.characterKeyId == characterKeyId)
        query = query.filter(self.model.seasonKeyId == seasonKeyId)
        query = query.filter(self.model.awarded == True)
        query = query.filter(self.model.hidden == False)
        return query.fetch(1000)
