import logging
from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.metagame.models.mm_match_character import MMMatchCharacter

class MMMatchCharacterController(BaseController):
    """MM Match Character Controller"""
    def __init__(self):

        self._default_order = 'created'
        self.model = MMMatchCharacter

    def list_by_seasonKeyId_seasonCharacterKeyId(self, seasonKeyId, seasonCharacterKeyId):
        query = self.model.query()
        query = query.filter(self.model.seasonKeyId == seasonKeyId)
        query = query.filter(self.model.seasonCharacterKeyId == seasonCharacterKeyId)
        query = query.order(self.model.created)
        return query.fetch(1000)

    def list_by_mmmatchKeyId(self, mmmatchKeyId):
        query = self.model.query()
        query = query.filter(self.model.mmmatchKeyId == mmmatchKeyId)
        return query.fetch(1000)

    def list_recent_by_characterKeyId(self, characterKeyId):
        query = self.model.query()
        query = query.filter(self.model.characterKeyId == characterKeyId)
        query = query.order(-self.model.created)
        return query.fetch(10)
