import csv
from datetime import datetime
from random import randint
import sqlite3


# Helper function to access the database...
def access_database(dbfile, query):
    connect = sqlite3.connect(dbfile)
    cursor = connect.cursor()
    cursor.execute(query)
    connect.commit()
    connect.close()


# Request file name to be read...
fname = input('Please enter csv file name (with .csv extension): ')

# Generate session id...
magic = ''
for i in range(9):
    magic += str(randint(0, 9))

# Open csv file...
with open(fname, newline='') as fh:
    myreader = csv.reader(fh, delimiter=',', quotechar='|')
    # read each line in the csv file...
    for row in myreader:
        print(row)
        # Initialise the parameters for each row...
        raw_datetime = row[0]
        raw_action = row[1]
        raw_location = row[2]
        raw_vehicle = row[3]
        raw_occupancy = row[4]

        # Convert raw_datetime to correct format...
        new_datetime = datetime.strptime(raw_datetime, '%Y%m%d%H%M')

        # Input the data...
        if raw_action == 'add':
            access_database('task8_9_database.db', "INSERT INTO add_records (location, type, occupancy, time_of_record, magic_id) \
            VALUES ('{}', '{}', {}, '{}', {})".format(raw_location, raw_vehicle, raw_occupancy, new_datetime, magic))
        elif raw_action == 'undo':
            # Only allow undo to undo one record, not just all that match input data...
            access_database('task8_9_database.db', "UPDATE add_records SET record_removed = 1 WHERE add_record_id IN \
            (SELECT add_record_id FROM add_records WHERE record_removed = 0 AND location = '{}' AND type = '{}' \
            AND occupancy = '{}' AND magic_id = '{}' ORDER BY add_record_id LIMIT 1)".format(raw_location,
                                                                                               raw_vehicle,
                                                                                               raw_occupancy, magic))

# task8_test.csv
# adding records
