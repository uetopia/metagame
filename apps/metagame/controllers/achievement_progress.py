import logging
from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.metagame.models.achievement_progress import AchievementProgress

class AchievementProgressController(BaseController):
    """AchievementProgress Controller"""
    def __init__(self):

        self._default_order = 'created'
        self.model = AchievementProgress

    def get_by_characterKeyId_achievementKeyId(self, characterKeyId, achievementKeyId):
        """ get a user """
        query = self.model.query()
        query = query.filter(self.model.characterKeyId == characterKeyId)
        query = query.filter(self.model.achievementKeyId == achievementKeyId)
        return query.get()

    def list_by_characterKeyId(self, characterKeyId):
        """ get a list of progresses for a character """
        query = self.model.query()
        query = query.filter(self.model.characterKeyId == characterKeyId)
        return query.fetch(1000)

    def list_by_characterKeyId_earned(self, characterKeyId):
        """ get a list of earned progresses for a character """
        query = self.model.query()
        query = query.filter(self.model.characterKeyId == characterKeyId)
        query = query.filter(self.model.earned == True)
        query = query.filter(self.model.awarded == False)
        return query.fetch(1000)

    def list_by_characterKeyId_earned_not_hidden(self, characterKeyId):
        """ get a list of earned progresses for a character """
        query = self.model.query()
        query = query.filter(self.model.characterKeyId == characterKeyId)
        query = query.filter(self.model.earned == True)
        query = query.filter(self.model.awarded == False)
        query = query.filter(self.model.hidden == False)
        return query.fetch(1000)

    def list_by_characterKeyId_awarded_not_hidden(self, characterKeyId):
        """ get a list of earned progresses for a character """
        query = self.model.query()
        query = query.filter(self.model.characterKeyId == characterKeyId)
        query = query.filter(self.model.awarded == True)
        query = query.filter(self.model.hidden == False)
        return query.fetch(1000)
