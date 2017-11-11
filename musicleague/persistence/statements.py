# =====
# USERS
# =====

CREATE_TABLE_USERS = """CREATE TABLE IF NOT EXISTS users (
                            id VARCHAR(255) NOT NULL PRIMARY KEY,
                            email VARCHAR(255) NOT NULL,
                            joined TIMESTAMP DEFAULT NOW(),
                            name VARCHAR(255) DEFAULT '');"""

DELETE_USER = "DELETE FROM users WHERE id = %s;"

INSERT_USER = "INSERT INTO users (id, email, name) VALUES (%s, %s, %s) ON CONFLICT (id) DO NOTHING;"

UPDATE_USER = "UPDATE users SET (email, name) = (%s, %s) WHERE id = %s;"

# =======
# LEAGUES
# =======

CREATE_TABLE_LEAGUES = """CREATE TABLE IF NOT EXISTS leagues (
                            id VARCHAR(255) PRIMARY KEY,
                            created TIMESTAMP DEFAULT NOW(),
                            name VARCHAR(255) NOT NULL,
                            owner_id VARCHAR(255) NOT NULL REFERENCES users(id));"""

DELETE_LEAGUE = "DELETE FROM leagues WHERE id = %s;"

INSERT_LEAGUE = "INSERT INTO leagues (id, name, owner_id) VALUES (%s, %s, %s) ON CONFLICT (id) DO NOTHING;"

UPDATE_LEAGUE = "UPDATE leagues SET (name) = (%s) WHERE id = %s;"

# ======
# ROUNDS
# ======

CREATE_TABLE_ROUNDS = """CREATE TABLE IF NOT EXISTS rounds (
                            id VARCHAR(255) PRIMARY KEY,
                            created TIMESTAMP DEFAULT NOW(),
                            description VARCHAR(255) DEFAULT '',
                            league_id VARCHAR(255) NOT NULL REFERENCES leagues(id),
                            name VARCHAR(255) NOT NULL,
                            playlist_url VARCHAR(255) DEFAULT '',
                            submissions_due TIMESTAMP NOT NULL,
                            votes_due TIMESTAMP NOT NULL);"""

DELETE_ROUND = "DELETE FROM users WHERE id = %s;"

INSERT_ROUND = """INSERT INTO rounds (id, description, league_id, name, submissions_due, votes_due)
                    VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (id) DO NOTHING;"""

UPDATE_ROUND = """UPDATE rounds SET (description, name, submissions_due, votes_due)
                    VALUES (%s, %s, %s, %s) WHERE id = %s;"""

# ===========
# SUBMISSIONS
# ===========

CREATE_TABLE_SUBMISSIONS = """CREATE TABLE IF NOT EXISTS submissions (
                                    id SERIAL PRIMARY KEY,
                                    created TIMESTAMP DEFAULT NOW(),
                                    round_id VARCHAR(255) NOT NULL REFERENCES rounds(id),
                                    spotify_uri VARCHAR(255) NOT NULL,
                                    submitter_id VARCHAR(255) NOT NULL REFERENCES users(id));"""

INSERT_SUBMISSION = "INSERT INTO submissions (round_id, spotify_uri, submitter_id) VALUES (%s, %s, %s);"

SELECT_SUBMISSION_ID = "SELECT id FROM submissions WHERE round_id = %s AND spotify_uri = %s;"


# =====
# VOTES
# =====

CREATE_TABLE_VOTES = """CREATE TABLE IF NOT EXISTS votes (
                            created TIMESTAMP DEFAULT NOW(),
                            round_id VARCHAR(255) NOT NULL REFERENCES rounds(id),
                            submission_id SERIAL NOT NULL REFERENCES submissions(id),
                            voter_id VARCHAR(255) NOT NULL REFERENCES users(id),
                            weight SMALLINT NOT NULL);"""

INSERT_VOTE = "INSERT INTO votes (round_id, submission_id, voter_id, weight) VALUES (%s, %s, %s, %s);"
