import logging
from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.metagame.models.users import Users

class UsersController(BaseController):
    """Users Controller"""
    def __init__(self):

        self._default_order = 'created'
        self.model = Users

    def get_by_firebaseUser(self, firebaseUser):
        """ get a user """
        query = self.model.query()
        query = query.filter(self.model.firebaseUser == firebaseUser)
        return query.get()

    def get_by_uetopia_playerKeyId(self, uetopia_playerKeyId):
        """ get a user """
        query = self.model.query()
        query = query.filter(self.model.uetopia_playerKeyId == uetopia_playerKeyId)
        return query.get()

    def list_roundActionUsed_page(self, page_size=20, batch_size=5, start_cursor=None):
        query = self.model.query()
        query = query.filter(self.model.roundActionUsed == True)
        entities, cursor, more = query.fetch_page(page_size,start_cursor=start_cursor, batch_size=batch_size)
        return entities, cursor, more

    def list_factionLeaders(self, currentFactionKeyId):
        query = self.model.query()
        query = query.filter(self.model.currentFactionKeyId == currentFactionKeyId)
        query = query.filter(self.model.currentFactionLead == True)
        return query.fetch(1000)
