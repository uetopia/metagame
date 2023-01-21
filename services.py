import fix_path
import endpoints

from service import seed
from service import users
from service import regions
from service import seasons
from service import maps
from service import zones
from service import characters
from service import achievements
from service import matches

app = endpoints.api_server([users.UsersApi, seed.Api, regions.RegionsApi, seasons.SeasonsApi, maps.MapsApi, zones.ZonesApi, characters.CharactersApi, achievements.AchievementsApi, matches.MatchesApi], restricted=False)
