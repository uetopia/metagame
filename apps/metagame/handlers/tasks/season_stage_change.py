import endpoints
import logging
import uuid
import time
import json
import hashlib
import hmac
import urllib
import httplib
import random
from collections import OrderedDict
from httplib2 import Http
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
from protorpc import remote
from protorpc import message_types
from google.appengine.datastore.datastore_query import Cursor
from oauth2client.contrib.appengine import AppAssertionCredentials
from oauth2client.client import GoogleCredentials
from protorpc import remote
from google.appengine.api import taskqueue

from apps.handlers import BaseHandler

from apps.metagame.controllers.maps import MapsController
from apps.metagame.controllers.zones import ZonesController
from apps.metagame.controllers.seasons import SeasonsController
from apps.metagame.controllers.regions import RegionsController
from apps.metagame.controllers.users import UsersController
from apps.metagame.controllers.bids import BidsController
from apps.metagame.controllers.factions import FactionsController
from apps.metagame.controllers.match import MatchController
from apps.metagame.controllers.achievements import AchievementsController

from configuration import *

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']

class SeasonStageChangeHandler(BaseHandler):
    def get(self):

        return self.post()

    def post(self):
        logging.info("[TASK] SeasonStageChangeHandler")

        ## just use the active season
        #key_id = self.request.get('key_id')

        mapController = MapsController()
        zoneController = ZonesController()
        bidController = BidsController()
        seasonController = SeasonsController()
        factionsController = FactionsController()
        matchController = MatchController()
        usersController = UsersController()
        achievementController = AchievementsController()

        season = seasonController.get_active()
        if not season:
            logging.error('Season not found')
            return

        if not season.active:
            logging.error('Season not active')
            return

        ## Keep track of any factions that need bids refunded.
        refunding_faction_key_id_list = []

        ## which stage are we currently on?
        if season.currentRoundPositioning:
            logging.info('currentRoundPositioning')

            ## - GO through each map
            ## - - Go through each zone
            ## - - - Find the high bid, timestamp if equal
            ## - - - Refund all other bids
            ## - - - - mark it as not high bid, add the faction to the task list, and process all refunds in a separate task for ech faction separately.
            ## - - - High bids with a defender - Fire off API call to start the match
            ## - - - Otherwise, team/faction/user takes control of the cell.
            ## - - Update the map
            ## Update the Season

            ##  - Go through each map
            maps_for_this_season = mapController.list_by_seasonKeyId(season.key.id())

            for map in maps_for_this_season:
                logging.info('processing map: %s' % map.title)

                zones = zoneController.list_by_mapKeyId(map.key.id())

                for zone in zones:
                    logging.info('processing zone: %s' %zone.title)

                    ## get bids in reverse chrono - this way OLDER greater or equal bids can always push out NEWER bids
                    bids = bidController.list_by_zoneKeyId(zone.key.id())
                    logging.info('found %s bids' % len(bids))

                    if len(bids) > 0:
                        high_bid = None
                        high_bid_amount = 0

                        ## This is a little confusing.
                        ## We are checking if the bid in the loop is greater than the previous
                        ## If it is, we are marking this one as "highest" - marking the previous as "not highest" and "processed"
                        ## if it's not, we mark it as "processed" so it can get picked up in the faction refund task

                        for bid in bids:
                            if bid.bidAmount >= high_bid_amount:
                                logging.info('found new high bid')
                                # if there is a previous high bid, mark it as not high bid anymore
                                if high_bid:
                                    logging.info('marking previous high bid processed')
                                    high_bid.highBid = False
                                    high_bid.bidProcessed = True

                                ## add the faction key to the list, if it's not already there
                                if bid.factionKeyId not in refunding_faction_key_id_list:
                                    refunding_faction_key_id_list.append(bid.factionKeyId)

                                bid.highBid = True
                                bid.bidProcessed = True

                                high_bid = bid
                                high_bid_amount = bid.bidAmount
                            else:
                                logging.info('found a lower bid')
                                bid.highBid = False
                                bid.bidProcessed = True


                                ## add the faction key to the list, if it's not already there
                                if bid.factionKeyId not in refunding_faction_key_id_list:
                                    refunding_faction_key_id_list.append(bid.factionKeyId)

                        # save
                        for bid in bids:
                            bidController.update(bid)

                        ## Now we have the highest bid in the high_bid variable
                        ## does this zone have a defender?
                        if zone.controlled:
                            logging.info('this zone is controlled')

                            ## also make sure that the defender is still active.  They may have gone offline or something
                            defending_user_captain = usersController.get_by_key_id(zone.userCaptainKeyId)
                            if defending_user_captain and defending_user_captain.metaGameActive:
                                logging.info('defender is still online')



                                ## Create a match record for this, associate with teams factions and zone.
                                match = matchController.create(
                                    title = zone.title,
                                    zoneKeyId = zone.key.id(),
                                    zoneTitle = zone.title,
                                    mapKeyId = zone.mapKeyId,
                                    mapTitle = zone.mapTitle,
                                    seasonKeyId = zone.seasonKeyId,
                                    seasonTitle = zone.seasonTitle,
                                    regionKeyId = zone.regionKeyId,
                                    regionTitle = zone.regionTitle,
                                    regionDatacenterLocation = zone.regionDatacenterLocation,
                                    #defenderTeamKeyId = zone.,
                                    defenderTeamTitle = zone.teamTitle,
                                    defenderFactionKeyId = zone.factionKeyId,
                                    #defenderFactionTitle = zone.,
                                    defenderFactionTag = zone.factionTag,
                                    defenderUserKeyId = zone.userCaptainKeyId,
                                    defenderUserTitle = zone.userCaptainTitle,
                                    defenderUetopiaGamePlayerKeyId = zone.uetopiaGamePlayerKeyId,
                                    attackerTeamKeyId = high_bid.teamKeyId,
                                    attackerTeamTitle = high_bid.teamTitle,
                                    attackerFactionKeyId = high_bid.factionKeyId,
                                    attackerFactionTitle = high_bid.factionTitle,
                                    attackerFactionTag = high_bid.factionTag,
                                    attackerUserKeyId = high_bid.userKeyId,
                                    attackerUserTitle = high_bid.userTitle,
                                    attackerUetopiaGamePlayerKeyId = high_bid.uetopiaGamePlayerKeyId,
                                    active = True,
                                    verified = False,
                                    expired = False,
                                )

                                ## TODO - fire matchmaker API call

                                uri = "/api/v1/game/metagame/match_begin"

                                params = OrderedDict([
                                          ("nonce", time.time()),
                                          ("encryption", "sha512"),
                                          ("attackingPlayerKeyId", match.attackerUetopiaGamePlayerKeyId),
                                          ("defendingPlayerKeyId", match.defenderUetopiaGamePlayerKeyId),
                                          #("gameModeKeyId", match.regionTitle),
                                          ("region", match.regionDatacenterLocation ),
                                          ("metaMatchKeyId", match.key.id() )
                                          ])

                                params = urllib.urlencode(params)

                                # Hash the params string to produce the Sign header value
                                H = hmac.new(UETOPIA_ASSIGNED_GAME_API_SECRET, digestmod=hashlib.sha512)
                                H.update(params)
                                sign = H.hexdigest()

                                headers = {"Content-type": "application/x-www-form-urlencoded",
                                                   "Key":UETOPIA_ASSIGNED_GAME_API_KEY,
                                                   "Sign":sign}

                                conn = httplib.HTTPSConnection(UETOPIA_API_URL)

                                conn.request("POST", uri, params, headers)
                                response = conn.getresponse()

                                #logging.info(response.read())

                                ## parse the response
                                jsonstring = str(response.read())
                                logging.info(jsonstring)
                                jsonobject = json.loads(jsonstring)

                                # do something with the response
                                if not jsonobject['request_successful']:
                                    logging.info('the validation request was unsuccessful')

                                    return

                                logging.info('validation was successful')

                            else:
                                logging.info('Defender was not online')

                                zone.controlled = True
                                zone.factionKeyId = bid.factionKeyId
                                zone.factionTag = bid.factionTag
                                zone.userCaptainKeyId = bid.userKeyId
                                zone.userCaptainTitle = bid.userTitle
                                zone.uetopiaGamePlayerKeyId = bid.uetopiaGamePlayerKeyId
                                zone.teamTitle = bid.teamTitle

                                # save
                                zoneController.update(zone)


                        else:
                            logging.info('Not controlled')

                            zone.controlled = True
                            zone.factionKeyId = bid.factionKeyId
                            zone.factionTag = bid.factionTag
                            zone.userCaptainKeyId = bid.userKeyId
                            zone.userCaptainTitle = bid.userTitle
                            zone.uetopiaGamePlayerKeyId = bid.uetopiaGamePlayerKeyId
                            zone.teamTitle = bid.teamTitle

                            # save
                            zoneController.update(zone)

                            # also update the user so we have the controlled map id

                ## Update Map
                ## push out to firebase
                taskUrl='/task/map/firebase/update'
                taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': map.key.id()}, countdown = 2,)


            ## update season
            season.currentRoundCombat = True
            season.currentRoundPositioning = False
            season.currentRoundResults = False

            # save
            seasonController.update(season)

            ## push out to firebase
            taskUrl='/task/season/firebase/update'
            taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': season.key.id()}, countdown = 2,)

            ## start a task to process bids for each of the factions
            for factionKeyId in refunding_faction_key_id_list:
                taskUrl='/task/faction/process_bids'
                taskqueue.add(url=taskUrl, queue_name='factionProcessBids', params={'key_id': factionKeyId}, countdown = 2,)

            if AUTOMATIC_PHASE_CHANGE:
                ## requeue the task based on settings in config
                logging.info('requeueing task')

                taskUrl='/task/season/stage_change'
                taskqueue.add(url=taskUrl, queue_name='seasonStageChange', countdown = ROUND_DURATION_COMBAT,)





        elif season.currentRoundCombat:
            logging.info('currentRoundCombat')

            ## Time has run out on the round.
            ## All games should be finished by now.
            ## Any unplayed matches result in the zone returning back to uncontrolled.

            ## There could potentially be a lot of matches, so we are going to batch these.
            ## appengine can only support a maximum query size of 1000, so by batching, we can bypass this limitation
            curs = Cursor()
            more  = True

            while more:
                active_matches, curs, more = matchController.list_active_page(start_cursor=curs)

                for match in active_matches:
                    logging.info('processing active match')
                    if match.verified:
                        logging.info('found verified match')

                        ## move the winning user/team/faction into the zone
                        zone = zoneController.get_by_key_id(match.zoneKeyId)
                        if zone:
                            zone.controlled = True
                            zone.factionKeyId = match.winningFactionKeyId
                            zone.factionTag = match.winningFactionTitle
                            zone.userCaptainKeyId = match.winningUserKeyId
                            zone.userCaptainTitle = match.winningUserTitle
                            zone.teamTitle = match.winningTeamTitle
                            zone.uetopiaGamePlayerKeyId = match.winningUetopiaGamePlayerKeyId
                            # save
                            zoneController.update(zone)

                        else:
                            logging.info('zone was not found!')



                    else:
                        logging.info('found expired match')

                        zone = zoneController.get_by_key_id(match.zoneKeyId)
                        if zone:
                            zone.controlled = False
                            zone.factionKeyId = None
                            zone.factionTag = None
                            zone.userCaptainKeyId = None
                            zone.userCaptainTitle = None
                            zone.teamTitle = None
                            zone.uetopiaGamePlayerKeyId = None
                            # save
                            zoneController.update(zone)

                        else:
                            logging.info('zone was not found!')



                    ## mark the match inactive/processed if you want to keep the data around for mining
                    ## in this example we are just going to delete it.
                    matchController.delete(match)


            ## then switch modes to results.
            logging.info('match processing complete.')

            ## update season
            season.currentRoundCombat = False
            season.currentRoundPositioning = False
            season.currentRoundResults = True

            # save
            seasonController.update(season)

            ## push out to firebase
            taskUrl='/task/season/firebase/update'
            taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': season.key.id()}, countdown = 2,)

            if AUTOMATIC_PHASE_CHANGE:
                ## requeue the task based on settings in config
                logging.info('requeueing task')

                taskUrl='/task/season/stage_change'
                taskqueue.add(url=taskUrl, queue_name='seasonStageChange', countdown = ROUND_DURATION_RESULTS,)


        else:
            logging.info('currentRoundResults')

            ## add up rewards for winning each zone, and add them into the facton record.
            ## TODO - allow building here, or some other action to utelize the materials.  build defenses or whatever.

            ##  - Go through each faction
            ##  - - Get all of the zones the faction controls
            ##  - - - sum up the changes
            ##  - Update the faction

            curs = Cursor()
            more  = True

            while more:
                active_factions, curs, more = factionsController.list_active_season_page(season.key.id(), start_cursor=curs)
                for faction in active_factions:
                    logging.info('processing faction')

                    ## get zones under this faction's control
                    controlled_zones = zoneController.list_by_factionKeyId(faction.key.id())
                    for zone in controlled_zones:
                        logging.info('found controlled zone')

                        ## add values for this zone to the faction
                        faction.energy = faction.energy + zone.energy
                        faction.materials = faction.materials + zone.materials
                        faction.control = faction.control + zone.control

                    ## give every faction the defaults - even if they don't control any zones
                    faction.energy = faction.energy + FACTION_ROUND_ENERGY
                    faction.materials = faction.materials + FACTION_ROUND_MATERIALS
                    faction.control = faction.control + FACTION_ROUND_CONTROL

                    # save
                    factionsController.update(faction)

                    ## update firebase only if season is not over
                    if datetime.datetime.now() < season.ends:
                        taskUrl='/task/faction/firebase/update'
                        taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': faction.key.id()}, countdown = 2,)

            ## check to see if the season is over - if it is, calculate the winners, give rewards, something...
            ## if not, update the round number and switch modes to positioning.

            if datetime.datetime.now() > season.ends:
                logging.info('this season is over.  ')

                ## TODO - mark it final, give rewards etc.

                curs = Cursor()
                more  = True
                winning_faction = None
                winner_found = False

                ## get the winning faction from local db - we need them all anyway to reset, so just get them all sorted by control
                while more:
                    logging.info('More is true')
                    factions, curs, more = factionsController.list_active_season_page_by_control(season.key.id(), start_cursor=curs)

                    for faction in factions:
                        logging.info('found faction')
                        ## the first record is our winner.
                        if not winner_found:
                            logging.info('found winner')
                            winner_found = True
                            winning_faction = faction

                            ## get the faction leaders from local db
                            faction_leaders = usersController.list_factionLeaders(faction.key.id())

                            ## divide up the materials points that the faction has accumulated among the faction leaders.
                            ## any remainder will be given to the first record found.

                            if len(faction_leaders):
                                logging.info('found at least one faction leader')

                                materials_earned_for_each_leader = faction.materials / len(faction_leaders)
                                materials_remainder = faction.materials % len(faction_leaders)
                                logging.info('materials_earned_for_each_leader: %s' %materials_earned_for_each_leader)
                                logging.info('materials_remainder: %s' %materials_remainder)

                                remainder_added = False

                                for faction_lead in faction_leaders:
                                    logging.info('found a faction lead')

                                    ## DO DROPS

                                    uri = "/api/v1/game/player/%s/drops/create" % faction_lead.uetopia_playerKeyId

                                    json_values = ({
                                        u'nonce': time.time(),
                                        u'encryption': "sha512",
                                        u'title': CURRENT_SEASON_WINNER_DROP['title'],
                                        u'description': CURRENT_SEASON_WINNER_DROP['description'],
                                        u'uiIcon': CURRENT_SEASON_WINNER_DROP['uiIcon'],
                                        u'data': CURRENT_SEASON_WINNER_DROP['data']
                                        })

                                    entity_json = json.dumps(json_values)


                                    # Hash the params string to produce the Sign header value
                                    H = hmac.new(UETOPIA_ASSIGNED_GAME_API_SECRET, digestmod=hashlib.sha512)
                                    H.update(entity_json)
                                    sign = H.hexdigest()

                                    headers = {"Content-type": "application/x-www-form-urlencoded",
                                                       "Key":UETOPIA_ASSIGNED_GAME_API_KEY,
                                                       "Sign":sign}

                                    conn = httplib.HTTPSConnection(UETOPIA_API_URL)

                                    conn.request("POST", uri, entity_json, headers)
                                    response = conn.getresponse()

                                    #logging.info(response.read())

                                    ## parse the response
                                    jsonstring = str(response.read())
                                    logging.info(jsonstring)
                                    jsonobject = json.loads(jsonstring)

                                    # do something with the response?
                                    if not jsonobject['request_successful']:
                                        logging.info('the request was unsuccessful')

                                    logging.info('request was successful')


                        ## empty out the faction's score to prepare for the next season?
                        ## this could result in zombie factions persisting throughout the seasons.
                        ## just going to delete it instead.
                        ## it will get recreated the next time a player signs in


                        factionsController.delete(faction)


                ## set the season to inactive.
                season.active = False
                seasonController.update(season)

                ## also switch off all achievement season_first_awarded
                achievements = achievementController.list()
                for achievement in achievements:
                    achievements.season_first_awarded = False
                    achievementController.update(achievementController)


                ## also dump firebase values for factions and active_season

                credentials = GoogleCredentials.get_application_default().create_scoped(_FIREBASE_SCOPES)
                http_auth = credentials.authorize(Http())
                empty_json = json.dumps({}) # just empty
                headers = {"Content-Type": "application/json"}

                URL = "%s/factions.json" % (FIREBASE_DATABASE_ROOT)
                resp, content = http_auth.request(URL,
                              "DELETE", ## We can delete data with a DELETE request
                              empty_json,
                              headers=headers)

                URL = "%s/active_season.json" % (FIREBASE_DATABASE_ROOT)
                resp, content = http_auth.request(URL,
                              "DELETE", ## We can delete data with a DELETE request
                              empty_json,
                              headers=headers)

                ## also delete the maps out of the regions
                URL = "%s/regions.json" % (FIREBASE_DATABASE_ROOT)
                resp, content = http_auth.request(URL,
                              "DELETE", ## We can delete data with a DELETE request
                              empty_json,
                              headers=headers)




            else:
                logging.info('season is not over, starting next round')

                ## clear out user moved bools
                ## there could be a lot of these, so we're going to bactch them like before.
                curs = Cursor()
                more  = True

                while more:
                    users_needing_round_reset, curs, more = usersController.list_roundActionUsed_page(start_cursor=curs)

                    for user in users_needing_round_reset:
                        logging.info('processing user')

                        user.roundActionUsed = False
                        usersController.update(user)

                        random_offset = random.randint(2,10) ## if you have a lot of volume you can increase this up to 30 or 60
                        taskUrl='/task/user/firebase/update'
                        taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': user.key.id()}, countdown = random_offset,)

                ## update season
                season.currentRound = season.currentRound +1
                season.currentRoundCombat = False
                season.currentRoundPositioning = True
                season.currentRoundResults = False

                # save
                seasonController.update(season)

                ## push season out to firebase
                taskUrl='/task/season/firebase/update'
                taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': season.key.id()}, countdown = 2,)

                ## push maps out to firebase
                all_maps_for_this_season = mapController.list_by_seasonKeyId(season.key.id())
                for map in all_maps_for_this_season:
                    random_offset = random.randint(2,10)
                    taskUrl='/task/map/firebase/update'
                    taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': map.key.id()}, countdown = random_offset,)


                if AUTOMATIC_PHASE_CHANGE:
                    ## requeue the task based on settings in config
                    logging.info('requeueing task')

                    taskUrl='/task/season/stage_change'
                    taskqueue.add(url=taskUrl, queue_name='seasonStageChange', countdown = ROUND_DURATION_POSITIONING,)
