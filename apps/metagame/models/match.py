import endpoints
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types

class Match(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    # general user info
    title = ndb.StringProperty(indexed=False)

    # connections to season and region
    zoneKeyId = ndb.IntegerProperty(indexed=True)
    zoneTitle = ndb.StringProperty(indexed=False)
    mapKeyId = ndb.IntegerProperty(indexed=True)
    mapTitle = ndb.StringProperty(indexed=False)
    seasonKeyId = ndb.IntegerProperty(indexed=True)
    seasonTitle = ndb.StringProperty(indexed=False)
    regionKeyId = ndb.IntegerProperty(indexed=True)
    regionTitle = ndb.StringProperty(indexed=False)
    regionDatacenterLocation = ndb.StringProperty(indexed=False)

    # connections to the user, party and faction
    # DEFENDER
    defenderTeamKeyId = ndb.IntegerProperty(indexed=False)
    defenderTeamTitle = ndb.StringProperty(indexed=False)
    defenderFactionKeyId = ndb.IntegerProperty(indexed=True)
    defenderFactionTitle = ndb.StringProperty(indexed=False)
    defenderFactionTag = ndb.StringProperty(indexed=False)
    defenderUserKeyId = ndb.IntegerProperty(indexed=False)
    defenderUserTitle = ndb.StringProperty(indexed=False)
    defenderUetopiaGamePlayerKeyId = ndb.IntegerProperty(indexed=False) ## the key to use for offsite identification of this player
    # ATTACKER
    attackerTeamKeyId = ndb.IntegerProperty(indexed=False)
    attackerTeamTitle = ndb.StringProperty(indexed=False)
    attackerFactionKeyId = ndb.IntegerProperty(indexed=True)
    attackerFactionTitle = ndb.StringProperty(indexed=False)
    attackerFactionTag = ndb.StringProperty(indexed=False)
    attackerUserKeyId = ndb.IntegerProperty(indexed=False)
    attackerUserTitle = ndb.StringProperty(indexed=False)
    attackerUetopiaGamePlayerKeyId = ndb.IntegerProperty(indexed=False) ## the key to use for offsite identification of this player

    # final stats - TODO store snapshots along the way for data mining
    winningUserKeyId = ndb.IntegerProperty(indexed=False)
    winningUserTitle = ndb.StringProperty(indexed=False)
    winningTeamTitle = ndb.StringProperty(indexed=False)
    winningFactionKeyId = ndb.IntegerProperty(indexed=True)
    winningFactionTitle = ndb.StringProperty(indexed=False)
    winningUetopiaGamePlayerKeyId = ndb.IntegerProperty(indexed=False)

    active = ndb.BooleanProperty(indexed=True)
    verified = ndb.BooleanProperty(indexed=True)
    expired = ndb.BooleanProperty(indexed=True)
