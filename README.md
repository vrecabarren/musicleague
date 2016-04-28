# Feedback
[![Build Status](https://travis-ci.org/nathancoleman/feedback.svg?branch=master)](https://travis-ci.org/nathancoleman/feedback)

Have you ever wanted to battle it out with your friends and see who has the
best taste in music?

Feedback let's you do just that! Create a session, invite your friends using
just their email addresses, and have everyone submit their favorite songs to be
voted on by the entire group! Feedback integrates with the Spotify API and will
handle the playlists, email reminders, and voting - all you have to do is
submit and listen!

## Using this Repo
Feedback is a [Python](https://www.python.org/) project that relies on
[Flask](http://flask.pocoo.org/), [Mongo](https://www.mongodb.org/) (via [MongoEngine](http://mongoengine.org/)),
and [Heroku](https://www.heroku.com/).

I recommend using [virtualenv](http://www.virtualenv.org/en/latest/) along with
[virtualenvwrapper](http://virtualenvwrapper.readthedocs.org/en/latest/) for
the smoothest experience.

You may do any of the below after cloning this repo and running ```make install```.

### Linting
```
make lint
```

### Running Unit Tests
```
make unit
```

### Running Locally
```
make run
```
