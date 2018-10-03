import endpoints
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types

class Bids(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    # connections to season and region
    zoneKeyId = ndb.IntegerProperty(indexed=True)
    zoneTitle = ndb.StringProperty(indexed=False)
    mapKeyId = ndb.IntegerProperty(indexed=True)
    mapTitle = ndb.StringProperty(indexed=False)
    seasonKeyId = ndb.IntegerProperty(indexed=True)
    seasonTitle = ndb.StringProperty(indexed=False)
    seasonActive = ndb.BooleanProperty(indexed=True)
    regionKeyId = ndb.IntegerProperty(indexed=True)
    regionTitle = ndb.StringProperty(indexed=False)

    # connections to the user, party and faction
    teamKeyId = ndb.IntegerProperty(indexed=False)
    teamTitle = ndb.StringProperty(indexed=False)
    factionKeyId = ndb.IntegerProperty(indexed=True)
    factionTitle = ndb.StringProperty(indexed=False)
    factionTag = ndb.StringProperty(indexed=False)
    userKeyId = ndb.IntegerProperty(indexed=True)
    userTitle = ndb.StringProperty(indexed=False)
    uetopiaGamePlayerKeyId = ndb.IntegerProperty(indexed=False)

    roundIndex = ndb.IntegerProperty(indexed=True)

    bidAmount = ndb.IntegerProperty(indexed=False)

    highBid = ndb.BooleanProperty(indexed=False)
    bidProcessed = ndb.BooleanProperty(indexed=True)
    bidReturned = ndb.BooleanProperty(indexed=False)


### PROTORPC MODELS FOR ENDPOINTS
### These are used to specify incoming and outgoing variables from the endpoints API
class BidResponse(messages.Message):
    """ a bid's data """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32)
    bidAmount = messages.IntegerField(2, variant=messages.Variant.INT32)
    created = messages.StringField(3) ## DATETIME

    response_message = messages.StringField(113)
    response_successful = messages.BooleanField(114)


class BidRequest(messages.Message):
    """ a bids's updates """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32)
    zoneKeyId = messages.IntegerField(18, variant=messages.Variant.INT32)
    bidAmount = messages.IntegerField(6, variant=messages.Variant.INT32)


BID_RESOURCE = endpoints.ResourceContainer(
    BidRequest
)
