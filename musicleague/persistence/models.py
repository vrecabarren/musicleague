class User:
    def __init__(self, id, email, image_url, joined, name, profile_bg):
        self.id = id
        self.email = email
        self.image_url = image_url
        self.joined = joined
        self.name = name
        self.profile_bg = profile_bg


class League:
    def __init__(self, id, created, name, owner_id):
        self.id = id
        self.created = created
        self.name = name
        self.owner = None
        self.owner_id = owner_id
        self.submission_periods = []
        self.users = []


class Round:
    def __init__(self, id, created, name, description, playlist_url, submissions_due, votes_due):
        self.id = id
        self.created = created
        self.name = name
        self.description = description
        self.playlist_url = playlist_url
        self.submissions = []
        self.submissions_due_date = submissions_due
        self.votes = []
        self.votes_due_date = votes_due
        self.league = None


class Submission:
    def __init__(self, user, tracks, created):
        self.user = user
        self.tracks = tracks
        self.created = created


class Vote:
    def __init__(self, user, votes, created):
        self.user = user
        self.votes = votes
        self.created = created
