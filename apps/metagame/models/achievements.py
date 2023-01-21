import endpoints
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types

class Achievements(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    # general info
    title = ndb.StringProperty(indexed=False)
    description = ndb.TextProperty(indexed=False)
    iconUrl = ndb.StringProperty(indexed=False)

    drop_json = ndb.TextProperty(indexed=False)
    # we need stome extra info about drops for the http request.
    drop_tier = ndb.IntegerProperty(indexed=False)

    # calculation is a reference to a specific attribute calculation.
    # these are performed in python as to permit maximum freedom.
    calculation = ndb.StringProperty(indexed=False)
    # a variable to pass into the calculation - damage > 50 for example
    calculation_int = ndb.IntegerProperty(indexed=False)

    # per match execution is like 5000 damage in a single match
    execute_per_match = ndb.BooleanProperty(indexed=False)
    ## all matches is executed after all match data is combined
    execute_all_matches = ndb.BooleanProperty(indexed=False)

    # seasonal
    seasonal = ndb.BooleanProperty(indexed=False)

    # unknown achievements will show up in the achievement list, but with a ? and no description
    unknown = ndb.BooleanProperty(indexed=False)
    # hidden do not show in the achievement list
    hidden = ndb.BooleanProperty(indexed=True)
    # give the drop when completed.
    do_drop = ndb.BooleanProperty(indexed=False)

    world_first_awarded = ndb.BooleanProperty(indexed=False)

    # this one needs to be cleared every time a season changes.
    season_first_awarded = ndb.BooleanProperty(indexed=False)


    # keep track of the how many players have earned this achievement?
    # order
    # grouping

    ## TODO - store any extra information about your Region

    def to_json(self):

        return ({
            u'title': self.title,
            u'description': self.description,
            u'iconUrl': self.iconUrl,
            u'seasonal': self.seasonal
        })


### PROTORPC MODELS FOR ENDPOINTS
### These are used to specify incoming and outgoing variables from the endpoints API
class AchievementResponse(messages.Message):
    """ a season's data """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32)
    title = messages.StringField(2)
    description = messages.StringField(3)
    iconUrl = messages.StringField(4)
    drop_json = messages.StringField(5)
    drop_tier = messages.IntegerField(17, variant=messages.Variant.INT32)
    calculation = messages.StringField(6)
    calculation_int = messages.IntegerField(7, variant=messages.Variant.INT32)
    seasonal = messages.BooleanField(8)
    unknown = messages.BooleanField(9)
    hidden = messages.BooleanField(10)
    do_drop = messages.BooleanField(11)
    execute_per_match = messages.BooleanField(12)
    execute_all_matches = messages.BooleanField(13)

    response_message = messages.StringField(40)
    response_successful = messages.BooleanField(50)


class AchievementRequest(messages.Message):
    """ a Achievement updates """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32)
    title = messages.StringField(2)
    description = messages.StringField(3)
    iconUrl = messages.StringField(4)
    drop_json = messages.StringField(5)
    drop_tier = messages.IntegerField(17, variant=messages.Variant.INT32)
    calculation = messages.StringField(6)
    calculation_int = messages.IntegerField(7, variant=messages.Variant.INT32)
    seasonal = messages.BooleanField(8)
    unknown = messages.BooleanField(9)
    hidden = messages.BooleanField(10)
    do_drop = messages.BooleanField(11)
    execute_per_match = messages.BooleanField(12)
    execute_all_matches = messages.BooleanField(13)

ACHIEVEMENT_RESOURCE = endpoints.ResourceContainer(
    AchievementRequest
)

class AchievementCollection(messages.Message):
    """ multiple Achievements """
    achievements = messages.MessageField(AchievementResponse, 1, repeated=True)
    response_message = messages.StringField(40)
    response_successful = messages.BooleanField(50)

class AchievementCollectionRequest(messages.Message):
    """ a Achievement collection request's data """
    cursor = messages.StringField(1)
    sort_order = messages.StringField(2)
    direction = messages.StringField(3)

ACHIEVEMENT_COLLECTION_PAGE_RESOURCE = endpoints.ResourceContainer(
    AchievementCollectionRequest
)
