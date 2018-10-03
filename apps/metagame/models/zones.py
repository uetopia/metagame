import endpoints
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types

class Zones(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    # general user info
    title = ndb.StringProperty(indexed=False)
    description = ndb.TextProperty(indexed=False)
    engine_travel_url = ndb.StringProperty(indexed=False)

    # coonections to season and region
    mapKeyId = ndb.IntegerProperty(indexed=True)
    mapTitle = ndb.StringProperty(indexed=False)
    seasonKeyId = ndb.IntegerProperty(indexed=True)
    seasonTitle = ndb.StringProperty(indexed=False)
    seasonActive = ndb.BooleanProperty(indexed=True)
    regionKeyId = ndb.IntegerProperty(indexed=True)
    regionTitle = ndb.StringProperty(indexed=False)
    regionDatacenterLocation = ndb.StringProperty(indexed=False)

    ## Defender connections
    controlled = ndb.BooleanProperty(indexed=False)
    factionKeyId = ndb.IntegerProperty(indexed=True)
    factionTag = ndb.StringProperty(indexed=False)
    userCaptainKeyId = ndb.IntegerProperty(indexed=True)
    userCaptainTitle = ndb.StringProperty(indexed=False)
    uetopiaGamePlayerKeyId = ndb.IntegerProperty(indexed=False)
    teamTitle = ndb.StringProperty(indexed=False)

    horizontalIndex = ndb.IntegerProperty(indexed=True)
    verticalIndex = ndb.IntegerProperty(indexed=True)

    energy = ndb.IntegerProperty(indexed=False)
    materials = ndb.IntegerProperty(indexed=False)
    control = ndb.IntegerProperty(indexed=False)
    validZone = ndb.BooleanProperty(indexed=False)


    def to_json(self):

        if self.title:
            title = self.title.encode('utf-8')
        else:
            title = ''

        return ({
                u'key_id': self.key.id(),
                u'title': title,
                u'horizontalIndex': self.horizontalIndex,
                u'verticalIndex':self.verticalIndex,
                u'energy': self.energy,
                u'materials': self.materials,
                u'control': self.control,
                u'validZone': self.validZone,
                u'controlled': self.controlled,
                u'factionTag': self.factionTag,
                u'teamTitle': self.teamTitle,
                u'regionKeyId': self.regionKeyId,
                u'mapKeyId': self.mapKeyId,
                u'mapTitle': self.mapTitle,
                u'userCaptainKeyId': self.userCaptainKeyId
        })


### PROTORPC MODELS FOR ENDPOINTS
### These are used to specify incoming and outgoing variables from the endpoints API
class ZoneResponse(messages.Message):
    """ a map's data """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32)
    title = messages.StringField(2)
    created = messages.StringField(3) ## DATETIME

    response_message = messages.StringField(113)
    response_successful = messages.BooleanField(114)


class ZoneRequest(messages.Message):
    """ a map's updates """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32)
    title = messages.StringField(2)
    description = messages.StringField(3)
    mapKeyId = messages.IntegerField(19, variant=messages.Variant.INT32)
    seasonKeyId = messages.IntegerField(20, variant=messages.Variant.INT32)
    regionKeyId = messages.IntegerField(22, variant=messages.Variant.INT32)
    horizontalIndex = messages.IntegerField(6, variant=messages.Variant.INT32)
    verticalIndex = messages.IntegerField(7, variant=messages.Variant.INT32)
    energy = messages.IntegerField(8, variant=messages.Variant.INT32)
    materials = messages.IntegerField(9, variant=messages.Variant.INT32)
    control = messages.IntegerField(10, variant=messages.Variant.INT32)
    validZone = messages.BooleanField(11)
    engine_travel_url = messages.StringField(12)


ZONE_RESOURCE = endpoints.ResourceContainer(
    ZoneRequest
)

class ZoneCollection(messages.Message):
    """ multiple zones """
    zones = messages.MessageField(ZoneResponse, 1, repeated=True)
    response_message = messages.StringField(40)
    response_successful = messages.BooleanField(50)

class ZoneCollectionRequest(messages.Message):
    """ a zone collection request's data """
    cursor = messages.StringField(1)
    sort_order = messages.StringField(2)
    direction = messages.StringField(3)
    mapKeyId = messages.IntegerField(5, variant=messages.Variant.INT32)

ZONE_COLLECTION_PAGE_RESOURCE = endpoints.ResourceContainer(
    ZoneCollectionRequest
)
