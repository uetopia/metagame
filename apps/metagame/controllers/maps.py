import logging
from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.metagame.models.maps import Maps

class MapsController(BaseController):
    """Maps Controller"""
    def __init__(self):

        self._default_order = 'created'
        self.model = Maps

    def list_by_regionKeyId(self, regionKeyId):
        """ get a list of maps for a region """
        query = self.model.query()
        query = query.filter(self.model.regionKeyId == regionKeyId)
        return query.fetch(100)

    def list_by_seasonKeyId(self, seasonKeyId):
        """ get a list of maps for a season """
        query = self.model.query()
        query = query.filter(self.model.seasonKeyId == seasonKeyId)
        return query.fetch(1000)
