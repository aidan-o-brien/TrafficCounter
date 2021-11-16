import sqlite3  # accessing database
import hashlib  # for protecting passwords


def access_database_parameterized(dbfile, query, values):
    '''convenience function to send queries to database.'''
    connect = sqlite3.connect(dbfile)
    cursor = connect.cursor()
    cursor.execute(query, values)
    connect.commit()
    connect.close()


def setup_tables(dbfile):
    '''Set up tables.'''

    # establish connection with db...
    connect = sqlite3.connect(dbfile)
    cursor = connect.cursor()
    # Use a script to send queries - clear existing and create fresh tables...
    cursor.executescript('''
    DROP TABLE IF EXISTS users;
    DROP TABLE IF EXISTS sessions;
    DROP TABLE IF EXISTS add_records;

    CREATE TABLE users (
    username    VARCHAR(255) PRIMARY KEY UNIQUE NOT NULL,
    password    VARCHAR(255) NOT NULL
    );

    CREATE TABLE sessions (
    session_id   INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    magic_id     INTEGER NOT NULL UNIQUE,
    user_id      TEXT,
    start_time   DATETIME,
    end_time     DATETIME,
    FOREIGN KEY(user_id) REFERENCES users(username)
    );

    CREATE TABLE add_records (
    add_record_id   INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    location        TEXT NOT NULL,
    type            TEXT NOT NULL,
    occupancy       INTEGER NOT NULL,
    time_of_record  DATETIME,
    magic_id        INTEGER,
    record_removed  INTEGER DEFAULT 0
    )
    ''')

    connect.commit()
    connect.close()


setup_tables('initial_database.db')
setup_tables('task8_9_database.db')

# Pre-populate the users table with test1, password1 etc...
for i in range(1, 11):
    password = 'password{}'.format(i)
    m = hashlib.sha1()
    m.update(password.encode())
    hashed_password = m.hexdigest()
    access_database_parameterized('initial_database.db',
                    "INSERT INTO users (username, password) \
                    VALUES (?, ?)", ('test{}'.format(i), hashed_password))
    access_database_parameterized('task8_9_database.db',
                    "INSERT INTO users (username, password) \
                    VALUES (?, ?)", ('test{}'.format(i), hashed_password))