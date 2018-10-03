import logging
from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.metagame.models.match import Match

class MatchController(BaseController):
    """Match Controller"""
    def __init__(self):

        self._default_order = 'created'
        self.model = Match

    def list_active_page(self, page_size=20, batch_size=5, start_cursor=None):
        query = self.model.query()
        query = query.filter(self.model.active == True)
        entities, cursor, more = query.fetch_page(page_size,start_cursor=start_cursor, batch_size=batch_size)
        return entities, cursor, more
