import logging
from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.metagame.models.regions import Regions

class RegionsController(BaseController):
    """Regions Controller"""
    def __init__(self):

        self._default_order = 'created'
        self.model = Regions
