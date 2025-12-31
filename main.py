from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from datetime import datetime, timezone
from dateutil import parser
import os
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/calendar']


def get_calendar_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            'client_secret_282718702884-77sc27oe2uq40q4r7rn6jp352c7lt81q.apps.googleusercontent.com.json', SCOPES
        )
        creds = flow.run_local_server(port=0, access_type='offline')
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('calendar', 'v3', credentials=creds)


def add_event():
    service = get_calendar_service()

    title = input("Event Title: ")
    date_input = input("Date (DD:MM:YYYY): ")
    start_time = input("Start Time (HH:MM, 24-hour): ")
    end_time = input("End Time (HH:MM, 24-hour): ")
    reminder = input("Reminder (minutes before): ")

    try:
        date_obj = datetime.strptime(date_input, "%d:%m:%Y")
        date = date_obj.strftime("%Y-%m-%d")
    except ValueError:
        print("Invalid date format. Use DD:MM:YYYY")
        return

    try:
        reminder = int(reminder)
    except ValueError:
        print("Reminder must be an integer")
        return

    event = {
        'summary': title,
        'start': {
            'dateTime': f"{date}T{start_time}:00",
            'timeZone': 'Asia/Kolkata'
        },
        'end': {
            'dateTime': f"{date}T{end_time}:00",
            'timeZone': 'Asia/Kolkata'
        },
        'reminders': {
            'useDefault': False,
            'overrides': [{'method': 'popup', 'minutes': reminder}]
        }
    }

    try:
        service.events().insert(
            calendarId='primary', body=event
        ).execute()
        print("Event added successfully")
    except Exception as e:
        print("Failed to add event:", e)
    events = show_events()    


def show_events():
    service = get_calendar_service()

    now = datetime.now(timezone.utc).isoformat()
    events = service.events().list(
        calendarId='primary',
        timeMin=now,
        maxResults=20,
        singleEvents=True,
        orderBy='startTime'
    ).execute().get('items', [])

    events.sort(
        key=lambda e: (
            e['start'].get('dateTime', ''),
            e['end'].get('dateTime', ''),
            e.get('summary', '')
        )
    )

    if not events:
        print("No upcoming events found")
        return []

    print("\nUpcoming Events:")
    for index, event in enumerate(events, start=1):
        start_time = event['start'].get('dateTime')
        if start_time:
            local_time = parser.parse(start_time).astimezone()
            formatted = local_time.strftime('%d:%m:%Y %H:%M')
            print(f"{index}. {formatted} | {event['summary']}")

    return events


def update_event():
    service = get_calendar_service()
    events = show_events()

    if not events:
        return

    try:
        choice = int(input("Select event number to update: "))
        if choice < 1 or choice > len(events):
            print("Invalid selection")
            return
        event = events[choice - 1]
    except (ValueError, IndexError):
        print("Invalid selection")
        return

    new_title = input(
        f"New title (press Enter to keep '{event['summary']}'): "
    )
    if new_title.strip():
        event['summary'] = new_title

    start_dt = parser.parse(event['start']['dateTime']).astimezone()
    end_dt = parser.parse(event['end']['dateTime']).astimezone()

    new_date = input(
        f"New date DD:MM:YYYY (Enter to keep {start_dt.strftime('%d:%m:%Y')}): "
    )
    if new_date.strip():
        try:
            date_obj = datetime.strptime(new_date, "%d:%m:%Y")
            date = date_obj.strftime("%Y-%m-%d")
        except ValueError:
            print("Invalid date format")
            return
    else:
        date = start_dt.strftime("%Y-%m-%d")

    new_start = input(
        f"New start time HH:MM (Enter to keep {start_dt.strftime('%H:%M')}): "
    ) or start_dt.strftime('%H:%M')

    new_end = input(
        f"New end time HH:MM (Enter to keep {end_dt.strftime('%H:%M')}): "
    ) or end_dt.strftime('%H:%M')

    old_reminder = event.get('reminders', {}).get('overrides', [])
    old_minutes = old_reminder[0]['minutes'] if old_reminder else 10

    new_reminder = input(
        f"New reminder minutes (Enter to keep {old_minutes}): "
    )
    if new_reminder.strip():
        try:
            new_reminder = int(new_reminder)
        except ValueError:
            print("Invalid reminder value")
            return
    else:
        new_reminder = old_minutes

    event['start']['dateTime'] = f"{date}T{new_start}:00"
    event['end']['dateTime'] = f"{date}T{new_end}:00"
    event['start']['timeZone'] = 'Asia/Kolkata'
    event['end']['timeZone'] = 'Asia/Kolkata'
    event['reminders'] = {
        'useDefault': False,
        'overrides': [{'method': 'popup', 'minutes': new_reminder}]
    }

    try:
        service.events().update(
            calendarId='primary',
            eventId=event['id'],
            body=event
        ).execute()
        print("Event updated successfully")
    except Exception as e:
        print("Failed to update event:", e)


def delete_event():
    service = get_calendar_service()
    events = show_events()

    if not events:
        return

    try:
        choice = int(input("Select event number to delete: "))
        if choice < 1 or choice > len(events):
            print("Invalid selection")
            return
        event = events[choice - 1]
    except (ValueError, IndexError):
        print("Invalid selection")
        return

    try:
        service.events().delete(
            calendarId='primary',
            eventId=event['id']
        ).execute()
        print("Event deleted successfully")
    except Exception as e:
        print("Failed to delete event:", e)


def main():
    while True:
        print("\nGoogle Calendar CLI")
        print("1. Add Event")
        print("2. View Upcoming Events")
        print("3. Update Event")
        print("4. Delete Event")
        print("5. Exit")

        choice = input("Choose an option: ").strip()

        if not choice:
            continue 

        if choice == "1":
            add_event()
        elif choice == "2":
            show_events()
        elif choice == "3":
            update_event()
        elif choice == "4":
            delete_event()
        elif choice == "5":
            break
        else:
            print("Invalid option selected")


if __name__ == "__main__":
    main()