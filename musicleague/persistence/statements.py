CREATE_TABLE_USERS = ("CREATE TABLE IF NOT EXISTS users ("
                      "id varchar(255) NOT NULL PRIMARY KEY,"
                      "email varchar(255) NOT NULL,"
                      "joined timestamp DEFAULT NOW(),"
                      "name varchar(255) DEFAULT '');")

CREATE_TABLE_LEAGUES = ("CREATE TABLE IF NOT EXISTS leagues ("
                        "id SERIAL PRIMARY KEY,"
                        "created timestamp DEFAULT NOW(),"
                        "name varchar(255) NOT NULL);")

CREATE_TABLE_ROUNDS = ("CREATE TABLE IF NOT EXISTS rounds ("
                       "id SERIAL PRIMARY KEY,"
                       "created TIMESTAMP DEFAULT NOW(),"
                       "description VARCHAR(255) DEFAULT '',"
                       "league_id SERIAL REFERENCES leagues (id),"
                       "name VARCHAR(255) NOT NULL,"
                       "playlist_url VARCHAR(255) DEFAULT '',"
                       "submissions_due TIMESTAMP NOT NULL,"
                       "votes_due TIMESTAMP NOT NULL);")

