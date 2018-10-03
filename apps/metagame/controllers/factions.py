import logging
from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.metagame.models.factions import Factions

class FactionsController(BaseController):
    """Factions Controller"""
    def __init__(self):

        self._default_order = 'created'
        self.model = Factions

    def get_by_uetopia_groupKeyId(self, uetopia_groupKeyId):
        """ get a user """
        query = self.model.query()
        query = query.filter(self.model.uetopia_groupKeyId == uetopia_groupKeyId)
        return query.get()

    def list_active_season_page(self, activeSeasonKeyId, page_size=20, batch_size=5, start_cursor=None):
        query = self.model.query()
        query = query.filter(self.model.activeSeasonKeyId == activeSeasonKeyId)
        entities, cursor, more = query.fetch_page(page_size,start_cursor=start_cursor, batch_size=batch_size)
        return entities, cursor, more

    def list_active_season_page_by_control(self, activeSeasonKeyId, page_size=20, batch_size=5, start_cursor=None):
        query = self.model.query()
        query = query.filter(self.model.activeSeasonKeyId == activeSeasonKeyId)
        query = query.order(-self.model.control)
        entities, cursor, more = query.fetch_page(page_size,start_cursor=start_cursor, batch_size=batch_size)
        return entities, cursor, more
