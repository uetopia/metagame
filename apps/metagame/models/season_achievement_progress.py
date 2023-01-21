import endpoints
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types

class SeasonAchievementProgress(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    # ref to the achievement
    achievementKeyId = ndb.IntegerProperty(indexed=False)

    # general info
    title = ndb.StringProperty(indexed=False)
    description = ndb.TextProperty(indexed=False)
    iconUrl = ndb.StringProperty(indexed=False)

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
    seasonKeyId = ndb.IntegerProperty(indexed=True)
    seasonTitle = ndb.StringProperty(indexed=False)

    # unknown achievements will show up in the achievement list, but with a ? and no description
    unknown = ndb.BooleanProperty(indexed=False)
    # hidden do not show in the achievement list
    hidden = ndb.BooleanProperty(indexed=True)

    # Track the progress in completing the achievement.
    # Some calculations may want a float, or an int, so we track both
    progressInt = ndb.IntegerProperty(indexed=False)
    progressFloat = ndb.FloatProperty(indexed=False)

    # refs to player and character
    userKeyId = ndb.IntegerProperty(indexed=False)
    userTitle = ndb.StringProperty(indexed=False)
    characterKeyId = ndb.IntegerProperty(indexed=True)
    characterTitle = ndb.StringProperty(indexed=False)
    seasonCharacterKeyId = ndb.IntegerProperty(indexed=True)
    seasonCharacterTitle = ndb.StringProperty(indexed=False)

    # flags
    # earned means the player has earned the achievement.
    earned = ndb.BooleanProperty(indexed=True)
    # awarded after the drops have been given to the player
    # so we can do this in a seperate task
    awarded = ndb.BooleanProperty(indexed=True)
    bidReturned = ndb.BooleanProperty(indexed=False)

    # firsts are only awarded one time, and the player that earned it keeps the bragging rights
    # season firsts are similarly only awarded once per season
    first = ndb.BooleanProperty(indexed=False)
    season_first = ndb.BooleanProperty(indexed=False)

    def to_json(self):

        return ({
            u'title': self.title,
            u'description': self.description,
            u'iconUrl': self.iconUrl,
            u'seasonal': self.seasonal
        })


### PROTORPC MODELS FOR ENDPOINTS
### These are used to specify incoming and outgoing variables from the endpoints API
class AchievementSeasonProgressResponse(messages.Message):
    """ a AchievementSeasonProgress's data """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32)
    title = messages.StringField(2)
    description = messages.StringField(3)
    iconUrl = messages.StringField(4)
    seasonal = messages.BooleanField(5)
    first = messages.BooleanField(6)
    season_first = messages.BooleanField(7)

    response_message = messages.StringField(40)
    response_successful = messages.BooleanField(50)


class AchievementSeasonProgressRequest(messages.Message):
    """ a AchievementSeasonProgress updates """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32)
    title = messages.StringField(2)
    description = messages.StringField(3)
    iconUrl = messages.StringField(4)
    seasonal = messages.BooleanField(5)

ACHIEVEMENT_SEASON_PROGRESS_RESOURCE = endpoints.ResourceContainer(
    AchievementSeasonProgressRequest
)

class AchievementSeasonProgressCollection(messages.Message):
    """ multiple AchievementSeasonProgress """
    achievement_progrogresses = messages.MessageField(AchievementSeasonProgressResponse, 1, repeated=True)
    response_message = messages.StringField(40)
    response_successful = messages.BooleanField(50)

class AchievementSeasonProgressCollectionRequest(messages.Message):
    """ a AchievementSeasonProgress collection request's data """
    cursor = messages.StringField(1)
    sort_order = messages.StringField(2)
    direction = messages.StringField(3)
    characterKeyId = messages.IntegerField(4, variant=messages.Variant.INT32)
    earned = messages.BooleanField(5)
    seasonKeyId = messages.IntegerField(6, variant=messages.Variant.INT32)
    awarded = messages.BooleanField(7)

ACHIEVEMENT_SEASON_PROGRESS_COLLECTION_PAGE_RESOURCE = endpoints.ResourceContainer(
    AchievementSeasonProgressCollectionRequest
)
