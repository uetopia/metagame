import logging
from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.metagame.models.bids import Bids

class BidsController(BaseController):
    """Bids Controller"""
    def __init__(self):

        self._default_order = 'created'
        self.model = Bids

    def list_by_zoneKeyId(self, zoneKeyId):
        """ get a list of bids for a zone """
        query = self.model.query()
        query = query.filter(self.model.zoneKeyId == zoneKeyId)
        query = query.order(-self.model.created)
        return query.fetch(1000)

    def list_processed_by_factionKeyId(self, factionKeyId):
        """ get a list of bids for a faction """
        query = self.model.query()
        query = query.filter(self.model.factionKeyId == factionKeyId)
        query = query.filter(self.model.bidProcessed == True)
        return query.fetch(1000)

    def get_unprocessed_by_userKeyId(self, userKeyId):
        """ get a list of bids for a faction """
        query = self.model.query()
        query = query.filter(self.model.userKeyId == userKeyId)
        query = query.filter(self.model.bidProcessed == False)
        return query.get()
