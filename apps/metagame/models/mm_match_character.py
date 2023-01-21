import endpoints
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types

## the mm match character contains data for a character in a single match
## it gets tallied up by tasks later to come up with character and seasonal results

class MMMatchCharacter(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    # general user info
    title = ndb.StringProperty(indexed=False)

    # connection to user and character
    userKeyId = ndb.IntegerProperty(indexed=True)
    characterKeyId = ndb.IntegerProperty(indexed=True)
    seasonCharacterKeyId = ndb.IntegerProperty(indexed=True)

    # this is the uetopia gamePlayerKeyId - also primarily stored in users
    uetopia_playerKeyId = ndb.IntegerProperty(indexed=True)
    # this is the uetopia characterKeyId
    uetopia_characterKeyId = ndb.IntegerProperty(indexed=True)

    # connections to the match
    mmmatchKeyId = ndb.IntegerProperty(indexed=True)
    mmmatchTitle = ndb.StringProperty(indexed=False)
    mapTitle = ndb.StringProperty(indexed=False)
    matchType = ndb.StringProperty(indexed=False)

    # connections to season
    seasonKeyId = ndb.IntegerProperty(indexed=True)
    seasonTitle = ndb.StringProperty(indexed=False)

    damage_dealt = ndb.IntegerProperty(indexed=False)
    ## TODO: Insert all of your custom variables.
    damage_received = ndb.IntegerProperty(indexed=False)
    kills = ndb.IntegerProperty(indexed=False)
    assists = ndb.IntegerProperty(indexed=False)
    deaths = ndb.IntegerProperty(indexed=False)
    rank = ndb.IntegerProperty(indexed=False)
    score  = ndb.IntegerProperty(indexed=False)
    level  = ndb.IntegerProperty(indexed=False)

    matches_played = ndb.IntegerProperty(indexed=False)
    mm1v1_played = ndb.IntegerProperty(indexed=False)
    mm2v2_played = ndb.IntegerProperty(indexed=False)
    mm3v3_played = ndb.IntegerProperty(indexed=False)
    mm4v4_played = ndb.IntegerProperty(indexed=False)

    matches_won = ndb.IntegerProperty(indexed=False)
    mm1v1_won = ndb.IntegerProperty(indexed=False)
    mm2v2_won = ndb.IntegerProperty(indexed=False)
    mm3v3_won = ndb.IntegerProperty(indexed=False)
    mm4v4_won = ndb.IntegerProperty(indexed=False)


    # raw JSON capture
    raw_json = ndb.TextProperty(indexed=False)



### PROTORPC MODELS FOR ENDPOINTS
### These are used to specify incoming and outgoing variables from the endpoints API
class MMMatchCharacterResponse(messages.Message):
    """ a mm match character's data """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32)
    title = messages.StringField(2)
    description = messages.StringField(3)
    characterKeyId = messages.IntegerField(4, variant=messages.Variant.INT32)
    uetopia_playerKeyId = messages.IntegerField(5, variant=messages.Variant.INT32)
    damage_dealt = messages.IntegerField(6, variant=messages.Variant.INT32)
    ## TODO: Insert all of your custom variables.
    damage_received = messages.IntegerField(16, variant=messages.Variant.INT32)
    kills = messages.IntegerField(26, variant=messages.Variant.INT32)
    assists = messages.IntegerField(27, variant=messages.Variant.INT32)
    deaths = messages.IntegerField(28, variant=messages.Variant.INT32)
    rank = messages.IntegerField(30, variant=messages.Variant.INT32)
    score = messages.IntegerField(31, variant=messages.Variant.INT32)
    level = messages.IntegerField(32, variant=messages.Variant.INT32)
    matches_played = messages.IntegerField(33, variant=messages.Variant.INT32)
    mm1v1_played = messages.IntegerField(34, variant=messages.Variant.INT32)
    mm2v2_played = messages.IntegerField(35, variant=messages.Variant.INT32)
    mm3v3_played = messages.IntegerField(36, variant=messages.Variant.INT32)
    mm4v4_played = messages.IntegerField(37, variant=messages.Variant.INT32)
    matches_won = messages.IntegerField(38, variant=messages.Variant.INT32)
    mm1v1_won = messages.IntegerField(39, variant=messages.Variant.INT32)
    mm2v2_won = messages.IntegerField(40, variant=messages.Variant.INT32)
    mm3v3_won = messages.IntegerField(41, variant=messages.Variant.INT32)
    mm4v4_won = messages.IntegerField(42, variant=messages.Variant.INT32)

    mmmatchKeyId = messages.IntegerField(50, variant=messages.Variant.INT32)
    mmmatchTitle = messages.StringField(51)
    mapTitle = messages.StringField(52)
    matchType = messages.StringField(53)

    response_message = messages.StringField(150)
    response_successful = messages.BooleanField(160)



class MMMatchCharacterRequest(messages.Message):
    """ a mm match character get request """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32)
    characterKeyId = messages.IntegerField(2, variant=messages.Variant.INT32)


MMMATCH_CHARACTER_RESOURCE = endpoints.ResourceContainer(
    MMMatchCharacterRequest
)

class MMMatchCharacterCollection(messages.Message):
    """ multiple mmmatch Characteres """
    mm_match_characters = messages.MessageField(MMMatchCharacterResponse, 1, repeated=True)
    response_message = messages.StringField(40)
    response_successful = messages.BooleanField(50)

class MMMatchCharacterCollectionRequest(messages.Message):
    """ a Character collection request's data """
    characterKeyId = messages.IntegerField(1, variant=messages.Variant.INT32)
    cursor = messages.StringField(2)
    sort_order = messages.StringField(3)
    direction = messages.StringField(4)

MMMATCH_CHARACTER_COLLECTION_PAGE_RESOURCE = endpoints.ResourceContainer(
    MMMatchCharacterCollectionRequest
)
