import endpoints
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types

from apps.metagame.models.mm_match_character import MMMatchCharacterResponse
## the mm match is one of the regular matchmaker matches
## it does not affect the metaGame
## it is only for states

class MMMatch(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    # general match info
    title = ndb.StringProperty(indexed=False)
    description = ndb.TextProperty(indexed=False) ## GameStory
    matchType = ndb.StringProperty(indexed=False)
    mapTitle = ndb.StringProperty(indexed=False)

    # incoming match key from uetopia
    uetopiaMatchKeyId = ndb.IntegerProperty(indexed=True)

    # connections to season and region
    seasonKeyId = ndb.IntegerProperty(indexed=True)
    seasonTitle = ndb.StringProperty(indexed=False)
    #regionKeyId = ndb.IntegerProperty(indexed=True)
    #regionTitle = ndb.StringProperty(indexed=False)
    regionDatacenterLocation = ndb.StringProperty(indexed=False)

    # connections to the user, party and faction

    # final stats
    winningTeamTitle = ndb.StringProperty(indexed=False)
    losingTeamTitle = ndb.StringProperty(indexed=False)

    # raw JSON capture
    raw_json = ndb.TextProperty(indexed=False)



### PROTORPC MODELS FOR ENDPOINTS
### These are used to specify incoming and outgoing variables from the endpoints API
class MMMatchResponse(messages.Message):
    """ a mmmatch's data """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32)
    title = messages.StringField(2)
    description = messages.StringField(3)
    matchType = messages.StringField(4)
    mapTitle = messages.StringField(5)

    uetopiaMatchKeyId = messages.IntegerField(7, variant=messages.Variant.INT32)
    seasonKeyId = messages.IntegerField(8, variant=messages.Variant.INT32)
    seasonTitle = messages.StringField(9)

    regionDatacenterLocation = messages.StringField(13)
    winningTeamTitle = messages.StringField(14)
    losingTeamTitle = messages.StringField(15)

    created = messages.StringField(21)

    winningTeam = messages.MessageField(MMMatchCharacterResponse, 50, repeated=True)
    losingTeam = messages.MessageField(MMMatchCharacterResponse, 51, repeated=True)

    response_message = messages.StringField(113)
    response_successful = messages.BooleanField(114)


class MMMatchRequest(messages.Message):
    """ a mmmatch updates """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32)
    title = messages.StringField(2)
    description = messages.StringField(3)
    matchType = messages.StringField(4)
    mapTitle = messages.StringField(5)

    uetopiaMatchKeyId = messages.IntegerField(7, variant=messages.Variant.INT32)
    seasonKeyId = messages.IntegerField(8, variant=messages.Variant.INT32)
    seasonTitle = messages.StringField(9)

    regionDatacenterLocation = messages.StringField(13)
    winningTeamTitle = messages.StringField(14)
    losingTeamTitle = messages.StringField(15)

    created = messages.StringField(21)


MMMATCH_RESOURCE = endpoints.ResourceContainer(
    MMMatchRequest
)

class MMMatchCollection(messages.Message):
    """ multiple mmmatches """
    mm_matches = messages.MessageField(MMMatchResponse, 1, repeated=True)
    response_message = messages.StringField(40)
    response_successful = messages.BooleanField(50)

class MMMatchCollectionRequest(messages.Message):
    """ a region collection request's data """
    cursor = messages.StringField(1)
    sort_order = messages.StringField(2)
    direction = messages.StringField(3)

MMMATCH_COLLECTION_PAGE_RESOURCE = endpoints.ResourceContainer(
    MMMatchCollectionRequest
)
