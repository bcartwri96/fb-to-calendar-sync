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

# globals
graph = None
in_cal = []

# store access token for FB
at = "EAAFzFSvJ2zMBAGkYbByDTfsloCic2DzoxzC\
bEi6XQvN6PKxwpbzjIaBP2TAlb3ijkG49rUTYjBZCsFSnaaPzCdm2rSC8y57vZA2VFiK3Y\
JkkRoDpx3S0NmDFIVF3j8QwEPP2NZCE5NJdl1ZAW5PtNFlMBweBKf7HlKy7tBDZAII5b2rk\
VGJWsr8uOBapZAmI0ZD"

at = "EAAFzFSvJ2zMBAFcmesZCsB3DXp3muSJEvsiLoBMGxDpZBzmupHgBdjkXVnN9Ja\
XEacbLRReiZCIbSZCSXpHtIn6WsW1DoZCu3bUWF9qFgAAJTcTZBxtyJebgOcd7m3OJhguNs\
EZAZAsH6WHvEEmxXQhcNB6opIZAeVIYZD"

def auth():
    return None

def events():
    all_e = graph.get_object(id="me", fields="events")
    return all_e

def main():
    # check auth
    # auth = auth()

    graph = gr.GraphAPI(access_token=at)

    # authenticate with google
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'fb-calendar.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        auth = OAuth2WebServerFlow(client_id='241170527866-fao8m3nto0hl6o5g56ig7r4410infked.apps.googleusercontent.com',
                            client_secret="fblU5ZmNDBFkV-KJjWzNSrGh",
                            scope="https://www.googleapis.com/auth/calendar",
                            redirect_uri="http://localhost/")
        creds = tools.run_flow(auth, store)


    # now we can use the creds and send our access token along for the ride!
    http = credentials.authorize(httplib2.Http())
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

        if not (eid in installed) and rsvp == "attending":
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
            print(add)
            event = service.events().insert(calendarId='q6g7u29qdbeej0furdoq8s7gj8@group.calendar.google.com', body=add).execute()
            print ('Event created: %s' % (event.get('htmlLink')))
            if event.get('htmlLink') != '':
                # event was created, now we need to add it to the in_cal
                in_cal.append(eid)

            # reset.
            estart = ''
            eend = ''
main()
