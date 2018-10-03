import logging
from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.metagame.models.seasons import Seasons

class SeasonsController(BaseController):
    """Seasons Controller"""
    def __init__(self):

        self._default_order = 'created'
        self.model = Seasons

    def get_active(self):
        """ Get the active season """
        query = self.model.query()
        query = query.filter(self.model.active == True)
        return query.get()
