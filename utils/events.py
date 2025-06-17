"""
Event management utilities for the Nimbus Discord bot.

This module provides utilities for event management, including:
- Event class for representing scheduled events
- EventManager class for managing events
- Functions for loading, saving, and retrieving events
"""
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from utils.config import load_json_data, save_json_data

# File to store events
EVENTS_FILE = 'data/events.json'

class Event:
    """
    Represents a scheduled event with date, time, and organizer information.
    """
    def __init__(self, title: str, date: str, time: str, organizer_id: int, message_id: int):
        """
        Initialize a new event.
        
        Args:
            title: Event title
            date: Event date in DD/MM/YYYY format
            time: Event time in HH:MM AM/PM format
            organizer_id: Discord ID of the event organizer
            message_id: Discord message ID of the event announcement
        """
        self.title = title
        self.date = date
        self.time = time
        self.organizer_id = organizer_id
        self.message_id = message_id
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert event to dictionary for JSON serialization.
        
        Returns:
            Dict containing event data
        """
        return {
            'title': self.title,
            'date': self.date,
            'time': self.time,
            'organizer_id': self.organizer_id,
            'message_id': self.message_id
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Event':
        """
        Create an Event object from dictionary data.
        
        Args:
            data: Dictionary containing event data
            
        Returns:
            Event object
        """
        return Event(
            data['title'],
            data['date'],
            data['time'],
            data['organizer_id'],
            data['message_id']
        )
    
    def get_datetime(self) -> datetime:
        """
        Convert event date and time to datetime object.
        
        Returns:
            datetime: Parsed datetime object
            
        Raises:
            ValueError: If the date/time format is invalid
        """
        date_str = f"{self.date} {self.time}"
        try:
            # Try 12-hour format first
            return datetime.strptime(date_str, "%d/%m/%Y %I:%M %p")
        except ValueError:
            # Try 24-hour format
            return datetime.strptime(date_str, "%d/%m/%Y %H:%M")

class EventManager:
    """
    Manages event creation, storage, and retrieval.
    """
    def __init__(self):
        """Initialize the event manager and load existing events."""
        self.events: List[Event] = []
        self.load_events()
    
    def load_events(self) -> None:
        """Load events from file."""
        try:
            data = load_json_data(EVENTS_FILE, [])
            self.events = [Event.from_dict(event_data) for event_data in data]
            if self.events:
                print(f"✓ Loaded {len(self.events)} events from storage")
        except Exception as e:
            logging.error(f"Error loading events: {e}")
            self.events = []
    
    def save_events(self) -> bool:
        """
        Save events to file.
        
        Returns:
            bool: True if successful, False otherwise
        """
        return save_json_data(EVENTS_FILE, [event.to_dict() for event in self.events])
    
    def add_event(self, event: Event) -> None:
        """
        Add a new event and save to file.
        
        Args:
            event: Event to add
        """
        self.events.append(event)
        self.save_events()
    
    def get_upcoming_events(self) -> List[Event]:
        """
        Get all upcoming events sorted by date.
        
        Returns:
            List of upcoming events sorted by date
        """
        now = datetime.now()
        upcoming = [
            event for event in self.events
            if event.get_datetime() > now
        ]
        return sorted(upcoming, key=lambda e: e.get_datetime())
    
    def cleanup_past_events(self) -> None:
        """
        Remove events that have already occurred.
        
        This method removes events with dates in the past and saves
        the updated event list if any events were removed.
        """
        now = datetime.now()
        original_count = len(self.events)
        self.events = [event for event in self.events if event.get_datetime() > now]
        if len(self.events) < original_count:
            self.save_events()