from webapp2 import Route

routes = [
    Route('/task/user/firebase/update','apps.metagame.handlers.tasks.user_firebase_update.UserUpdateFirebaseHandler', name='task-user-firebase-update'),
    Route('/task/season/firebase/update','apps.metagame.handlers.tasks.season_firebase_update.SeasonUpdateFirebaseHandler', name='task-season-firebase-update'),
    Route('/task/map/firebase/update','apps.metagame.handlers.tasks.map_firebase_update.MapUpdateFirebaseHandler', name='task-map-firebase-update'),
    Route('/task/faction/firebase/update','apps.metagame.handlers.tasks.faction_firebase_update.FactionUpdateFirebaseHandler', name='task-faction-firebase-update'),
    Route('/task/characters/firebase/update','apps.metagame.handlers.tasks.characters_firebase_update.CharactersUpdateFirebaseHandler', name='task-characters-firebase-update'),

    Route('/task/character/statistics/calculate','apps.metagame.handlers.tasks.character_statistics_calculate.CharacterStatisticsCalculateHandler', name='task-character-statistics-calculate'),
    Route('/task/character/achievement/process','apps.metagame.handlers.tasks.achievement_earned_process.AchievementEarnedProcessHandler', name='task-achievement-earned-process'),

    Route('/task/season/stage_change','apps.metagame.handlers.tasks.season_stage_change.SeasonStageChangeHandler', name='task-season-state-change'),

    Route('/task/faction/process_bids','apps.metagame.handlers.tasks.faction_process_bids.FactionProcessBidsHandler', name='task-faction-process-bids'),

    ]
