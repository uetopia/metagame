from webapp2 import Route

routes = [
    Route('/api/v1/metagame/player_start', 'apps.metagame.api.v1.player_start_meta_mode.playerStartMetaGameHandler', name="player-start-meta-game"),
    Route('/api/v1/metagame/player_end', 'apps.metagame.api.v1.player_end_meta_mode.playerEndMetaGameHandler', name="player-end-meta-game"),
    Route('/api/v1/metagame/match_results', 'apps.metagame.api.v1.match_results_meta_mode.matchResultsMetaGameHandler', name="match-results-meta-game"),
    ]
