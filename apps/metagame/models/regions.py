import endpoints
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types

class Regions(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    # general user info
    title = ndb.StringProperty(indexed=False)
    description = ndb.TextProperty(indexed=False)

    # datacenter location
    datacenter_location = ndb.StringProperty(indexed=True)

    # TODO - optional play start/end times?


    ## TODO - store any extra information about your Region

    def to_json(self):
        return ({
            u'title': self.title,
            u'description': self.description
        })




### PROTORPC MODELS FOR ENDPOINTS
### These are used to specify incoming and outgoing variables from the endpoints API
class RegionResponse(messages.Message):
    """ a region's data """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32)
    title = messages.StringField(2)

    response_message = messages.StringField(113)
    response_successful = messages.BooleanField(114)


class RegionRequest(messages.Message):
    """ a users updates """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32)
    title = messages.StringField(2)
    description = messages.StringField(3)
    datacenter_location = messages.StringField(4)


REGION_RESOURCE = endpoints.ResourceContainer(
    RegionRequest
)

class RegionCollection(messages.Message):
    """ multiple regions """
    regions = messages.MessageField(RegionResponse, 1, repeated=True)
    response_message = messages.StringField(40)
    response_successful = messages.BooleanField(50)

class RegionCollectionRequest(messages.Message):
    """ a region collection request's data """
    cursor = messages.StringField(1)
    sort_order = messages.StringField(2)
    direction = messages.StringField(3)

REGION_COLLECTION_PAGE_RESOURCE = endpoints.ResourceContainer(
    RegionCollectionRequest
)
