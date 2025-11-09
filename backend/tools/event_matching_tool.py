"""
Event Matching Tool for finding anxiety-appropriate social activities.

This tool fetches events from various sources (Meetup, Eventbrite, TAMU)
and matches them to user preferences and anxiety levels.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import httpx

from backend.core import get_settings

settings = get_settings()


class EventMatchingTool:
    """
    Event matching integration for personalized activity recommendations.

    Analyzes:
    - Event size (small groups for high anxiety)
    - Activity structure (structured activities preferred)
    - Proximity to user
    - Interest alignment (music, tech, sports, etc.)
    """

    def __init__(self):
        """Initialize Event Matching Tool."""
        self.client = httpx.AsyncClient()

    async def search_meetup_events(
        self,
        location: str = "College Station, TX",
        radius: int = 10,
        categories: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for events on Meetup.

        Args:
            location: City/location to search
            radius: Search radius in miles
            categories: List of category IDs to filter

        Returns:
            List of Meetup events
        """
        if not settings.meetup_api_key:
            return []

        try:
            # Note: Meetup API v3 is being replaced. This is a placeholder.
            # In production, use GraphQL API or official SDK
            url = "https://api.meetup.com/find/upcoming_events"
            params = {
                "key": settings.meetup_api_key,
                "text": location,
                "radius": radius,
                "page": 20,
            }

            response = await self.client.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()

            events = []
            for event in data.get("events", []):
                events.append(
                    {
                        "id": event.get("id"),
                        "name": event.get("name"),
                        "description": event.get("description", "")[:200],
                        "time": event.get("time"),
                        "venue": event.get("venue", {}).get("name"),
                        "group": event.get("group", {}).get("name"),
                        "rsvp_count": event.get("yes_rsvp_count", 0),
                        "link": event.get("link"),
                        "source": "meetup",
                    }
                )

            return events

        except Exception as error:
            print(f"Meetup API error: {error}")
            return []

    async def search_eventbrite_events(
        self, location: str = "College Station, TX"
    ) -> List[Dict[str, Any]]:
        """
        Search for events on Eventbrite.

        Args:
            location: City/location to search

        Returns:
            List of Eventbrite events
        """
        if not settings.eventbrite_token:
            return []

        try:
            url = "https://www.eventbriteapi.com/v3/events/search/"
            headers = {"Authorization": f"Bearer {settings.eventbrite_token}"}
            params = {
                "location.address": location,
                "location.within": "10mi",
                "expand": "venue",
                "page_size": 20,
            }

            response = await self.client.get(url, headers=headers, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()

            events = []
            for event in data.get("events", []):
                events.append(
                    {
                        "id": event.get("id"),
                        "name": event.get("name", {}).get("text"),
                        "description": event.get("description", {}).get("text", "")[:200],
                        "start": event.get("start", {}).get("local"),
                        "end": event.get("end", {}).get("local"),
                        "venue": event.get("venue", {}).get("name") if event.get("venue") else None,
                        "capacity": event.get("capacity"),
                        "link": event.get("url"),
                        "source": "eventbrite",
                    }
                )

            return events

        except Exception as error:
            print(f"Eventbrite API error: {error}")
            return []

    async def search_tamu_events(self) -> List[Dict[str, Any]]:
        """
        Search for events from TAMU events calendar.
        Note: This is a placeholder. TAMU may not have a public API.

        Returns:
            List of TAMU events (placeholder)
        """
        # Placeholder for TAMU events
        # In production, scrape TAMU events page or use official API if available
        return []

    async def get_all_events(self, location: str = "College Station, TX") -> List[Dict[str, Any]]:
        """
        Fetch events from all sources.

        Args:
            location: City/location to search

        Returns:
            Combined list of events from all sources
        """
        meetup_events = await self.search_meetup_events(location)
        eventbrite_events = await self.search_eventbrite_events(location)
        tamu_events = await self.search_tamu_events()

        all_events = meetup_events + eventbrite_events + tamu_events
        return all_events

    async def filter_by_anxiety_level(
        self, events: List[Dict[str, Any]], anxiety_level: str
    ) -> List[Dict[str, Any]]:
        """
        Filter events based on user's social anxiety level.

        Args:
            events: List of events to filter
            anxiety_level: "low", "medium", or "high"

        Returns:
            Filtered list of anxiety-appropriate events
        """
        if anxiety_level == "low":
            # All events are OK
            return events

        elif anxiety_level == "medium":
            # Prefer smaller events (< 30 people)
            return [e for e in events if e.get("rsvp_count", 0) < 30 or e.get("capacity", 0) < 30]

        elif anxiety_level == "high":
            # Only small, structured events (< 15 people)
            return [e for e in events if e.get("rsvp_count", 0) < 15 or e.get("capacity", 0) < 15]

        return events

    async def match_interests(
        self, events: List[Dict[str, Any]], interests: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Match events to user interests based on keywords.

        Args:
            events: List of events to match
            interests: List of interest keywords (e.g., ["music", "tech", "sports"])

        Returns:
            Events matching user interests
        """
        if not interests:
            return events

        matched_events = []
        for event in events:
            event_text = (
                f"{event.get('name', '')} {event.get('description', '')} {event.get('group', '')}"
            ).lower()

            for interest in interests:
                if interest.lower() in event_text:
                    matched_events.append(event)
                    break

        return matched_events

    async def recommend_events(
        self,
        location: str = "College Station, TX",
        anxiety_level: str = "medium",
        interests: Optional[List[str]] = None,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Get personalized event recommendations.

        Args:
            location: User's location
            anxiety_level: User's social anxiety level
            interests: User's interests
            limit: Maximum number of recommendations

        Returns:
            List of recommended events
        """
        # Fetch all events
        all_events = await self.get_all_events(location)

        # Filter by anxiety level
        filtered_events = await self.filter_by_anxiety_level(all_events, anxiety_level)

        # Match interests
        if interests:
            filtered_events = await self.match_interests(filtered_events, interests)

        # Return top N
        return filtered_events[:limit]


def get_event_matching_tool_description() -> str:
    """Get tool description for MCP registration."""
    return """
    Matches users with anxiety-appropriate social events from Meetup, Eventbrite, and TAMU.
    Considers event size, activity structure, proximity, and interest alignment
    to generate personalized recommendations.
    """
