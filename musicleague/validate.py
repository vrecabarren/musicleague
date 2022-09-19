from musicleague.persistence.select import select_previous_submission


def check_duplicate_albums(my_tracks, their_tracks):
    """ Collect the album ID for each track already submitted. Compare
    the album ID for each track currently being submitted and add any
    track being submitted to duplicate_tracks if album ID has already
    been submitted.
    """
    duplicate_tracks = []
    if not their_tracks:
        return duplicate_tracks

    their_ids = [track['album']['id'] for track in their_tracks if track]

    for my_track in my_tracks:
        if my_track['album']['id'] in their_ids:
            duplicate_tracks.append(my_track['uri'])

    return duplicate_tracks


def check_duplicate_artists(my_tracks, their_tracks):
    """ Collect the primary artist IDs and the set of artist IDs for each
    track already submitted. Compare the primary artist ID and set of artist
    IDs for each track currently being submitted and add any track being
    submitted to duplicate_tracks if primary artist or set of artists has
    already been submitted.
    """
    duplicate_tracks = []
    if not their_tracks:
        return duplicate_tracks

    primary_ids = set([track['artists'][0]['id']
                       for track in filter(None, their_tracks)])

    collab_ids = [set([artist['id'] for artist in track['artists']])
                  for track in filter(None, their_tracks)]

    for my_track in my_tracks:
        my_primary = my_track['artists'][0]['id']
        my_collab = set([artist['id'] for artist in my_track['artists']])
        if my_primary in primary_ids or my_collab in collab_ids:
            duplicate_tracks.append(my_track['uri'])

    return duplicate_tracks


def check_duplicate_tracks(my_tracks, their_tracks):
    """ Collect the track ID and title for each track already submitted.
    Compare the track ID and title for each track currently being
    submitted and add any track being submitted to duplicate_tracks if
    track ID or title has already been submitted.
    """
    duplicate_tracks = []
    if not their_tracks:
        return duplicate_tracks

    their_ids = [track['id'] for track in their_tracks if track]
    their_names = [track['name'] for track in their_tracks if track]

    for my_track in my_tracks:
        if my_track['id'] in their_ids:
            duplicate_tracks.append(my_track['uri'])

        if my_track['name'] in their_names and check_duplicate_artists([my_track], their_tracks):
            duplicate_tracks.append(my_track['uri'])

    return duplicate_tracks


def check_duplicate_season_entry(my_tracks, season_tracks):
    """ Collect the track ID and title for each track already submitted to this league this season. 
    Compare the track ID and title for each track currently being
    submitted and add any track being submitted to duplicate_tracks if
    track ID or title has already been submitted to this league this season.
    """
    duplicate_tracks = []
    if not season_tracks:
        return duplicate_tracks
    
    season_track_ids = [track['id'] for track in season_tracks if track]
    
    for my_track in my_tracks:
        if my_track['id'] in season_ids:
            duplicate_tracks.append(my_track['uri'])

    return duplicate_tracks


def check_repeat_submissions(user_id, tracks, exclude_league_id):
    # TODO Batch into one network call for query
    repeat_submissions = {}

    for track in tracks:
        created, league_name = select_previous_submission(user_id, track, exclude_league_id)
        if created and league_name:
            repeat_submissions[track] = (created,league_name)

    return repeat_submissions
