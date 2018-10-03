from webapp2 import Route

routes = [
    Route('/task/user/firebase/update','apps.metagame.handlers.tasks.user_firebase_update.UserUpdateFirebaseHandler', name='task-user-firebase-update'),
    Route('/task/season/firebase/update','apps.metagame.handlers.tasks.season_firebase_update.SeasonUpdateFirebaseHandler', name='task-season-firebase-update'),
    Route('/task/map/firebase/update','apps.metagame.handlers.tasks.map_firebase_update.MapUpdateFirebaseHandler', name='task-map-firebase-update'),
    Route('/task/faction/firebase/update','apps.metagame.handlers.tasks.faction_firebase_update.FactionUpdateFirebaseHandler', name='task-faction-firebase-update'),

    Route('/task/season/stage_change','apps.metagame.handlers.tasks.season_stage_change.SeasonStageChangeHandler', name='task-season-state-change'),

    Route('/task/faction/process_bids','apps.metagame.handlers.tasks.faction_process_bids.FactionProcessBidsHandler', name='task-faction-process-bids'),

    ]
