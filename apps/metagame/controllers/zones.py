import logging
from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.metagame.models.zones import Zones

class ZonesController(BaseController):
    """Seasons Controller"""
    def __init__(self):

        self._default_order = 'created'
        self.model = Zones

    def list_by_mapKeyId(self, mapKeyId):
        """ get a list of zones for a map """
        query = self.model.query()
        query = query.filter(self.model.mapKeyId == mapKeyId)
        #query = query.order(self.model.horizontalIndex, self.model.verticalIndex)
        return query.fetch(1000)

    def list_ordered_by_mapKeyId(self, mapKeyId):
        """ get a list of zones for a map """
        query = self.model.query()
        query = query.filter(self.model.mapKeyId == mapKeyId)
        query = query.order(self.model.verticalIndex)
        query = query.order(self.model.horizontalIndex)
        return query.fetch(1000)

    def get_controlled_by_userCaptainKeyId(self, userCaptainKeyId):
        """ get a controlled zone by the user controlling it """
        query = self.model.query()
        query = query.filter(self.model.userCaptainKeyId == userCaptainKeyId)
        #query = query.order(self.model.horizontalIndex, self.model.verticalIndex)
        return query.get()

    def list_by_factionKeyId(self, factionKeyId):
        """ get a controlled zone by the user controlling it """
        query = self.model.query()
        query = query.filter(self.model.factionKeyId == factionKeyId)
        #query = query.order(self.model.horizontalIndex, self.model.verticalIndex)
        return query.fetch(1000)
