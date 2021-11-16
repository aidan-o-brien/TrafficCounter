# Import relevant tools...
import csv
import sqlite3
from datetime import datetime

# Have a helper function to access database...
def access_database_with_result(dbfile, query):
    connect = sqlite3.connect(dbfile)
    cursor = connect.cursor()
    rows = cursor.execute(query).fetchall()
    connect.commit()
    connect.close()
    return rows

# Definition of vehicles (allowed to be hard coded)...
vehicles = ['car', 'taxi', 'bus', 'motorbike', 'bicycle', 'van', 'truck', 'other']

# Ask which database they would like to query...
dbfile = input('Please input the database filename you would like to query: ')

# Find all unique locations...
locations = [location[0] for location in access_database_with_result(dbfile, "SELECT location FROM add_records GROUP BY location")]

# Ask for valid date ranges...
start_datetime = None
end_datetime = None
# Continue asking for dates until valid ones are given...
while start_datetime is None:
    try:
        start_dt_str = input('Please provide a start date and time in the format: YYYY-MM-DD HH:MM:SS ')
        start_datetime = datetime.strptime(start_dt_str, '%Y-%m-%d %H:%M:%S')
    except:
        print('Invalid datetime format. Please try again.')

while end_datetime is None:
    try:
        end_dt_str = input('Please provide a end date and time in the format: YYYY-MM-DD HH:MM:SS ')
        end_datetime = datetime.strptime(end_dt_str, '%Y-%m-%d %H:%M:%S')
    except:
        print('Invalid datetime format. Please try again.')


# Create csv...
with open('task8_out.csv', 'w', newline='') as fh:
    mywriter = csv.writer(fh, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    # Loop through locations...
    for location in locations:
        # For each location, loop through the different vehicle types...
        for vehicle in vehicles:
            csv_list = []
            csv_list.append(location)
            csv_list.append(vehicle)
            # Find the count of 1,2,3,4 for each vehicle-location pair...
            for count in range(1,5):
                temp_result = access_database_with_result(dbfile, "SELECT occupancy, count(occupancy) FROM add_records \
                WHERE time_of_record >= '{}' AND time_of_record <= '{}' AND type = '{}' AND record_removed = 0 AND location = '{}' AND occupancy = {} \
                GROUP BY occupancy".format(start_datetime, end_datetime, vehicle, location, count))
                if len(temp_result) == 0:
                    csv_list.append(0)
                else:
                    csv_list.append(temp_result[0][1])
            print(location, vehicle, csv_list)
            mywriter.writerow(csv_list)
