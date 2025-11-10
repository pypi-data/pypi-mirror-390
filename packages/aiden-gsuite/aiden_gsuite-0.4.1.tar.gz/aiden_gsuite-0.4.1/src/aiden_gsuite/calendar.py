from googleapiclient.discovery import build
import httplib2
from oauth2client.client import AccessTokenCredentials
from aiden_gsuite.credential import Credential, MCP_AGENT
import logging
import traceback
from datetime import datetime
import pytz

class CalendarService():
    def __init__(self, credential: Credential):
        credentials = AccessTokenCredentials(credential.token, MCP_AGENT)
        http = httplib2.Http()
        http = credentials.authorize(http)
        self.service = build('calendar', 'v3', http=http)
    
    def list_calendars(self) -> list:
        """
        Lists all calendars accessible by the user.
        
        Returns:
            list: List of calendar objects with their metadata
        """
        calendar_list = self.service.calendarList().list().execute()

        calendars = []
        
        for calendar in calendar_list.get('items', []):
            if calendar.get('kind') == 'calendar#calendarListEntry':
                calendars.append({
                    'id': calendar.get('id'),
                    'summary': calendar.get('summary'),
                    'primary': calendar.get('primary', False),
                    'time_zone': calendar.get('timeZone'),
                    'etag': calendar.get('etag'),
                    'access_role': calendar.get('accessRole')
                })

        return calendars

    def get_events(self, time_min=None, time_max=None, max_results=250, show_deleted=False, calendar_id: str ='primary'):
        """
        Retrieve calendar events within a specified time range.
        
        Args:
            time_min (str, optional): Start time in RFC3339 format. Defaults to current time.
            time_max (str, optional): End time in RFC3339 format
            max_results (int): Maximum number of events to return (1-2500)
            show_deleted (bool): Whether to include deleted events
            
        Returns:
            list: List of calendar events
        """
        # If no time_min specified, use current time
        if not time_min:
            time_min = datetime.now(pytz.UTC).isoformat()
            
        # Ensure max_results is within limits
        max_results = min(max(1, max_results), 2500)
        
        # Prepare parameters
        params = {
            'calendarId': calendar_id,
            'timeMin': time_min,
            'maxResults': max_results,
            'singleEvents': True,
            'orderBy': 'startTime',
            'showDeleted': show_deleted
        }
        
        # Add optional time_max if specified
        if time_max:
            params['timeMax'] = time_max
            
        # Execute the events().list() method
        events_result = self.service.events().list(**params).execute()
        
        # Extract the events
        events = events_result.get('items', [])
        
        # Process and return the events
        processed_events = []
        for event in events:
            processed_event = {
                'id': event.get('id'),
                'summary': event.get('summary'),
                'description': event.get('description'),
                'start': event.get('start'),
                'end': event.get('end'),
                'status': event.get('status'),
                'creator': event.get('creator'),
                'organizer': event.get('organizer'),
                'attendees': event.get('attendees'),
                'location': event.get('location'),
                'hangoutLink': event.get('hangoutLink'),
                'conferenceData': event.get('conferenceData'),
                'recurringEventId': event.get('recurringEventId')
            }
            processed_events.append(processed_event)
            
        return processed_events
        
    def create_event(self, summary: str, start_time: str, end_time: str, 
                location: str | None = None, description: str | None = None, 
                attendees: list | None = None, send_notifications: bool = True,
                timezone: str | None = None,
                calendar_id : str = 'primary') -> dict | None:
        """
        Create a new calendar event.
        
        Args:
            summary (str): Title of the event
            start_time (str): Start time in RFC3339 format
            end_time (str): End time in RFC3339 format
            location (str, optional): Location of the event
            description (str, optional): Description of the event
            attendees (list, optional): List of attendee email addresses
            send_notifications (bool): Whether to send notifications to attendees
            timezone (str, optional): Timezone for the event (e.g. 'America/New_York')
            
        Returns:
            dict: Created event data or None if creation fails
        """
        # Prepare event data
        event = {
            'summary': summary,
            'start': {
                'dateTime': start_time,
                'timeZone': timezone or 'UTC',
            },
            'end': {
                'dateTime': end_time,
                'timeZone': timezone or 'UTC',
            }
        }
        
        # Add optional fields if provided
        if location:
            event['location'] = location
        if description:
            event['description'] = description
        if attendees:
            event['attendees'] = [{'email': email} for email in attendees]
            
        # Create the event
        created_event = self.service.events().insert(
            calendarId=calendar_id,
            body=event,
            sendNotifications=send_notifications
        ).execute()
        
        return created_event
        
    def delete_event(self, event_id: str, send_notifications: bool = True, calendar_id: str = 'primary'):
        """
        Delete a calendar event by its ID.
        
        Args:
            event_id (str): The ID of the event to delete
            send_notifications (bool): Whether to send cancellation notifications to attendees
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        self.service.events().delete(
            calendarId=calendar_id,
            eventId=event_id,
            sendNotifications=send_notifications
        ).execute()
        
    def modify_event(self, event_id: str, summary: str, start_time: str, end_time: str, 
                location: str | None = None, description: str | None = None, 
                attendees: list | None = None, send_notifications: bool = True,
                timezone: str | None = None,
                calendar_id : str = 'primary') -> dict | None:
        """
        Modify an existing calendar event.
        """

        event = self.service.events().get(
            calendarId=calendar_id,
            eventId=event_id
        ).execute()
        
        if event:
            event['summary'] = summary
            event['start'] = {
                'dateTime': start_time,
                'timeZone': timezone or 'UTC',
            }
            event['end'] = {
                'dateTime': end_time,
                'timeZone': timezone or 'UTC',
            }
            if location:
                event['location'] = location
            if description:
                event['description'] = description
            if attendees:
                event['attendees'] = [{'email': email} for email in attendees]
            
            updated_event = self.service.events().update(
                calendarId=calendar_id,
                eventId=event_id,
                body=event,
                sendNotifications=send_notifications
            ).execute()
            
            return updated_event
        
        else:
            logging.error(f"Event {event_id} not found")
            raise RuntimeError(f"Event {event_id} not found")