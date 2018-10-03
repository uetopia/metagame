import datetime

WEB_CLIENT_ID = ''
WEB_CLIENT_AUTOCREATED_BY_GOOGLE = ''
GOOGLE_SERVER_API_KEY = ''

ADMIN_DISCORD_WEBHOOK = ""

UETOPIA_API_URL = "yourproject.appspot.com"
UETOPIA_ASSIGNED_GAME_ID = ""
UETOPIA_ASSIGNED_GAME_API_KEY = ""
UETOPIA_ASSIGNED_GAME_API_SECRET = ""
UETOPIA_ASSIGNED_GAME_MODE_ID = ""

FIREBASE_DATABASE_ROOT = "https://yourproject.firebaseio.com"

## Zone types determine how maps are built.  These reference the actual game level to load when a match takes place in this zone.
## minimum and maximum values are rolled when the actual zone is created based on these values.
ZONE_TYPES = [
    {'title': 'Default Zone',
    'engine_travel_url': 'game/Maps/ThirdPersonExample?listen',
    'probability': 70,
    'energyMin': 0,
    'energyMax': 50,
    'materialsMin': 0,
    'materialsMax': 50,
    'controlMin': 0,
    'controlMax': 50,
    'validZone': True
    },
    {'title': 'Energy Zone',
    'engine_travel_url': 'game/Maps/ThirdPersonExample?listen',
    'probability': 80,
    'energyMin': 50,
    'energyMax': 100,
    'materialsMin': 0,
    'materialsMax': 50,
    'controlMin': 0,
    'controlMax': 50,
    'validZone': True
    },
    {'title': 'Material Zone',
    'engine_travel_url': 'game/Maps/ThirdPersonExample?listen',
    'probability': 90,
    'energyMin': 0,
    'energyMax': 50,
    'materialsMin': 50,
    'materialsMax': 100,
    'controlMin': 0,
    'controlMax': 50,
    'validZone': True
    },
    {'title': 'Blank Zone',
    'engine_travel_url': '',
    'probability': 100,
    'energyMin': 0,
    'energyMax': 0,
    'materialsMin': 0,
    'materialsMax': 0,
    'controlMin': 0,
    'controlMax': 0,
    'validZone': False
    }
]


## values to assign to new factions when they sign up, or when a new season starts
FACTION_STARTING_ENERGY = 100
FACTION_STARTING_MATERIALS = 0
FACTION_STARTING_CONTROL = 0

## Default values to assign to active factions at the start of each round
FACTION_ROUND_ENERGY = 1
FACTION_ROUND_MATERIALS = 0
FACTION_ROUND_CONTROL = 0

## Minimum and maximum bid amounts
MINIMUM_BID = 1
MAXIMUM_BID = 100000

## Duration in seconds for each round
ROUND_DURATION_POSITIONING = 300
ROUND_DURATION_COMBAT = 600
ROUND_DURATION_RESULTS = 150

## Disabling automatic phase changing is helpful for testing and debugging.
## Hit this url when you want to advance the phase manually:  https://[projectname].appspot.com/task/season/stage_change
AUTOMATIC_PHASE_CHANGE = False
