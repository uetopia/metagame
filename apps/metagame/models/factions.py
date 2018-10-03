import endpoints
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types

class Factions(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    # general faction info
    tag = ndb.StringProperty(indexed=False)
    title = ndb.StringProperty(indexed=False)
    description = ndb.TextProperty(indexed=False)

    uetopia_groupKeyId = ndb.IntegerProperty(indexed=True)

    # keep track of the active season so we can clear it out at the end.
    activeSeasonKeyId = ndb.IntegerProperty(indexed=True)

    ## metagame values - these get reset for each new season.
    energy = ndb.IntegerProperty(indexed=False)
    materials = ndb.IntegerProperty(indexed=False)
    control = ndb.IntegerProperty(indexed=True)

    ## TODO - store any extra information about your faction

    def to_json(self):
        return ({
            u'key_id': self.key.id(),
            u'title': self.title,
            u'description': self.description,
            u'tag': self.tag,
            u'energy': self.energy,
            u'materials': self.materials,
            u'control':self.control
        })

    def to_json_with_zones(self):
        return ({
            u'key_id': self.key.id(),
            u'title': self.title,
            u'description': self.description,
            u'tag': self.tag,
            u'energy': self.energy,
            u'materials': self.materials,
            u'control':self.control,
            u'zones': self.zones
        })




### PROTORPC MODELS FOR ENDPOINTS
### These are used to specify incoming and outgoing variables from the endpoints API
class FactionResponse(messages.Message):
    """ a faction's data """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32)
    title = messages.StringField(2)

class FactionRequest(messages.Message):
    """ a faction's updates """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32)


FACTION_RESOURCE = endpoints.ResourceContainer(
    FactionRequest
)
