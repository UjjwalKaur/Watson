import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]


def main():
  """Shows basic usage of the Google Calendar API.
  Prints the start and name of the next 10 events on the user's calendar.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("calendar", "v3", credentials=creds)
    
    page_token = None
    while True:
        calendar_list = service.calendarList().list(pageToken=page_token).execute()
        print('Printing out the different calendar names...')
        for calendar_list_entry in calendar_list['items']:
            print(f"{calendar_list_entry['summary']}: {calendar_list_entry['id']}")
        page_token = calendar_list.get('nextPageToken')
        if not page_token:
            break

    # Call the Calendar API
    tychr_calendar_id = '9516edcfcdd01aab1c8352e98a4816a4cbea47a5d41bf1360b615eecb985903a@group.calendar.google.com'
    now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
    print("Getting the upcoming 10 events")
    events_result = (
        service.events()
        .list(
            calendarId=tychr_calendar_id,
            timeMin=now,
            maxResults=10,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])

    if not events:
      print("No upcoming events found.")
      return

    # Prints the start and name of the next 10 events
    for event in events:
      start = event["start"].get("dateTime", event["start"].get("date"))
      print(start, event["summary"])
      
    create_event(service)

  except HttpError as error:
    print(f"An error occurred: {error}")

def create_event(service):
    # Refer to the Python quickstart on how to setup the environment:
    # https://developers.google.com/calendar/quickstart/python
    # Change the scope to 'https://www.googleapis.com/auth/calendar' and delete any
    # stored credentials.
    tychr_calendar_id = '9516edcfcdd01aab1c8352e98a4816a4cbea47a5d41bf1360b615eecb985903a@group.calendar.google.com'

    event = {
    'summary': 'Create Watson for Tychr',
    'location': 'On my PC',
    'description': 'Yay, let us do this!',
    'start': {
        'dateTime': '2025-03-06T13:00:00+05:30',
        'timeZone': 'Asia/Kolkata',
    },
    'end': {
        'dateTime': '2025-03-06T14:00:00+05:30',
        'timeZone': 'Asia/Kolkata',
    },
    """'recurrence': [
        'RRULE:FREQ=DAILY;COUNT=2'
    ],"""
    'attendees': [
        {'email': 'ujjwalkaur2005@gmail.com'},
    ],
    'reminders': {
        'useDefault': False,
        'overrides': [
        {'method': 'email', 'minutes': 24 * 60},
        {'method': 'popup', 'minutes': 10},
        ],
    },
    }

    event = service.events().insert(calendarId=tychr_calendar_id, body=event).execute()
    print('Event created: %s' % (event.get('htmlLink')))
        
        
if __name__ == "__main__":
  main()