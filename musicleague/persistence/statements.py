# ================
# USER PREFERENCES
# ================

CREATE_TABLE_USER_PREFERENCES = """CREATE TABLE IF NOT EXISTS user_preferences (
                                        user_id VARCHAR(255) NOT NULL PRIMARY KEY REFERENCES users(id),
                                        owner_all_users_submitted_notifications BOOL NOT NULL DEFAULT TRUE,
                                        owner_all_users_voted_notifications BOOL NOT NULL DEFAULT TRUE,
                                        owner_user_left_notifications BOOL NOT NULL DEFAULT TRUE,
                                        owner_user_submitted_notifications BOOL NOT NULL DEFAULT TRUE,
                                        owner_user_voted_notifications BOOL NOT NULL DEFAULT TRUE,
                                        user_added_to_league_notifications BOOL NOT NULL DEFAULT TRUE,
                                        user_playlist_created_notifications BOOL NOT NULL DEFAULT TRUE,
                                        user_removed_from_league_notifications BOOL NOT NULL DEFAULT TRUE,
                                        user_submit_reminder_notifications BOOL NOT NULL DEFAULT TRUE,
                                        user_vote_reminder_notifications BOOL NOT NULL DEFAULT TRUE);"""

SELECT_USER_PREFERENCES = """SELECT owner_all_users_submitted_notifications,
                                    owner_all_users_voted_notifications,
                                    owner_user_left_notifications,
                                    owner_user_submitted_notifications,
                                    owner_user_voted_notifications,
                                    user_added_to_league_notifications,
                                    user_playlist_created_notifications,
                                    user_removed_from_league_notifications,
                                    user_submit_reminder_notifications,
                                    user_vote_reminder_notifications
                            FROM user_preferences
                            WHERE user_id = %s;"""

UPSERT_USER_PREFERENCES = """INSERT INTO user_preferences (user_id,
                                                           owner_all_users_submitted_notifications,
                                                           owner_all_users_voted_notifications,
                                                           owner_user_left_notifications,
                                                           owner_user_submitted_notifications,
                                                           owner_user_voted_notifications,
                                                           user_added_to_league_notifications,
                                                           user_playlist_created_notifications,
                                                           user_removed_from_league_notifications,
                                                           user_submit_reminder_notifications,
                                                           user_vote_reminder_notifications)
                             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                             ON CONFLICT (user_id)
                             DO
                                UPDATE
                                    SET (owner_all_users_submitted_notifications,
                                         owner_all_users_voted_notifications,
                                         owner_user_left_notifications,
                                         owner_user_submitted_notifications,
                                         owner_user_voted_notifications,
                                         user_added_to_league_notifications,
                                         user_playlist_created_notifications,
                                         user_removed_from_league_notifications,
                                         user_submit_reminder_notifications,
                                         user_vote_reminder_notifications)
                                    =   (EXCLUDED.owner_all_users_submitted_notifications,
                                         EXCLUDED.owner_all_users_voted_notifications,
                                         EXCLUDED.owner_user_left_notifications,
                                         EXCLUDED.owner_user_submitted_notifications,
                                         EXCLUDED.owner_user_voted_notifications,
                                         EXCLUDED.user_added_to_league_notifications,
                                         EXCLUDED.user_playlist_created_notifications,
                                         EXCLUDED.user_removed_from_league_notifications,
                                         EXCLUDED.user_submit_reminder_notifications,
                                         EXCLUDED.user_vote_reminder_notifications)
                                    WHERE user_preferences.user_id = EXCLUDED.user_id;"""

# =====
# USERS
# =====

CREATE_TABLE_USERS = """CREATE TABLE IF NOT EXISTS users (
                            id VARCHAR(255) NOT NULL PRIMARY KEY,
                            email VARCHAR(255) NOT NULL,
                            image_url VARCHAR(255) NOT NULL,
                            joined TIMESTAMP NOT NULL DEFAULT NOW(),
                            name VARCHAR(255) DEFAULT '',
                            profile_bg VARCHAR(255) NOT NULL,
                            is_admin BOOL NOT NULL DEFAULT FALSE);"""

DELETE_USER = "DELETE FROM users WHERE id = %s;"

INSERT_USER = """INSERT INTO users (id, email, image_url, joined, name, profile_bg)
                    VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (id) DO NOTHING;"""

SELECT_USER = "SELECT email, image_url, is_admin, joined, name, profile_bg FROM users WHERE id = %s;"

SELECT_USER_BY_EMAIL = "SELECT id, image_url, is_admin, joined, name, profile_bg FROM users WHERE email = %s;"

SELECT_USERS_COUNT = "SELECT COUNT(id) FROM users;"

SELECT_USERS_IN_LEAGUE = "SELECT user_id FROM memberships WHERE league_id = %s ORDER BY created;"

UPDATE_USER = "UPDATE users SET (email, image_url, name, profile_bg, is_admin) = (%s, %s, %s, %s, %s) WHERE id = %s;"

UPSERT_USER = """INSERT INTO users (id, email, image_url, joined, name, profile_bg, is_admin)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE
                    SET (email, image_url, joined, name, profile_bg, is_admin)
                    = (EXCLUDED.email, EXCLUDED.image_url, EXCLUDED.joined, EXCLUDED.name, EXCLUDED.profile_bg, EXCLUDED.is_admin)
                    WHERE users.id = EXCLUDED.id;"""

# =============
# INVITED USERS
# =============

CREATE_TABLE_INVITED_USERS = """CREATE TABLE IF NOT EXISTS invited_users (
                                    id VARCHAR(255) NOT NULL PRIMARY KEY,
                                    invited TIMESTAMP NOT NULL DEFAULT NOW(),
                                    email VARCHAR(255) NOT NULL,
                                    league_id VARCHAR(255) NOT NULL REFERENCES leagues(id),
                                    UNIQUE (email, league_id));"""

DELETE_INVITED_USER = "DELETE FROM invited_users WHERE id = %s;"

INSERT_INVITED_USER = "INSERT INTO invited_users (id, email, league_id) VALUES (%s, %s, %s) ON CONFLICT (email, league_id) DO NOTHING;"

SELECT_INVITED_USERS_COUNT = "SELECT COUNT(id) FROM invited_users;"

SELECT_INVITED_USERS_IN_LEAGUE = "SELECT id, email FROM invited_users WHERE league_id = %s ORDER BY invited;"

# ====
# BOTS
# ====

CREATE_TABLE_BOTS = """CREATE TABLE IF NOT EXISTS bots (
                            id VARCHAR(255) NOT NULL PRIMARY KEY,
                            access_token VARCHAR(255) NOT NULL,
                            refresh_token VARCHAR(255) NOT NULL,
                            expires_at INT NOT NULL);"""

SELECT_BOT = "SELECT access_token, refresh_token, expires_at FROM bots WHERE id = %s;"

UPSERT_BOT = """INSERT INTO bots (id, access_token, refresh_token, expires_at)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE
                    SET (access_token, refresh_token, expires_at)
                    = (EXCLUDED.access_token, EXCLUDED.refresh_token, EXCLUDED.expires_at)
                    WHERE bots.id = EXCLUDED.id;"""

# =======
# LEAGUES
# =======

CREATE_TABLE_LEAGUES = """CREATE TABLE IF NOT EXISTS leagues (
                            id VARCHAR(255) PRIMARY KEY,
                            created TIMESTAMP NOT NULL DEFAULT NOW(),
                            name VARCHAR(255) NOT NULL,
                            owner_id VARCHAR(255) NOT NULL REFERENCES users(id),
                            status SMALLINT NOT NULL DEFAULT 0);"""

DELETE_LEAGUE = "DELETE FROM leagues WHERE id = %s;"

INSERT_LEAGUE = "INSERT INTO leagues (id, created, name, owner_id, status) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (id) DO NOTHING;"

SELECT_LEAGUE = "SELECT created, name, owner_id, status FROM leagues WHERE id = %s;"

SELECT_LEAGUES_COUNT = "SELECT COUNT(id) FROM leagues;"

UPDATE_LEAGUE = "UPDATE leagues SET (name, status) = (%s, %s) WHERE id = %s;"

UPDATE_LEAGUE_STATUS = "UPDATE leagues SET status = %s WHERE id = %s;"

# ===========
# MEMBERSHIPS
# ===========

CREATE_TABLE_MEMBERSHIPS = """CREATE TABLE IF NOT EXISTS memberships (
                                created TIMESTAMP NOT NULL DEFAULT NOW(),
                                league_id VARCHAR(255) NOT NULL REFERENCES leagues(id),
                                rank SMALLINT NOT NULL DEFAULT -1,
                                user_id VARCHAR(255) NOT NULL REFERENCES users(id),
                                UNIQUE (league_id, user_id));"""

DELETE_MEMBERSHIP = "DELETE FROM memberships WHERE league_id = %s AND user_id = %s;"

DELETE_MEMBERSHIPS = "DELETE FROM memberships WHERE league_id = %s;"

INSERT_MEMBERSHIP = """INSERT INTO memberships (league_id, user_id)
                            VALUES (%s, %s) ON CONFLICT (league_id, user_id) DO NOTHING;"""

SELECT_MEMBERSHIPS_COUNT = "SELECT COUNT(league_id) from memberships WHERE user_id = %s;"

SELECT_MEMBERSHIPS_FOR_USER = """SELECT memberships.league_id
                                    FROM memberships
                                    INNER JOIN leagues ON leagues.id = memberships.league_id
                                    WHERE memberships.user_id = %s
                                    ORDER BY leagues.created DESC;"""

SELECT_MEMBERSHIPS_PLACED_FOR_USER = """SELECT rank, count(league_id)
                                            FROM memberships
                                            WHERE user_id = %s
                                            AND rank IN (1,2,3)
                                            GROUP BY rank
                                            ORDER BY rank;"""

UPDATE_MEMBERSHIP_RANK = "UPDATE memberships SET rank = %s WHERE league_id = %s AND user_id = %s;"

SELECT_SCOREBOARD = """SELECT users.id, memberships.rank
                        FROM memberships
                        INNER JOIN users ON users.id = memberships.user_id
                        WHERE memberships.league_id = %s
                        ORDER BY memberships.rank;"""

# ======
# ROUNDS
# ======

CREATE_TABLE_ROUNDS = """CREATE TABLE IF NOT EXISTS rounds (
                            id VARCHAR(255) PRIMARY KEY,
                            created TIMESTAMP NOT NULL DEFAULT NOW(),
                            description VARCHAR(255) DEFAULT '',
                            league_id VARCHAR(255) NOT NULL REFERENCES leagues(id),
                            name VARCHAR(255) NOT NULL,
                            playlist_url VARCHAR(255) DEFAULT '',
                            status SMALLINT NOT NULL DEFAULT 0,
                            submissions_due TIMESTAMP NOT NULL,
                            votes_due TIMESTAMP NOT NULL);"""

DELETE_ROUND = "DELETE FROM rounds WHERE id = %s;"

DELETE_ROUNDS = "DELETE FROM rounds WHERE league_id = %s;"

INSERT_ROUND = """INSERT INTO rounds (id, created, description, league_id, name, status, submissions_due, votes_due)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (id) DO NOTHING;"""

SELECT_ROUND = """SELECT league_id, created, description, name, playlist_url, submissions_due, votes_due
                    FROM rounds WHERE id = %s;"""

SELECT_ROUNDS_COUNT = "SELECT COUNT(id) FROM rounds;"

SELECT_ROUNDS_IN_LEAGUE = "SELECT id FROM rounds WHERE league_id = %s ORDER BY submissions_due, votes_due;"

SELECT_ROUNDS_IN_LEAGUE_WITH_STATUS = """SELECT id FROM rounds
                                            WHERE league_id = %s AND status = %s
                                            ORDER BY submissions_due, votes_due;"""

UPDATE_ROUND = """UPDATE rounds SET (description, name, status, submissions_due, votes_due)
                    = (%s, %s, %s, %s, %s) WHERE id = %s;"""

UPDATE_ROUND_STATUS = "UPDATE rounds SET status = %s WHERE id = %s;"

UPSERT_ROUND = """INSERT INTO rounds (id, created, description, league_id, name, playlist_url, status, submissions_due, votes_due)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE
                    SET (created, description, league_id, name, playlist_url, status, submissions_due, votes_due)
                    = (EXCLUDED.created, EXCLUDED.description, EXCLUDED.league_id, EXCLUDED.name, EXCLUDED.playlist_url,
                       EXCLUDED.status, EXCLUDED.submissions_due, EXCLUDED.votes_due)
                    WHERE rounds.id = EXCLUDED.id"""

# ===========
# SUBMISSIONS
# ===========

CREATE_TABLE_SUBMISSIONS = """CREATE TABLE IF NOT EXISTS submissions (
                                    created TIMESTAMP NOT NULL DEFAULT NOW(),
                                    rank SMALLINT NOT NULL DEFAULT -1,
                                    round_id VARCHAR(255) NOT NULL REFERENCES rounds(id),
                                    spotify_uri VARCHAR(255) NOT NULL,
                                    submitter_id VARCHAR(255) NOT NULL REFERENCES users(id),
                                    UNIQUE (round_id, spotify_uri));"""

INSERT_SUBMISSION = """INSERT INTO submissions (created, round_id, spotify_uri, submitter_id)
                            VALUES (%s, %s, %s, %s)
                            ON CONFLICT (round_id, spotify_uri) DO UPDATE
                            SET created = EXCLUDED.created
                            WHERE submissions.round_id = EXCLUDED.round_id
                            AND submissions.spotify_uri = EXCLUDED.spotify_uri;"""

DELETE_SUBMISSIONS = "DELETE FROM submissions WHERE submitter_id = %s AND round_id = %s;"

SELECT_SUBMISSIONS = """SELECT created, league_id, round_id, submitter_id, tracks
                            FROM (
                                SELECT created, league_id, round_id, submitter_id, tracks,
                                RANK() OVER (PARTITION BY round_id, submitter_id ORDER BY created) AS rn
                                FROM (
                                    SELECT created, round_id, submitter_id, ARRAY_AGG(spotify_uri) as tracks
                                    FROM submissions
                                    GROUP BY round_id, submitter_id, created
                                    ORDER BY created DESC
                                ) AS s
                            ) AS s
                            WHERE league_id = %s AND rn = 1;"""

SELECT_SUBMISSIONS_COUNT = "SELECT COUNT(submitter_id) FROM submissions;"

SELECT_SUBMISSIONS_FROM_USER = """SELECT created, json_object_agg(spotify_uri, rank)
                                    FROM submissions WHERE round_id = %s AND submitter_id = %s
                                    GROUP BY created
                                    ORDER BY created DESC
                                    LIMIT 1;"""

UPDATE_SUBMISSION_RANK = "UPDATE submissions SET rank = %s WHERE round_id = %s AND spotify_uri = %s;"

# =====
# VOTES
# =====

CREATE_TABLE_VOTES = """CREATE TABLE IF NOT EXISTS votes (
                            created TIMESTAMP DEFAULT NOW(),
                            round_id VARCHAR(255) NOT NULL,
                            spotify_uri VARCHAR(255) NOT NULL,
                            voter_id VARCHAR(255) NOT NULL REFERENCES users(id),
                            weight SMALLINT NOT NULL,
                            FOREIGN KEY (round_id, spotify_uri) REFERENCES submissions(round_id, spotify_uri),
                            UNIQUE (created, round_id, spotify_uri, voter_id, weight));"""

INSERT_VOTE = """INSERT INTO votes (created, round_id, spotify_uri, voter_id, weight)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (created, round_id, spotify_uri, voter_id, weight) DO UPDATE
                    SET (created, weight)
                    = (EXCLUDED.created, EXCLUDED.weight)
                    WHERE votes.round_id = EXCLUDED.round_id
                    AND votes.spotify_uri = EXCLUDED.spotify_uri
                    AND votes.voter_id = EXCLUDED.voter_id;"""

DELETE_VOTES = "DELETE FROM votes WHERE voter_id = %s AND round_id = %s;"

SELECT_VOTES = """SELECT votes.spotify_uri,
                         votes.weight,
                         vu.id
                  FROM votes
                  LEFT JOIN users vu ON vu.id = votes.voter_id
                  WHERE votes.round_id = %s
                  ORDER BY votes.created;"""

SELECT_VOTES_FROM_USER = """SELECT created, json_object_agg(spotify_uri, weight)
                                FROM votes WHERE round_id = %s AND voter_id = %s
                                GROUP BY created
                                ORDER BY created DESC
                                LIMIT 1;"""

SELECT_SUBMISSIONS_WITH_VOTES = """SELECT submissions.spotify_uri,
                                          su.id,
                                          su.name,
                                          vu.id,
                                          vu.name,
                                          votes.weight
                                   FROM submissions
                                   RIGHT JOIN votes ON votes.spotify_uri = submissions.spotify_uri
                                   LEFT JOIN users su ON su.id = submissions.submitter_id
                                   LEFT JOIN users vu ON vu.id = votes.voter_id
                                   WHERE submissions.round_id = %s
                                   ORDER BY points DESC;"""

SELECT_VOTES_COUNT = "SELECT COUNT(voter_id) FROM votes;"
