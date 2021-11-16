import csv
import sqlite3
from random import randint
from datetime import datetime
import pandas as pd


# Helper function to access the database...
def access_database(dbfile, query):
    connect = sqlite3.connect(dbfile)
    cursor = connect.cursor()
    cursor.execute(query)
    connect.commit()
    connect.close()


# Request file name to be read...
fname = input('Please enter csv file name (with .csv extension): ')

# Put file in chronological order...
df = pd.read_csv(fname, header=None, parse_dates=[1])
df.sort_values([1], inplace=True)
df.to_csv(fname, index=False, header=None)

# Read the csv...
with open(fname, newline='') as fh:
    myreader = csv.reader(fh, delimiter=',', quotechar='|')
    for row in myreader:
        # Initialise parameters...
        user = row[0]
        dt = row[1]
        action = row[2]
        dt = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')

        # Create magic id...
        magic = ''
        for i in range(9):
            magic += str(randint(0, 9))

        # Add sessions...
        if action == 'login':  # add session start record
            access_database('task8_9_database.db',
                            "INSERT INTO sessions (magic_id, user_id, start_time) VALUES ({}, '{}', '{}')".format(
                                magic, user, dt))
        elif action == 'logout':  # add session end record
            access_database('task8_9_database.db', "UPDATE sessions \
            SET end_time = '{}' \
            WHERE session_id IN \
            (SELECT session_id FROM sessions \
            WHERE user_id = '{}' AND end_time IS NULL \
            ORDER BY start_time LIMIT 1)".format(dt, user))

# test1, 201906011243, login
# test_task9_in.csv
# adding sessions
