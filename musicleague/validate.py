def check_duplicate_albums(my_tracks, their_tracks):
    """ Collect the album ID for each track already submitted. Compare
    the album ID for each track currently being submitted and add any
    track being submitted to duplicate_tracks if album ID has already
    been submitted.
    """
    duplicate_tracks = []

    their_ids = [track['album']['id'] for track in their_tracks if track]

    for my_track in my_tracks:
        if my_track['album']['id'] in their_ids:
            duplicate_tracks.append(my_track['uri'])

    return duplicate_tracks


def check_duplicate_artists(my_tracks, their_tracks):
    """ Collect the set of artist IDs for each track already submitted.
    Compare the set of artist IDs for each track currently being submitted
    and add any track being submitted to duplicate_tracks if set of artists
    has already been submitted.
    """
    duplicate_tracks = []

    their_ids = [set([artist['id'] for artist in track['artists']])
                 for track in their_tracks if track]

    for my_track in my_tracks:
        my_ids = set([artist['id'] for artist in my_track['artists']])
        if my_ids in their_ids:
            duplicate_tracks.append(my_track['uri'])

    return duplicate_tracks


def check_duplicate_tracks(my_tracks, their_tracks):
    """ Collect the track ID for each track already submitted. Compare
    the track ID for each track currently being submitted and add any
    track being submitted to duplicate_tracks if track ID has already
    been submitted.
    """
    duplicate_tracks = []

    their_ids = [track['id'] for track in their_tracks if track]

    for my_track in my_tracks:
        if my_track['id'] in their_ids:
            duplicate_tracks.append(my_track['uri'])

    return duplicate_tracks
