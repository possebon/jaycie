from apiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
import pickle
import os
import datefinder
import datetime
import pytz
import json
from flask import Flask
from flask import request, jsonify
from flask import Response
import logger

businessHours = [None]*7
businessHours[0] = {'start': '13:00', 'end': '19:00'}
businessHours[1] = {'start': '09:00', 'end': '19:00'}
businessHours[2] = {'start': '09:00', 'end': '19:00'}
businessHours[3] = {'start': '09:00', 'end': '19:00'}
businessHours[4] = {'start': '09:00', 'end': '21:00'}
businessHours[5] = {'start': '09:00', 'end': '22:00'}
businessHours[6] = {'start': None, 'end': None}

date_time_format_string = "%Y-%m-%dT%H:%M:%S"
date_time_format_string_tz = "%Y-%m-%dT%H:%M:%S%z"

app = Flask(__name__)

def check_slot(start_time, busy_slots):
    if (type(start_time) is not datetime.datetime):
        matches = list(datefinder.find_dates(start_time))
        start_time = matches[0]

    if len(busy_slots) == 0:

        weekday = start_time.weekday()

        available_hours = [x for x in range(
        int(businessHours[weekday]['start'][0:2]), int(businessHours[weekday]['end'][0:2]))]

        return True, available_hours

    weekday = datetime.datetime.strptime(
        busy_slots[0]['start'], date_time_format_string_tz).weekday()

    available_hours = [x for x in range(
        int(businessHours[weekday]['start'][0:2]), int(businessHours[weekday]['end'][0:2]))]

    slot_available = True

    for slot in busy_slots:
        slot_start = datetime.datetime.strptime(
            slot['start'], date_time_format_string_tz).time()

        if slot_start.hour in available_hours:
            # Need to remove from available_hours the hour start of busy_slot
            available_hours.remove(slot_start.hour)


    for slot in busy_slots:
        slot_start = datetime.datetime.strptime(
            slot['start'], date_time_format_string_tz).time()
        slot_end = datetime.datetime.strptime(
            slot['end'], date_time_format_string_tz).time()

        if (start_time.time() == slot_start) and (start_time.time() >= slot_start and start_time.time() < slot_end):
            # Means that this time is already reserved or that requested start time conflicts with another slot reserved
            slot_available = False
            break

    return slot_available, available_hours

def get_calendar(calendar_name):
    #Fetch all available calendars
    calendars = google_service.calendarList().list().execute()

    for calendar in calendars['items']:
        if (calendar['summary'] == calendar_name):
            return calendar['id'], calendar['timeZone']

def check_calendar(calendar_name, event_date_time):
    calendar_id, calendar_timezone = get_calendar(calendar_name)
    matches = list(datefinder.find_dates(event_date_time))

    if len(matches):
        start_time = matches[0]


    return True

def create_calendar_event(data):

    calendar_name = data['calendarName']
    start_time = data['start']['dateTime']
    end_time = data['end']['dateTime']

    if 'reminders' not in data:
        print("Sem o elemento reminders")
        data['reminders'] = {
            "useDefault": "False",
            "overrides": [

                {
                    "method": "popup",
                    "minutes": 10
                }]
        }

    print(data)
    response_appointment = {}
    response_appointment['appointment_confirmed'] = False

    calendar_id, calendar_timezone = get_calendar(calendar_name)

    is_free, available_hours = check_calendar_freebusy(
          calendar_id, calendar_timezone, start_time, end_time)
    response_appointment['available_hours'] = available_hours

    if not is_free:
        response_appointment['appointment_confirmed'] = is_free
        return response_appointment, 200

    if (type(start_time) is not datetime.datetime):
        matches = list(datefinder.find_dates(start_time))
        start_time = matches[0]

    if (type(end_time) is not datetime.datetime):
        matches = list(datefinder.find_dates(end_time))
        end_time = matches[0]

    if 'calendarName' in data:
        data.pop('calendarName', None)

    data['start']['dateTime'] = start_time.strftime(date_time_format_string)

    data['end']['dateTime'] = end_time.strftime(
            date_time_format_string)
    try:
        response_google = google_service.events().insert(calendarId=calendar_id, body=data).execute()
        if (response_google['status'] == 'confirmed'):
            response_appointment['appointment_confirmed'] = True
            return response_appointment, 200
    except Exception as e:
        print(e)



def check_calendar_freebusy(calendar_id, time_zone, start_time, end_time):
    if (type(start_time) is not datetime.datetime):
        matches = list(datefinder.find_dates(start_time))
        start_time = matches[0]

    if (type(end_time) is not datetime.datetime):
        matches = list(datefinder.find_dates(end_time))
        end_time = matches[0]

    tz_offset = datetime.datetime.now(
        pytz.timezone(time_zone)).strftime('%z')

    weekday = start_time.weekday()

    day_date = start_time.date()

    agenda_start = day_date.strftime(
        "%Y-%m-%d") + ' ' + businessHours[weekday]['start']

    agenda_start = datetime.datetime.strptime(agenda_start,  "%Y-%m-%d %H:%M")

    agenda_end = day_date.strftime("%Y-%m-%d") + \
        ' ' + businessHours[weekday]['end']

    agenda_end = datetime.datetime.strptime(agenda_end,  "%Y-%m-%d %H:%M")

    google_payload = {
        "timeMin": agenda_start.strftime(date_time_format_string) + tz_offset,
        "timeMax": agenda_end.strftime(date_time_format_string) + tz_offset,
        "timeZone": time_zone,
        "items": [
            {
                "id": calendar_id
            }
        ]
    }
    try:
        response_google = google_service.freebusy().query(body=google_payload).execute()
        slot_available = True
        other_slots_available = None
        busy_slots = response_google['calendars'][calendar_id]['busy']
        slot_available, other_slots_available = check_slot(start_time, busy_slots)

        return slot_available, other_slots_available

    except Exception as e:
        print(e)
    
    print(response_google)

def edit_calendar_event(calendar_name, event_date_time, event_duration, event_title, event_description):
    calendar_id, calendar_timezone = get_calendar(calendar_name)
    matches = list(datefinder.find_dates(event_date_time))

    if len(matches):
        start_time = matches[0]
        end_time = start_time + datetime.timedelta(minutes=event_duration)
        
    start_time = event_date_time

    event = {
        'summary': event_title,
        # 'location': location,
        'description': event_description,
        'start': {
            'dateTime': start_time.strftime(date_time_format_string),
            'timeZone': calendar_timezone,
        },
        'end': {
            'dateTime': end_time.strftime(date_time_format_string),
            'timeZone': calendar_timezone,
        },
        # 'reminders': {
        #     'useDefault': False,
        #     'overrides': [
        #         {'method': 'email', 'minutes': 24 * 60},
        #         {'method': 'popup', 'minutes': 10},
        #     ],
        # },
    }

    result = google_service.events().insert(calendarId=calendar_id, body=event).execute()

    return result


def delete_calendar_event(calendar_name, event_date_time, event_title, event_description):
    calendar_id, calendar_timezone = get_calendar(calendar_name)
    matches = list(datefinder.find_dates(event_date_time))

    if len(matches):
        start_time = matches[0]
        
    start_time = event_date_time
    return True

@app.route('/')
def backend_index():
    return "Jaycie Backend"

   
@app.route('/calendar/appointment', methods=['GET', 'POST', 'DELETE'])
def api_appointment():
    data = request.get_json()
    if request.method == 'POST':
        print(data)
        response_calendar, status_code = create_calendar_event(data)

    elif request.method == 'GET':
        print("TODO")
        
    elif request.method == 'DELETE':
        print("TODO")

    return jsonify(response_calendar), status_code

if __name__ == "__main__":
    global google_service
    scopes = ['https://www.googleapis.com/auth/calendar']
    timeZone = 'America/Sao_Paulo'

    exec_path = os.path.dirname(os.path.realpath(__file__))

    # Instantiate Google Calendar Services API
    flow = InstalledAppFlow.from_client_secrets_file(
        exec_path + "/client_secret.json", scopes=scopes)


    if os.path.exists(exec_path +'/token.pkl'):
        credentials = pickle.load(open(exec_path + "/token.pkl", "rb"))
    else:
        credentials = flow.run_console()
        pickle.dump(credentials, open(exec_path + "/token.pkl", "wb"))

    google_service = build(
        "calendar", "v3", credentials=credentials, cache_discovery=False, cache=None)


    # Backend Flask app
    app.run(host='0.0.0.0', port='5000', debug=True)
