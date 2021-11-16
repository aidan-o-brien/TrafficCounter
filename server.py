#!/usr/bin/env python

# This is a simple web server for a traffic counting application.
# It's your job to extend it by adding the backend functionality to support
# recording the traffic in a SQL database. You will also need to support
# some predefined users and access/session control. You should only
# need to extend this file. The client side code (html, javascript and css)
# is complete and does not require editing or detailed understanding.

# import the various libraries needed
import http.cookies as Cookie  # some cookie handling support
from http.server import BaseHTTPRequestHandler, HTTPServer  # the heavy lifting of the web server
import urllib  # some url parsing support
import base64  # some encoding support
import sqlite3
import hashlib
from random import randint

# Definitions...
occupancies = ['1', '2', '3', '4']
vehicles = ['car', 'bus', 'bicycle', 'motorbike', 'van', 'truck', 'taxi', 'other']


def build_response_refill(where, what):
    '''Builds a refill action that allows part of the currently
    loaded page to be replaced.'''

    text = "<action>\n"
    text += "<type>refill</type>\n"
    text += "<where>" + where + "</where>\n"
    m = base64.b64encode(bytes(what, 'ascii'))
    text += "<what>" + str(m, 'ascii') + "</what>\n"
    text += "</action>\n"
    return text


def build_response_redirect(where):
    '''Builds the page redirection action. It indicates which page the client should fetch.
    If this action is used, only one instance of it should contained in the response
    and there should be no refill action.'''

    text = "<action>\n"
    text += "<type>redirect</type>\n"
    text += "<where>" + where + "</where>\n"
    text += "</action>\n"
    return text


def access_database_parameterized(dbfile, query, values):
    '''Helper function to access a given database and submit a query with parameters.'''

    connect = sqlite3.connect(dbfile)
    cursor = connect.cursor()
    cursor.execute(query, values)
    connect.commit()
    connect.close()


def access_database_with_result_parameterized(dbfile, query, values):
    '''Helper function to access a given database and submit a query with parameters.
    It also returns the results of the query submitted to the database.'''

    connect = sqlite3.connect(dbfile)
    cursor = connect.cursor()
    rows = cursor.execute(query, values).fetchall()
    connect.commit()
    connect.close()
    return rows


def handle_validate(iuser, imagic):
    '''Decides if the combination of user and magic is valid.'''

    # If username and magic cannot be found > index error > except False
    try:
        # look up user in db...
        if iuser == access_database_with_result_parameterized('initial_database.db', "SELECT \
        user_id FROM sessions WHERE \
        user_id = ? AND magic_id = ?", (iuser, imagic))[0][0]:
            print('User good.')
            # look up magic in db
            if imagic == str(access_database_with_result_parameterized('initial_database.db',
                                                                       "SELECT magic_id FROM sessions \
            WHERE user_id = ? AND magic_id = ?", (iuser, imagic))[0][0]):
                print('User and magic good.')
                return True
    except:
        return False


def handle_delete_session(iuser, imagic):
    '''Remove the combination of user and magic from the data base, ending the login.'''

    # the above has been changed to just present an error message saying they are already logged in
    return


def handle_login_request(iuser, imagic, parameters):
    '''Function takes incoming user and magic. Checks if these are valid. If so, creates a suitable
    session record in the database with a random magic identifier that is returned.
    Also returns the response action set (text).'''

    print('Log in request start iuser and imagic:', iuser, imagic)

    if handle_validate(iuser, imagic):
        # the user is already logged in, so end the existing session.
        handle_delete_session(iuser, imagic)
    # Initiate text response...
    text = "<response>\n"
    user = '!'
    magic = ''
    # Parameter handling...
    # If username is missing, send appropriate error message to client...
    if 'usernameinput' not in parameters:
        text += build_response_refill('message', 'Please enter username')
    # If password is missing, send appropriate error message to client...
    elif 'passwordinput' not in parameters:
        text += build_response_refill('message', 'Please enter password')

    # Check that username and password are correct...
    else:
        # Check that username is a valid username...
        user = parameters['usernameinput'][0]
        # Check if the username matches an entry in the db...
        try:
            if access_database_with_result_parameterized('initial_database.db', "SELECT \
            username FROM users \
            WHERE username = ?", (user,))[0][0] == user:
                # Check if the password matches the password of that username in the db...
                m = hashlib.sha1()
                m.update(parameters['passwordinput'][0].encode())
                # print('Username valid')
                # If the password is correct, check if they are already logged in...
                if m.hexdigest() == access_database_with_result_parameterized('initial_database.db',
                                                                              "SELECT password \
                FROM users WHERE username = ?", (user,))[0][0]:
                    # Check if they already have an active session...
                    # print('Password correct')
                    session_already_active = False
                    if len(access_database_with_result_parameterized('initial_database.db',
                                                                     "SELECT * FROM sessions \
                    WHERE user_id = ? AND end_time IS NULL", (user,))) != 0:
                        session_already_active = True
                    if not session_already_active:
                        text += build_response_redirect('/page.html')
                        # Generate random magic session id...
                        for i in range(9):
                            magic += str(randint(0, 9))
                        # Add a session to the db...
                        access_database_parameterized('initial_database.db', "INSERT INTO sessions \
                        (magic_id, user_id, start_time) VALUES (?, ?, CURRENT_TIMESTAMP)",
                                                      (magic, user))
                    else:
                        text += build_response_refill('message', 'You are already logged in')
                else:
                    text += build_response_refill('message', 'Incorrect password')
            else:  # is this else statement doing anything?
                text += build_response_refill('message', 'Invalid username')
        except:
            text += build_response_refill('message', 'Invalid username')

    text += "</response>\n"
    print('Login request end - user and magic:', user, magic)
    return [user, magic, text]


def handle_add_request(iuser, imagic, parameters):
    '''This function takes an incoming username, incoming magic and parameters dictionary.
    Checks whether the session is a valid session, whether all input fields have been completed.
    If the above is satistfied, the function adds input to the database.
    Return the username, magic identifier (these can be empty  strings) and the
    response action set'''

    text = "<response>\n"
    print('Handle add request start - iuser and imagic:', iuser, imagic)
    print('Parameters:', parameters)

    if not handle_validate(iuser, imagic):  # do they have valid username and session id
        # If invalid username and session id > send error message and set display total as --
        print('Invalid session detected')
        text += build_response_refill('message', 'You are not logged in.\
                                                 Please go to the log in page.')
        text += build_response_refill('total', '--')
    else:  # a valid session so parameter validation
        print('Valid session detected')
        # Parameter validation on location...
        if 'locationinput' not in parameters or \
                not all([char.isspace() or char.isalpha() for char in parameters['locationinput'][0]]):
            text += build_response_refill('message', 'Error with location input. Try again.')
            # Update total even if input invalid...
            session_total = access_database_with_result_parameterized('initial_database.db', "SELECT \
            count(add_record_id) FROM add_records \
            WHERE magic_id = ? AND record_removed = 0", (imagic,))[0][0]
            text += build_response_refill('total', '{}'.format(session_total))
        # Parameter validation on occupancy...
        elif 'occupancyinput' not in parameters or parameters['occupancyinput'][0] not in occupancies:
            text += build_response_refill('message', 'Error with occupancy. Try again.')
            # Update total even if input invalid...
            session_total = access_database_with_result_parameterized('initial_database.db', "SELECT \
            count(add_record_id) FROM add_records \
            WHERE magic_id = ? AND record_removed = 0", (imagic,))[0][0]
            text += build_response_refill('total', '{}'.format(session_total))
        # Parameter validation on vehicle...
        elif 'typeinput' not in parameters or parameters['typeinput'][0] not in vehicles:
            text += build_response_refill('message', 'Error with vehicle. Try again.')
            # update total even if input invalid...
            session_total = access_database_with_result_parameterized('initial_database.db', "SELECT \
            count(add_record_id) FROM add_records \
            WHERE magic_id = ? AND record_removed = 0", (imagic,))[0][0]
            text += build_response_refill('total', '{}'.format(session_total))
        else:
            # If all fields are filled out correctly, add data to db...
            access_database_parameterized('initial_database.db', "INSERT INTO add_records \
            (location, type, occupancy, time_of_record, magic_id) \
            VALUES (?, ?, ?, CURRENT_TIMESTAMP, ?)", (parameters['locationinput'][0], parameters['typeinput'][0],
                                                      parameters['occupancyinput'][0], imagic))
            text += build_response_refill('message', 'Entry added.')
            # Update total to the number of records added during that session...
            session_total = access_database_with_result_parameterized('initial_database.db', "SELECT \
            count(add_record_id) FROM add_records \
            WHERE magic_id = ? AND record_removed = 0", (imagic,))[0][0]  # ignores ones which will be removed
            text += build_response_refill('total', '{}'.format(session_total))

    text += "</response>\n"  # send back message is text

    user = iuser  # previously ''
    magic = imagic  # previously ''

    print('Handle add request end - user and magic:', user, magic)

    return [user, magic, text]


def handle_undo_request(iuser, imagic, parameters):
    '''Function takes incoming user and magic, checks whether these are valid.
    Checks whether all input fields have been provided in parameters and then removes
    data from database if above is satisfied. This allows users to correct errors.
    Return the username, magic identifier (these can be empty  strings) and the response action set.'''

    text = "<response>\n"
    if not handle_validate(iuser, imagic):  # invalid session
        print('Invalid session detected.')
        # Update message and total even if they are not logged in...
        text += build_response_refill('message', 'You are not logged in. Please go to the log in page.')
        text += build_response_refill('total', '--')
    else:  # a valid session so process the recording of the entry.
        print('Valid session detected.')
        # Parameter validation...

        if 'locationinput' not in parameters or \
                not all([char.isspace() or char.isalpha() for char in parameters['locationinput'][0]]):
            text += build_response_refill('message', 'Error with location input. Try again.')
            # Update total even if input invalid...
            session_total = access_database_with_result_parameterized('initial_database.db', "SELECT  \
            count(add_record_id) FROM add_records \
            WHERE magic_id = ? AND record_removed = 0", (imagic,))[0][0]
            text += build_response_refill('total', '{}'.format(session_total))

        elif 'occupancyinput' not in parameters or parameters['occupancyinput'][0] not in occupancies:
            text += build_response_refill('message', 'Error with occupancy. Try again.')
            # Update total even if input invalid...
            session_total = access_database_with_result_parameterized('initial_database.db', "SELECT \
            count(add_record_id) FROM add_records \
            WHERE magic_id = ? AND record_removed = 0", (imagic,))[0][0]
            text += build_response_refill('total', '{}'.format(session_total))

        elif 'typeinput' not in parameters or parameters['typeinput'][0] not in vehicles:
            text += build_response_refill('message', 'Please fill in all required fields')
            # update total even if input invalid...
            session_total = access_database_with_result_parameterized('initial_database.db', "SELECT \
            count(add_record_id) FROM add_records \
            WHERE magic_id = ? AND record_removed = 0", (imagic,))[0][0]
            text += build_response_refill('total', '{}'.format(session_total))

        else:  # all fields filled in...
            # initialise parameters...
            ilocation = parameters['locationinput'][0]
            ioccupancy = parameters['occupancyinput'][0]
            itype_ = parameters['typeinput'][0]

            # send query...
            if len(access_database_with_result_parameterized('initial_database.db', "SELECT add_record_id \
            FROM add_records \
            WHERE magic_id = ? AND record_removed = 0 AND location = ? AND type = ? AND occupancy = ? \
            ORDER BY add_record_id LIMIT 1", (imagic, ilocation, itype_, ioccupancy))) != 0:
                # if input found > update db to  removed, send message back to client and update total message...
                # find a record matching the given input...
                access_database_parameterized('initial_database.db', "UPDATE add_records SET record_removed = 1 \
                WHERE add_record_id IN \
                (SELECT add_record_id FROM add_records \
                WHERE magic_id = ? AND record_removed = 0 AND location = ? AND type = ? AND occupancy = ? \
                ORDER BY add_record_id LIMIT 1)", (imagic, ilocation, itype_, ioccupancy))
                text += build_response_refill('message', 'Entry Un-done.')
                session_total = access_database_with_result_parameterized('initial_database.db', "SELECT  \
                count(add_record_id) FROM add_records \
                WHERE magic_id = ? AND record_removed = 0", (imagic,))[0][0]
                text += build_response_refill('total', '{}'.format(session_total))
            else:
                # could not find input...
                text += build_response_refill('message', 'Could not find a matching record \
                from current session. Please note that input is case sensitive.')
                session_total = access_database_with_result_parameterized('initial_database.db', "SELECT \
                count(add_record_id) FROM add_records \
                WHERE magic_id = ? AND record_removed = 0", (imagic,))[0][0]
                text += build_response_refill('total', '{}'.format(session_total))

    text += "</response>\n"
    user = iuser  # previously ''
    magic = imagic  # previously ''
    return [user, magic, text]


def handle_back_request(iuser, imagic, parameters):
    '''Redirects user from summary page to the recording screen.'''

    text = "<response>\n"
    if not handle_validate(iuser, imagic):
        text += build_response_redirect('/index.html')
    else:
        text += build_response_redirect('/summary.html')
    text += "</response>\n"
    user = ''  # iuser  # previously ''
    magic = ''  # imagic  # previously ''
    print('Handle back request is being used')
    return [user, magic, text]


def handle_logout_request(iuser, imagic, parameters):
    '''Checks whether the user has a valid session - incoming user and magic versus database.
    If this is satisfied, logout will be recorded in the database.
    Session magic is revoked.'''

    text = "<response>\n"
    text += build_response_redirect('/index.html')  # redirect to log in page
    user = '!'
    magic = ''  # session magic revoked?
    text += "</response>\n"
    # Update db to end session
    access_database_parameterized('initial_database.db', "UPDATE sessions SET end_time = CURRENT_TIMESTAMP \
    WHERE user_id = ? AND magic_id = ?", (iuser, imagic))
    print('Handle logout request is being used')
    return [user, magic, text]


def handle_summary_request(iuser, imagic, parameters):
    '''Takes incoming user and magic id.
    Sends an update to the client based on the database.'''

    text = "<response>\n"
    print('Handle summary called...')

    if not handle_validate(iuser, imagic):
        text += build_response_redirect('/index.html')
    else:
        # add refill texts for sums...
        text = find_count_with_update_text('initial_database.db', imagic, 'car', text)
        text = find_count_with_update_text('initial_database.db', imagic, 'taxi', text)
        text = find_count_with_update_text('initial_database.db', imagic, 'bus', text)
        text = find_count_with_update_text('initial_database.db', imagic, 'motorbike', text)
        text = find_count_with_update_text('initial_database.db', imagic, 'bicycle', text)
        text = find_count_with_update_text('initial_database.db', imagic, 'van', text)
        text = find_count_with_update_text('initial_database.db', imagic, 'truck', text)
        text = find_count_with_update_text('initial_database.db', imagic, 'other', text)
        # add refill text for updating total...
        session_total = access_database_with_result_parameterized('initial_database.db', "SELECT \
        count(add_record_id) FROM add_records \
        WHERE magic_id = ? AND record_removed = 0", (imagic,))[0][0]
        text += build_response_refill('total', '{}'.format(session_total))
        text += "</response>\n"
        user = iuser  # previously ''
        magic = imagic  # previously ''

    return [user, magic, text]


def find_count_with_update_text(dbfile, imagic, vehicle, text):
    '''Helper function to find the count of a given vehicle and session.'''

    count = access_database_with_result_parameterized(dbfile, "SELECT count(add_record_id) FROM add_records \
    WHERE magic_id = ? AND \
    record_removed = 0 AND type = ?", (imagic, vehicle))[0][0]
    sum_vehicle = 'sum_' + vehicle
    text += build_response_refill(sum_vehicle, '{}'.format(count))

    return text


# HTTPRequestHandler class
class myHTTPServer_RequestHandler(BaseHTTPRequestHandler):

    # GET This function responds to GET requests to the web server.
    def do_GET(self):

        def set_cookies(x, user, magic):
            '''Function adds/updates two cookies returned with a webpage.
            These identify the user who is logged in. The first parameter identifies the user.
            and the second should be used to verify the login session.'''

            ucookie = Cookie.SimpleCookie()
            ucookie['u_cookie'] = user
            x.send_header("Set-Cookie", ucookie.output(header='', sep=''))
            mcookie = Cookie.SimpleCookie()
            mcookie['m_cookie'] = magic
            x.send_header("Set-Cookie", mcookie.output(header='', sep=''))


        def get_cookies(source):
            '''The get_cookies function returns the values of the user and magic cookies if they exist
            it returns empty strings if they do not.'''

            rcookies = Cookie.SimpleCookie(source.headers.get('Cookie'))
            user = ''
            magic = ''
            for keyc, valuec in rcookies.items():
                if keyc == 'u_cookie':
                    user = valuec.value
                if keyc == 'm_cookie':
                    magic = valuec.value
            return [user, magic]

        # Fetch the cookies that arrived with the GET request
        # The identify the user session.
        user_magic = get_cookies(self)

        print(user_magic)

        # Parse the GET request to identify the file requested and the GET parameters
        parsed_path = urllib.parse.urlparse(self.path)

        # Decided what to do based on the file requested.

        # Return a CSS (Cascading Style Sheet) file.
        # These tell the web client how the page should appear.
        if self.path.startswith('/css'):
            self.send_response(200)
            self.send_header('Content-type', 'text/css')
            self.end_headers()
            with open('.' + self.path, 'rb') as file:
                self.wfile.write(file.read())
            file.close()

        # Return a Javascript file.
        # These tell contain code that the web client can execute.
        if self.path.startswith('/js'):
            self.send_response(200)
            self.send_header('Content-type', 'text/js')
            self.end_headers()
            with open('.' + self.path, 'rb') as file:
                self.wfile.write(file.read())
            file.close()

        # A special case of '/' means return the index.html (homepage)
        # of a website
        elif parsed_path.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('./index.html', 'rb') as file:
                self.wfile.write(file.read())
            file.close()

        # Return html pages.
        elif parsed_path.path.endswith('.html'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('.' + parsed_path.path, 'rb') as file:
                self.wfile.write(file.read())
            file.close()

        # The special file 'action' is not a real file, it indicates an action
        # we wish the server to execute.
        elif parsed_path.path == '/action':
            self.send_response(200)  # respond that this is a valid page request
            # extract the parameters from the GET request.
            # These are passed to the handlers.
            parameters = urllib.parse.parse_qs(parsed_path.query)

            if 'command' in parameters:
                # check if one of the parameters was 'command'
                # If it is, identify which command and call the appropriate handler function.
                if parameters['command'][0] == 'login':
                    [user, magic, text] = handle_login_request(user_magic[0], user_magic[1], parameters)
                    # The result to a login attempt will be to set
                    # the cookies to identify the session.
                    set_cookies(self, user, magic)
                elif parameters['command'][0] == 'add':
                    [user, magic, text] = handle_add_request(user_magic[0], user_magic[1], parameters)
                    if user == '!':  # Check if we've been tasked with discarding the cookies.
                        set_cookies(self, '', '')
                elif parameters['command'][0] == 'undo':
                    [user, magic, text] = handle_undo_request(user_magic[0], user_magic[1], parameters)
                    if user == '!':  # Check if we've been tasked with discarding the cookies.
                        set_cookies(self, '', '')
                elif parameters['command'][0] == 'back':
                    [user, magic, text] = handle_back_request(user_magic[0], user_magic[1], parameters)
                    if user == '!':  # Check if we've been tasked with discarding the cookies.
                        set_cookies(self, '', '')
                elif parameters['command'][0] == 'summary':
                    [user, magic, text] = handle_summary_request(user_magic[0], user_magic[1], parameters)
                    if user == '!':  # Check if we've been tasked with discarding the cookies.
                        set_cookies(self, '', '')
                elif parameters['command'][0] == 'logout':
                    [user, magic, text] = handle_logout_request(user_magic[0], user_magic[1], parameters)
                    if user == '!':  # Check if we've been tasked with discarding the cookies.
                        set_cookies(self, '', '')
                else:
                    # The command was not recognised, report that to the user.
                    text = "<response>\n"
                    text += build_response_refill('message', 'Internal Error: Command not recognised.')
                    text += "</response>\n"

            else:
                # There was no command present, report that to the user.
                text = "<response>\n"
                text += build_response_refill('message', 'Internal Error: Command not found.')
                text += "</response>\n"
            self.send_header('Content-type', 'application/xml')
            self.end_headers()
            self.wfile.write(bytes(text, 'utf-8'))
        else:
            # A file that does n't fit one of the patterns above was requested.
            self.send_response(404)
            self.end_headers()
        return


def run():
    '''This is the entry point function to this code.'''

    print('starting server...')
    # You can add any extra start up code here
    # Server settings
    # Choose port 8081 over port 80, which is normally used for a http server
    server_address = ('127.0.0.1', 8081)
    httpd = HTTPServer(server_address, myHTTPServer_RequestHandler)
    print('running server...')
    httpd.serve_forever()  # This function will not return till the server is aborted.


run()
