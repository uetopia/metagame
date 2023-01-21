import logging
from apps.controllers import BaseController
from google.appengine.ext import ndb
from apps.metagame.models.achievements import Achievements

class AchievementsController(BaseController):
    """Achievements Controller"""
    def __init__(self):

        self._default_order = 'created'
        self.model = Achievements
