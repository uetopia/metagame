import endpoints
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types

from apps.metagame.models.season_characters import SeasonCharacterResponse

class Characters(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    # general character info
    title = ndb.StringProperty(indexed=False)
    description = ndb.TextProperty(indexed=False)

    # link back to user
    userKeyId = ndb.IntegerProperty(indexed=True)

    # this is the uetopia gamePlayerKeyId - also primarily stored in users
    uetopia_playerKeyId = ndb.IntegerProperty(indexed=True)
    # this is the uetopia characterKeyId
    uetopia_characterKeyId = ndb.IntegerProperty(indexed=True)

    # keep track of all stats for this character
    # this is like career stats - all time
    damage_dealt = ndb.IntegerProperty(indexed=False)
    ## TODO: Insert all of your custom variables.
    damage_received = ndb.IntegerProperty(indexed=False)
    kills = ndb.IntegerProperty(indexed=False)
    assists = ndb.IntegerProperty(indexed=False)
    deaths = ndb.IntegerProperty(indexed=False)
    rank = ndb.IntegerProperty(indexed=True)
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

    # Copied downstream from User
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
            u'userKeyId': self.uetopia_connected,
            u'damage_dealt': self.damage_dealt,
            ## TODO: Insert all of your custom variables.
            u'damage_received': self.damage_received,
            u'kills': self.kills,
            u'assists': self.assists,
            u'deaths': self.deaths,
            u'rank': self.rank,
            u'score': self.score,
            u'level': self.level,
            u'matches_played': self.matches_played,
            u'mm1v1_played': self.mm1v1_played,
            u'mm2v2_played': self.mm2v2_played,
            u'mm3v3_played': self.mm3v3_played,
            u'mm4v4_played': self.mm4v4_played,
            u'matches_won': self.matches_won,
            u'mm1v1_won': self.mm1v1_won,
            u'mm2v2_won': self.mm2v2_won,
            u'mm3v3_won': self.mm3v3_won,
            u'mm4v4_won': self.mm4v4_won
        })

    def to_json_thin(self):
        return ({
            u'key_id': self.key.id(),
            u'title': self.title,
            u'damage_dealt': self.damage_dealt,
            u'kills': self.kills,
            u'deaths': self.deaths,
            u'rank': self.rank,
            u'score': self.score,
            u'level': self.level
        })



### PROTORPC MODELS FOR ENDPOINTS
### These are used to specify incoming and outgoing variables from the endpoints API
class CharacterResponse(messages.Message):
    """ a character's data """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32)
    title = messages.StringField(2)
    description = messages.StringField(3)
    #userKeyId = messages.IntegerField(4)
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

    season_characters = messages.MessageField(SeasonCharacterResponse, 50, repeated=True)

    active_season_key_id = messages.IntegerField(51, variant=messages.Variant.INT32)

    response_message = messages.StringField(150)
    response_successful = messages.BooleanField(160)



class CharacterRequest(messages.Message):
    """ a character get request """
    key_id = messages.IntegerField(1, variant=messages.Variant.INT32)


CHARACTER_RESOURCE = endpoints.ResourceContainer(
    CharacterRequest
)
