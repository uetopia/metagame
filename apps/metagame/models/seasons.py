import endpoints
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types

class Seasons(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    starts = ndb.DateTimeProperty()
    ends = ndb.DateTimeProperty()

    # general user info
    title = ndb.StringProperty(indexed=False)
    description = ndb.TextProperty(indexed=False)

    # currently active
    active = ndb.BooleanProperty(indexed=True)
    # active but closing down
    closing = ndb.BooleanProperty(indexed=False)
    # next season - so we can show "next season starts in"
    next = ndb.BooleanProperty(indexed=True)

    # round status
    currentRound = ndb.IntegerProperty(indexed=True)
    currentRoundPositioning = ndb.BooleanProperty(indexed=True)
    currentRoundCombat = ndb.BooleanProperty(indexed=True)
    currentRoundResults = ndb.BooleanProperty(indexed=True)

    # TODO - optional play start/end times?

    # keep track of the winner(s) after the season is complete
    winningFactionKeyId = ndb.IntegerProperty(indexed=False)
    winningFactionTag = ndb.StringProperty(indexed=False)
    winningFactionKeyControl = ndb.IntegerProperty(indexed=False)


    ## TODO - store any extra information about your Region

    def to_json(self):

        ## convert datetimes if entered
        if self.starts:
            starts_str = self.starts.isoformat()
        else:
            starts_str = ""

        if self.ends:
            ends_str = self.ends.isoformat()
        else:
            ends_str = ""

        return ({
            u'title': self.title,
            u'description': self.description,
            u'starts': starts_str,
            u'ends': ends_str,
            u'active': self.active,
            u'closing': self.closing,
            u'currentRound':self.currentRound,
            u'currentRoundPositioning': self.currentRoundPositioning,
            u'currentRoundCombat': self.currentRoundCombat,
            u'currentRoundResults': self.currentRoundResults
        })



### PROTORPC MODELS FOR ENDPOINTS
### These are used to specify incoming and outgoing variables from the endpoints API
class SeasonResponse(messages.Message):
    """ a season's data """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32)
    title = messages.StringField(2)
    description = messages.StringField(3)
    starts = messages.StringField(4)
    ends = messages.StringField(5)
    active = messages.BooleanField(6)
    closing = messages.BooleanField(7)
    next = messages.BooleanField(8)
    currentRound = messages.IntegerField(17, variant=messages.Variant.INT32)
    currentRoundPositioning = messages.BooleanField(18)
    currentRoundCombat = messages.BooleanField(19)
    currentRoundResults = messages.BooleanField(20)
    created = messages.StringField(21)

    response_message = messages.StringField(40)
    response_successful = messages.BooleanField(50)


class SeasonRequest(messages.Message):
    """ a serasons updates """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32)
    title = messages.StringField(2)
    description = messages.StringField(3)
    starts = messages.StringField(4)
    ends = messages.StringField(5)
    active = messages.BooleanField(6)
    closing = messages.BooleanField(7)
    next = messages.BooleanField(8)
    currentRound = messages.IntegerField(17, variant=messages.Variant.INT32)
    currentRoundPositioning = messages.BooleanField(18)
    currentRoundCombat = messages.BooleanField(19)
    currentRoundResults = messages.BooleanField(20)


SEASON_RESOURCE = endpoints.ResourceContainer(
    SeasonRequest
)

class SeasonCollection(messages.Message):
    """ multiple seasons """
    seasons = messages.MessageField(SeasonResponse, 1, repeated=True)
    response_message = messages.StringField(40)
    response_successful = messages.BooleanField(50)

class SeasonCollectionRequest(messages.Message):
    """ a season collection request's data """
    cursor = messages.StringField(1)
    sort_order = messages.StringField(2)
    direction = messages.StringField(3)

SEASON_COLLECTION_PAGE_RESOURCE = endpoints.ResourceContainer(
    SeasonCollectionRequest
)
