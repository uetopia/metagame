import logging
from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.metagame.models.model import Model

class ModelController(BaseController):
    """Model Controller"""
    def __init__(self):

        self._default_order = 'created'
        self.model = Model

    def list_page_by_user_id(self, user_id, page_size=20, batch_size=5, start_cursor=None, order=None, filterbytext=None):
        query = self.model.query()
        query = query.filter(self.model.user_id == user_id)

        entities, cursor, more = query.fetch_page(page_size,start_cursor=start_cursor, batch_size=batch_size)

        return entities, cursor, more#, cursor_back, less
