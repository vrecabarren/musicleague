from unittest import TestCase
from uuid import uuid4

from musicleague.validate import check_duplicate_albums
from musicleague.validate import check_duplicate_artists
from musicleague.validate import check_duplicate_tracks


class CheckDuplicateAlbumsTestCase(TestCase):

    def test_no_duplicate_album(self):
        my_tracks = [track(album_id='3')]
        their_tracks = [track(album_id='1'), track(album_id='2')]
        duplicate_tracks = check_duplicate_albums(my_tracks, their_tracks)
        self.assertEqual([], duplicate_tracks)

    def test_single_duplicate_album(self):
        my_tracks = [track(album_id='2'), track(album_id='3')]
        their_tracks = [track(album_id='1'), track(album_id='2')]
        duplicate_tracks = check_duplicate_albums(my_tracks, their_tracks)
        self.assertEqual([my_tracks[0]['uri']], duplicate_tracks)

    def test_multiple_duplicate_albums(self):
        my_tracks = [track(album_id='2'), track(album_id='1')]
        their_tracks = [track(album_id='1'), track(album_id='2')]
        duplicate_tracks = check_duplicate_albums(my_tracks, their_tracks)
        self.assertEqual([t['uri'] for t in my_tracks], duplicate_tracks)


class CheckDuplicateArtistsTestCase(TestCase):

    def test_no_duplicate_artist(self):
        my_tracks = [track(artist_ids=['3'])]
        their_tracks = [track(artist_ids=['1']), track(artist_ids=['2'])]
        duplicate_tracks = check_duplicate_artists(my_tracks, their_tracks)
        self.assertEqual([], duplicate_tracks)

    def test_single_duplicate_artist(self):
        my_tracks = [track(artist_ids=['2']), track(artist_ids=['3'])]
        their_tracks = [track(artist_ids=['1']), track(artist_ids=['2'])]
        duplicate_tracks = check_duplicate_artists(my_tracks, their_tracks)
        self.assertEqual([my_tracks[0]['uri']], duplicate_tracks)

    def test_multiple_duplicate_artists(self):
        my_tracks = [track(artist_ids=['2']), track(artist_ids=['1'])]
        their_tracks = [track(artist_ids=['1']), track(artist_ids=['2'])]
        duplicate_tracks = check_duplicate_artists(my_tracks, their_tracks)
        self.assertEqual([t['uri'] for t in my_tracks], duplicate_tracks)

    def test_tracks_same_artists_different_order(self):
        my_tracks = [track(artist_ids=['3', '2', '1'])]
        their_tracks = [track(artist_ids=['2', '1', '3'])]
        duplicate_tracks = check_duplicate_artists(my_tracks, their_tracks)
        self.assertEqual([t['uri'] for t in my_tracks], duplicate_tracks)


class CheckDuplicateTracksTestCase(TestCase):

    def test_no_duplicate_tracks(self):
        my_tracks = [track(track_id='3')]
        their_tracks = [track(track_id='1'), track(track_id='2')]
        duplicate_tracks = check_duplicate_tracks(my_tracks, their_tracks)
        self.assertEqual([], duplicate_tracks)

    def test_single_duplicate_track(self):
        my_tracks = [track(track_id='2'), track(track_id='3')]
        their_tracks = [track(track_id='1'), track(track_id='2')]
        duplicate_tracks = check_duplicate_tracks(my_tracks, their_tracks)
        self.assertEqual([my_tracks[0]['uri']], duplicate_tracks)

    def test_multiple_duplicate_tracks(self):
        my_tracks = [track(track_id='2'), track(track_id='1')]
        their_tracks = [track(track_id='1'), track(track_id='2')]
        duplicate_tracks = check_duplicate_tracks(my_tracks, their_tracks)
        self.assertEqual([t['uri'] for t in my_tracks], duplicate_tracks)


def track(track_id=None, album_id=None, artist_ids=None):
    track_id = uuid4().hex if track_id is None else track_id
    album_id = uuid4().hex if album_id is None else album_id
    artist_ids = [] if artist_ids is None else artist_ids

    return {'id': track_id,
            'uri': 'spotify:track:' + track_id,
            'album': {'id': album_id},
            'artists': [{'id': artist_id} for artist_id in artist_ids]}