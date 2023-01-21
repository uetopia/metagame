import logging
from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.metagame.models.mm_match import MMMatch

class MMMatchController(BaseController):
    """Matchmaker Match Controller"""
    def __init__(self):

        self._default_order = 'created'
        self.model = MMMatch

    def get_by_uetopiaMatchKeyId(self, uetopiaMatchKeyId):
        """ get a mmmatch by uetopiaMatchKeyId """
        query = self.model.query()
        query = query.filter(self.model.uetopiaMatchKeyId == uetopiaMatchKeyId)
        return query.get()
