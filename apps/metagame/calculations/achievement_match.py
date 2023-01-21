def calc_damage_done(matchCharacter, achievement_progress, damage_required):
    if matchCharacter:
        # no progress with this.  It is per match
        #achievement_progress.progressInt = achievement_progress.progressInt + matchCharacter.damage_dealt
        if matchCharacter.damage_dealt  >= damage_required:
            achievement_progress.earned = True
    return achievement_progress


## TODO: Insert all of your custom variable calculations.
