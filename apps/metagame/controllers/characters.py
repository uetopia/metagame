import logging
from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.metagame.models.characters import Characters

class CharactersController(BaseController):
    """Characters Controller"""
    def __init__(self):

        self._default_order = 'created'
        self.model = Characters

    def list_by_userKeyId(self, userKeyId):
        query = self.model.query()
        query = query.filter(self.model.userKeyId == userKeyId)
        return query.fetch(100)

    def get_by_uetopia_characterKeyId(self, uetopia_characterKeyId):
        """ get a character """
        query = self.model.query()
        query = query.filter(self.model.uetopia_characterKeyId == uetopia_characterKeyId)
        return query.get()

    def list_by_top_rank(self):
        query = self.model.query()
        query = query.order(-self.model.rank)
        return query.fetch(100)
