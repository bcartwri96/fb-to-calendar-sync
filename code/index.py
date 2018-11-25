# Written by Ben Cartwright while bored on holidays, Nov 2018
# Presumes we have an access token already for the user,
# perhaps I'll extend it later but for the moment it's good for me!

# imports
import facebook as gr
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.file import Storage
from oauth2client import tools, client
from apiclient import discovery
import httplib2
import os
from datetime import datetime as dt
from datetime import timedelta as td
import dateutil.parser as dp
import pickle
import requests as r

# globals
global graph
global in_cal

graph = None
in_cal = []

# calendar id
cal_id = "672j3lukabp5f4e9uhqa1i8eu0@group.calendar.google.com"

def get_file_line(path):
    try:
        with open(path, 'rb') as infile:
            res = infile.readlines(0)
    except FileNotFoundError:
        print("File not found. Cannot read "+path)
        exit()
    return res[0].decode("utf-8").strip()

def put_file_line(path, data):
    with open(path, 'wb') as outfile:
        pickle.dump(data, outfile)
    return 1


# get sensitive data
f_client_secret = get_file_line("code/client_secret")
at = get_file_line("code/user_token")

# get the access token
f_client_id = "320764471845088"
f_url = "http://localhost/"
f_creds = "client_credentials"
print(f_client_id, f_client_secret)
http_req = r.get('https://graph.facebook.com/oauth/access_token?client_id='+f_client_id+"&client_secret="+f_client_secret+"&redirect_uri="+f_url+"&grant_type="+f_creds+"")
app_token = http_req.json()['access_token']

# AT THE TIME OF WRITING, Facebook does not allow developers to get user
# access tokens programmatically in Python - need to use JS or something
# and a frontend browser, so instead here is a hardcoded version and after
# it expires, you need to replace it with another one and *ensure you extend
# it!*

# TOKEN EXPIRES IN 3 MONTHS FROM NOVEMBER 22, 2018
# Site: https://developers.facebook.com/tools/debug/accesstoken/

def main():
    global in_cal
    print('Init')
    # get the list of added events
    try:
        with open("added.json", 'rb+') as infile:
            in_cal = pickle.load(infile)
    except FileNotFoundError:
        in_cal = []

    graph = gr.GraphAPI(access_token=at)

    # authenticate with google
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'fb-calendar.json')

    store = Storage(credential_path)
    creds = store.get()
    if not creds or creds.invalid:
        auth = OAuth2WebServerFlow(client_id=get_file_line("code/g_client_id"),
                            client_secret=get_file_line("code/g_client_secret"),
                            scope="https://www.googleapis.com/auth/calendar",
                            redirect_uri="http://localhost/")
        creds = tools.run_flow(auth, store)


    # now we can use the creds and send our access token along for the ride!
    http = creds.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    all_e = graph.get_object(id="me", fields="events{id, name, timezone, start_time, end_time, event_times, rsvp_status}")
    events = all_e['events']['data']

    for e in events:
        ename = e['name']
        eid = e['id']
        etimezone = e['timezone']
        rsvp = e['rsvp_status']
        try:
            # for i in range(0, len(e['event_times']), 1)):
            estart = e['start_time']
            eend = e['end_time']
            if estart == '' and eend == '':
                estart = e['event_times'][0]['start_time']
                eend = e['event_times'][0]['end_time']
        except KeyError:
            # might be that only start time specified, so try get the start time
            try:
                estart = e['start_time']
                if estart != '':
                    # problem is, we have no enddate
                    eend = estart
                    eend = dp.parse(eend)
                    eend = eend + td(hours=1)
                    eend = str(eend.isoformat())
            except KeyError:
                estart=''
                eend=''

        if not (eid in in_cal) and rsvp == "attending":
            # we want to add it into the calendar
            add = {
                'summary': ename,
                'start': {
                    'dateTime': estart,
                    'timeZone': etimezone,
                },
                'end': {
                    'dateTime': eend,
                    'timeZone': etimezone,
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'popup', 'minutes': 60},
                    ],
                },
            }
            # event = service.events().insert(calendarId=cal_id, body=add).execute()
            # print ('Event created: %s' % (event.get('htmlLink')))
            in_cal.append(eid)

        # reset.
        estart = ''
        eend = ''


def cleanup():
    global in_cal
    put_file_line("added.json", in_cal)

main()
cleanup()
