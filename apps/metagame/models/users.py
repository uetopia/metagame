import endpoints
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types

class Users(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    # general user info
    title = ndb.StringProperty(indexed=False)
    description = ndb.TextProperty(indexed=False)

    # Firebase auth
    firebaseUser = ndb.StringProperty(indexed=True)

    # has the user connected to uetopia
    uetopia_connected = ndb.BooleanProperty(indexed=False)
    uetopia_playerKeyId = ndb.IntegerProperty(indexed=True)

    # can this user view the admin interface - be careful!
    admin = ndb.BooleanProperty(indexed=False)

    # is the user currently active?  In-game with matchmaker meta mode active.
    metaGameActive = ndb.BooleanProperty(indexed=False)

    # team captains are only allowed to take one action per round.
    roundActionUsed = ndb.BooleanProperty(indexed=True)

    # Users can belong to multiple factions (groups), but can only be active in one at a time.
    currentFactionKeyId = ndb.IntegerProperty(indexed=True)
    currentFactionTag = ndb.StringProperty(indexed=False)
    currentFactionLead = ndb.BooleanProperty(indexed=True)
    currentFactionTeamLead = ndb.BooleanProperty(indexed=False)

    # Team Information
    currentTeamKeyId = ndb.IntegerProperty(indexed=False)
    currentTeamCaptain = ndb.BooleanProperty(indexed=False)
    currentTeamTitle = ndb.StringProperty(indexed=False)

    # Zone information
    holdingZoneKeyId = ndb.IntegerProperty(indexed=False)
    holdingZone = ndb.BooleanProperty(indexed=False)
    holdingZoneTitle = ndb.StringProperty(indexed=False)

    ## TODO - store any extra information about your players

    def to_json(self):
        return ({
            u'key_id': self.key.id(),
            u'title': self.title,
            u'description': self.description,
            u'uetopia_connected': self.uetopia_connected,
            u'admin': self.admin,
            u'metaGameActive': self.metaGameActive,
            u'roundActionUsed':self.roundActionUsed,
            u'currentFactionTag': self.currentFactionTag,
            u'currentFactionLead': self.currentFactionLead,
            u'currentFactionTeamLead': self.currentFactionTeamLead,
            u'currentTeamCaptain':self.currentTeamCaptain,
            u'holdingZoneKeyId': self.holdingZoneKeyId,
            u'holdingZone': self.holdingZone,
            u'holdingZoneTitle': self.holdingZoneTitle
        })



### PROTORPC MODELS FOR ENDPOINTS
### These are used to specify incoming and outgoing variables from the endpoints API
class UserResponse(messages.Message):
    """ a user's data """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32)
    title = messages.StringField(2)
    uetopia_connected = messages.BooleanField(6)

class UserRequest(messages.Message):
    """ a users updates """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32)
    security_code = messages.StringField(2)


USER_RESOURCE = endpoints.ResourceContainer(
    UserRequest
)
