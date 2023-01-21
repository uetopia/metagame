import logging
from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.metagame.models.season_characters import SeasonCharacters

class SeasonCharactersController(BaseController):
    """SeasonCharacters Controller"""
    def __init__(self):

        self._default_order = 'created'
        self.model = SeasonCharacters

    def get_by_characterKeyId_seasonKeyId(self, characterKeyId, seasonKeyId):
        """ Get the season character """
        query = self.model.query()
        query = query.filter(self.model.characterKeyId == characterKeyId)
        query = query.filter(self.model.seasonKeyId == seasonKeyId)
        return query.get()

    def list_by_characterKeyId(self, characterKeyId):
        """ get a list of seasoncharacters for a character """
        query = self.model.query()
        query = query.filter(self.model.characterKeyId == characterKeyId)
        #query = query.order(self.model.horizontalIndex, self.model.verticalIndex)
        return query.fetch(1000)
