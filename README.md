# Music League
[![Build Status](https://travis-ci.org/nathancoleman/musicleague.svg?branch=master)](https://travis-ci.org/nathancoleman/musicleague)
[![Coverage Status](https://coveralls.io/repos/github/nathancoleman/musicleague/badge.svg?branch=master)](https://coveralls.io/github/nathancoleman/musicleague?branch=master)

Have you ever wanted to battle it out with your friends and see who has the
best taste in music?

Music League let's you do just that! Create a league, invite your friends,
and have everyone submit their favorite songs to be
voted on by the entire group! Music League integrates with the Spotify API and will
handle the playlists, email reminders, and voting - all you have to do is
submit, listen, and vote!

## Using this Repo
Music League relies on multiple other open source projects:
- [Flask](http://flask.pocoo.org/)
- [HaikunatorPY](https://github.com/Atrox/haikunatorpy)
- [Mongo](https://www.mongodb.org/) (via [MongoEngine](http://mongoengine.org/))
- [Spotipy](http://spotipy.readthedocs.io/en/latest/)

I recommend using [virtualenv](http://www.virtualenv.org/en/latest/) along with
[virtualenvwrapper](http://virtualenvwrapper.readthedocs.org/en/latest/) for
the smoothest experience.

### Prerequisites
There are two prerequisites to install before running:
- [MongoDB](https://docs.mongodb.com/manual/installation/)
- [Redis](https://redis.io/topics/quickstart)

### Make Utils

You may do any of the below after installing prerequisites, cloning this repo, and running ```make install```.

#### Linting
```
make lint
```

#### Running Unit Tests
_Requires listed prerequisites to be up and running._
```
make unit
```

#### Running Locally
_Requires listed prerequisites to be up and running._
```
make run
```

#### Running Continuous Integration Script
_Requires listed prerequisites to be up and running._
```
make ci
```
