import endpoints
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types

class Maps(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    # general user info
    title = ndb.StringProperty(indexed=False)
    description = ndb.TextProperty(indexed=False)

    # coonections to season and region
    seasonKeyId = ndb.IntegerProperty(indexed=True)
    seasonTitle = ndb.StringProperty(indexed=False)
    seasonActive = ndb.BooleanProperty(indexed=True)
    regionKeyId = ndb.IntegerProperty(indexed=True)
    regionTitle = ndb.StringProperty(indexed=False)
    regionDatacenterLocation = ndb.StringProperty(indexed=False)

    zoneCountHorizontal = ndb.IntegerProperty(indexed=False)
    zoneCountVertical = ndb.IntegerProperty(indexed=False)

    # final stats - TODO store snapshots along the way for data mining
    winningFactionKeyId = ndb.IntegerProperty(indexed=True)
    winningFactionTitle = ndb.StringProperty(indexed=False)

    def to_json(self):

        if self.title:
            title = self.title.encode('utf-8')
        else:
            title = ''

        return ({
                u'key_id': self.key.id(),
                u'title': title,
                u'description': self.description,
                u'seasonActive':self.seasonActive,
                u'winningFactionKeyId': self.winningFactionKeyId,
                u'winningFactionTitle': self.winningFactionTitle,
                u'zones': self.zones
        })




### PROTORPC MODELS FOR ENDPOINTS
### These are used to specify incoming and outgoing variables from the endpoints API
class MapResponse(messages.Message):
    """ a map's data """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32)
    title = messages.StringField(2)
    created = messages.StringField(3) ## DATETIME

    response_message = messages.StringField(113)
    response_successful = messages.BooleanField(114)


class MapRequest(messages.Message):
    """ a map's updates """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32)
    title = messages.StringField(2)
    description = messages.StringField(3)
    seasonKeyId = messages.IntegerField(4, variant=messages.Variant.INT32)
    regionKeyId = messages.IntegerField(5, variant=messages.Variant.INT32)
    zoneCountHorizontal = messages.IntegerField(6, variant=messages.Variant.INT32)
    zoneCountVertical = messages.IntegerField(7, variant=messages.Variant.INT32)


MAP_RESOURCE = endpoints.ResourceContainer(
    MapRequest
)

class MapCollection(messages.Message):
    """ multiple maps """
    maps = messages.MessageField(MapResponse, 1, repeated=True)
    response_message = messages.StringField(40)
    response_successful = messages.BooleanField(50)

class MapCollectionRequest(messages.Message):
    """ a region collection request's data """
    cursor = messages.StringField(1)
    sort_order = messages.StringField(2)
    direction = messages.StringField(3)
    regionKeyId = messages.IntegerField(5, variant=messages.Variant.INT32)

MAP_COLLECTION_PAGE_RESOURCE = endpoints.ResourceContainer(
    MapCollectionRequest
)
