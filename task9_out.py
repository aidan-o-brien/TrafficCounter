import sqlite3
from datetime import datetime
from datetime import timedelta
from pandas.tseries.offsets import DateOffset  # handle sticky month situations
import csv
import math


# Have a helper function to access database...
def access_database_with_result(dbfile, query):
    connect = sqlite3.connect(dbfile)
    cursor = connect.cursor()
    rows = cursor.execute(query).fetchall()
    connect.commit()
    connect.close()
    return rows


# Have a helper function for summing lists and round up...
def get_sum(hours_list):
    sum = 0
    for i in range(len(hours_list)):
        if hours_list[i] != None:  # if they are still logged in, they will do not get paid (sorry guys)
            sum += hours_list[i]
    # Round up...
    sum = math.ceil(sum * 10) / 10
    return sum


# Request a database to be queried...
dbfile = input('Please enter the database file you would like to query: ')

# Request a date to query with...
requested_date = None
while requested_date is None:
    try:
        string_date = input('Please enter a date you would like to enquire about (format required: YYYYMMDD): ')
        requested_date = datetime.strptime(string_date, '%Y%m%d')
    except:
        print('Invalid date format. Please try again.')

# Initialise datetimes - start and end that date, start and end preceding week, start and end preceding month...
## Start and end of given date...
day_end = requested_date + timedelta(1)  # <
day_start = requested_date  # <=
print(day_start, day_end)
## Start and end of week...
week_end = requested_date + timedelta(1)  # <
week_start = requested_date - timedelta(6)  # <=
print(week_start, week_end)
## Start and end of month...
month_end = requested_date + timedelta(1)  # <
month_start = requested_date - DateOffset(months=1) + timedelta(1)  # <=
print(month_start, month_end)

# Find all unique users...
users = [user[0] for user in access_database_with_result(dbfile, "SELECT username FROM users")]

# Create a csv file...
with open('task9_out.csv', 'w', newline='') as fh:
    mywriter = csv.writer(fh, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    # Loop through user...
    for user in users:
        csv_list = []
        csv_list.append(user)

        # Find daily total hours...
        day_hours = access_database_with_result(dbfile, "SELECT \
        CASE \
        WHEN end_time > '{}' \
        THEN 24*(julianday('{}') - julianday(start_time)) \
        ELSE 24*(julianday(end_time) - julianday(start_time)) \
        END \
        FROM sessions \
        WHERE user_id = '{}' AND start_time > '{}' AND start_time < '{}'".format(day_end, day_end, user, day_start,
                                                                                 day_end))
        ## Format day hours...
        day_hours = [item[0] for item in day_hours]

        # Find weekly total hours...
        week_hours = access_database_with_result(dbfile, "SELECT \
        CASE \
        WHEN end_time > '{}' \
        THEN 24*(julianday('{}') - julianday(start_time)) \
        ELSE 24*(julianday(end_time) - julianday(start_time)) \
        END \
        FROM sessions \
        WHERE user_id = '{}' AND start_time > '{}' AND start_time < '{}'".format(week_end, week_end, user, week_start,
                                                                                 week_end))
        ## Format week hours...
        week_hours = [item[0] for item in week_hours]

        # Find monthly total hours...
        month_hours = access_database_with_result(dbfile, "SELECT \
        CASE \
        WHEN end_time > '{}' \
        THEN 24*(julianday('{}') - julianday(start_time)) \
        ELSE 24*(julianday(end_time) - julianday(start_time)) \
        END \
        FROM sessions \
        WHERE user_id = '{}' AND start_time > '{}' AND start_time < '{}'".format(month_end, month_end, user,
                                                                                 month_start, month_end))
        ## Format month hours...
        month_hours = [item[0] for item in month_hours]

        ## Add up, round up, and add to csv list...
        csv_list.append(get_sum(day_hours))
        csv_list.append(get_sum(week_hours))
        csv_list.append(get_sum(month_hours))

        # Add csv list to csv file...
        mywriter.writerow(csv_list)
