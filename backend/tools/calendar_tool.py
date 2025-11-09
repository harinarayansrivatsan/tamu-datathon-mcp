"""
Google Calendar Tool for detecting social event patterns.

This tool fetches calendar events and analyzes social event frequency
to detect changes in social behavior.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from backend.core import get_settings

settings = get_settings()


class CalendarTool:
    """
    Google Calendar integration for social event tracking.

    Analyzes:
    - Social event frequency (events with multiple attendees)
    - Event type patterns (social vs. work vs. personal)
    - Decline in social commitments over time
    """

    def __init__(self, access_token: str):
        """
        Initialize Calendar Tool with user's OAuth token.

        Args:
            access_token: Google OAuth access token
        """
        self.credentials = Credentials(token=access_token)
        self.service = build("calendar", "v3", credentials=self.credentials)

    async def get_social_events(
        self, days_back: int = 30, min_attendees: int = 2
    ) -> List[Dict[str, Any]]:
        """
        Fetch social events from user's calendar.

        Args:
            days_back: Number of days to look back
            min_attendees: Minimum number of attendees to classify as "social"

        Returns:
            List of social event dictionaries
        """
        try:
            now = datetime.utcnow()
            time_min = (now - timedelta(days=days_back)).isoformat() + "Z"
            time_max = now.isoformat() + "Z"

            events_result = (
                self.service.events()
                .list(
                    calendarId="primary",
                    timeMin=time_min,
                    timeMax=time_max,
                    maxResults=100,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )

            events = events_result.get("items", [])
            social_events = []

            for event in events:
                attendees = event.get("attendees", [])
                if len(attendees) >= min_attendees:
                    social_events.append(
                        {
                            "id": event.get("id"),
                            "summary": event.get("summary", "Untitled Event"),
                            "start": event.get("start", {}).get("dateTime"),
                            "end": event.get("end", {}).get("dateTime"),
                            "attendees_count": len(attendees),
                            "description": event.get("description", ""),
                        }
                    )

            return social_events

        except HttpError as error:
            print(f"An error occurred: {error}")
            return []

    async def calculate_social_frequency(self, days_back: int = 30) -> float:
        """
        Calculate social event frequency (events per week).

        Args:
            days_back: Number of days to analyze

        Returns:
            Average social events per week
        """
        social_events = await self.get_social_events(days_back)
        weeks = days_back / 7
        return len(social_events) / weeks if weeks > 0 else 0.0

    async def detect_social_decline(
        self, baseline_frequency: float, current_period_days: int = 14
    ) -> Dict[str, Any]:
        """
        Detect decline in social event frequency compared to baseline.

        Args:
            baseline_frequency: User's baseline social event frequency (events/week)
            current_period_days: Number of recent days to compare

        Returns:
            Dictionary with decline analysis
        """
        current_frequency = await self.calculate_social_frequency(current_period_days)
        decline_percentage = (
            ((baseline_frequency - current_frequency) / baseline_frequency * 100)
            if baseline_frequency > 0
            else 0
        )

        return {
            "baseline_frequency": baseline_frequency,
            "current_frequency": current_frequency,
            "decline_percentage": decline_percentage,
            "is_declining": decline_percentage > 25,  # >25% decline is concerning
            "period_days": current_period_days,
        }

    async def get_upcoming_social_events(self, days_ahead: int = 7) -> List[Dict[str, Any]]:
        """
        Get upcoming social events to assess future social commitments.

        Args:
            days_ahead: Number of days to look ahead

        Returns:
            List of upcoming social events
        """
        try:
            now = datetime.utcnow()
            time_min = now.isoformat() + "Z"
            time_max = (now + timedelta(days=days_ahead)).isoformat() + "Z"

            events_result = (
                self.service.events()
                .list(
                    calendarId="primary",
                    timeMin=time_min,
                    timeMax=time_max,
                    maxResults=50,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )

            events = events_result.get("items", [])
            social_events = []

            for event in events:
                attendees = event.get("attendees", [])
                if len(attendees) >= 2:
                    social_events.append(
                        {
                            "summary": event.get("summary", "Untitled Event"),
                            "start": event.get("start", {}).get("dateTime"),
                            "attendees_count": len(attendees),
                        }
                    )

            return social_events

        except HttpError as error:
            print(f"An error occurred: {error}")
            return []

    async def get_declined_invitations(self, days_back: int = 30) -> Dict[str, Any]:
        """
        Track declined invitation patterns (increased declines may indicate withdrawal).

        Args:
            days_back: Number of days to analyze

        Returns:
            Dictionary with declined invitation analysis
        """
        try:
            now = datetime.utcnow()
            time_min = (now - timedelta(days=days_back)).isoformat() + "Z"
            time_max = now.isoformat() + "Z"

            events_result = (
                self.service.events()
                .list(
                    calendarId="primary",
                    timeMin=time_min,
                    timeMax=time_max,
                    maxResults=100,
                    singleEvents=True,
                )
                .execute()
            )

            events = events_result.get("items", [])

            total_invitations = 0
            declined_count = 0
            declined_events = []

            for event in events:
                attendees = event.get("attendees", [])

                # Find user's response status
                for attendee in attendees:
                    if attendee.get("self", False):  # This is the user
                        total_invitations += 1
                        response_status = attendee.get("responseStatus")

                        if response_status == "declined":
                            declined_count += 1
                            declined_events.append(
                                {
                                    "summary": event.get("summary", "Untitled Event"),
                                    "start": event.get("start", {}).get("dateTime"),
                                    "attendees_count": len(attendees),
                                }
                            )

            decline_rate = (
                (declined_count / total_invitations * 100) if total_invitations > 0 else 0
            )

            return {
                "total_invitations": total_invitations,
                "declined_count": declined_count,
                "decline_rate": round(decline_rate, 2),
                "is_concerning": decline_rate > 40,  # >40% decline rate is concerning
                "declined_events": declined_events[:5],  # Return last 5 declined events
            }

        except HttpError as error:
            print(f"An error occurred: {error}")
            return {"total_invitations": 0, "declined_count": 0, "decline_rate": 0}

    async def identify_recurring_contacts(self, days_back: int = 60) -> Dict[str, Any]:
        """
        Build friend graph from calendar data (identify frequent social contacts).

        Args:
            days_back: Number of days to analyze

        Returns:
            Dictionary with friend graph analysis
        """
        try:
            now = datetime.utcnow()
            time_min = (now - timedelta(days=days_back)).isoformat() + "Z"
            time_max = now.isoformat() + "Z"

            events_result = (
                self.service.events()
                .list(
                    calendarId="primary",
                    timeMin=time_min,
                    timeMax=time_max,
                    maxResults=200,
                    singleEvents=True,
                )
                .execute()
            )

            events = events_result.get("items", [])

            contact_frequency = {}

            for event in events:
                attendees = event.get("attendees", [])

                # Only count events with 2+ attendees (social events)
                if len(attendees) >= 2:
                    for attendee in attendees:
                        if not attendee.get("self", False):  # Exclude the user themselves
                            email = attendee.get("email")
                            name = attendee.get("displayName", email)

                            if email:
                                if email not in contact_frequency:
                                    contact_frequency[email] = {
                                        "name": name,
                                        "count": 0,
                                        "email": email,
                                    }
                                contact_frequency[email]["count"] += 1

            # Sort by frequency and get top 10
            top_contacts = sorted(
                contact_frequency.values(), key=lambda x: x["count"], reverse=True
            )[:10]

            return {
                "total_unique_contacts": len(contact_frequency),
                "top_contacts": top_contacts,
                "has_frequent_contacts": len(top_contacts) > 0 and top_contacts[0]["count"] >= 3,
            }

        except HttpError as error:
            print(f"An error occurred: {error}")
            return {"total_unique_contacts": 0, "top_contacts": []}

    async def filter_social_events(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter out noise events (work meetings, all-day events, single-person events).

        Args:
            events: Raw event list from calendar

        Returns:
            Filtered list of genuine social events
        """
        social_events = []

        for event in events:
            summary = event.get("summary", "").lower()
            attendees = event.get("attendees", [])
            start = event.get("start", {})
            recurrence = event.get("recurrence", [])

            # Skip if no attendees or only 1 person
            if len(attendees) < 2:
                continue

            # Skip all-day events (likely not social)
            if "date" in start and "dateTime" not in start:
                continue

            # Skip recurring work meetings (daily/weekly pattern)
            if recurrence:
                recurrence_str = str(recurrence).lower()
                if "freq=daily" in recurrence_str or "freq=weekly" in recurrence_str:
                    # Additional check: if it's a work-related term, skip
                    work_terms = ["standup", "sync", "meeting", "status", "review", "scrum"]
                    if any(term in summary for term in work_terms):
                        continue

            # Skip events with work-related keywords
            work_keywords = ["standup", "1:1", "sync", "status", "review", "interview"]
            if any(keyword in summary for keyword in work_keywords):
                continue

            # This is likely a genuine social event
            social_events.append(event)

        return social_events

    async def analyze_social_patterns(self, days_back: int = 30) -> Dict[str, Any]:
        """
        Comprehensive social pattern analysis combining all Phase 1.2 enhancements.

        Args:
            days_back: Number of days to analyze

        Returns:
            Dictionary with comprehensive social analysis
        """
        # Get all events
        try:
            now = datetime.utcnow()
            time_min = (now - timedelta(days=days_back)).isoformat() + "Z"
            time_max = now.isoformat() + "Z"

            events_result = (
                self.service.events()
                .list(
                    calendarId="primary",
                    timeMin=time_min,
                    timeMax=time_max,
                    maxResults=200,
                    singleEvents=True,
                )
                .execute()
            )

            all_events = events_result.get("items", [])

            # Filter to genuine social events
            social_events = await self.filter_social_events(all_events)

            # Get declined invitations
            declined_analysis = await self.get_declined_invitations(days_back)

            # Get friend graph
            friend_graph = await self.identify_recurring_contacts(days_back)

            # Calculate social frequency from filtered events
            weeks = days_back / 7
            social_frequency = len(social_events) / weeks if weeks > 0 else 0

            return {
                "total_events": len(all_events),
                "social_events": len(social_events),
                "social_frequency": round(social_frequency, 2),
                "declined_analysis": declined_analysis,
                "friend_graph": friend_graph,
                "period_days": days_back,
            }

        except HttpError as error:
            print(f"An error occurred: {error}")
            return {}


def get_calendar_tool_description() -> str:
    """Get tool description for MCP registration."""
    return """
    Analyzes Google Calendar to detect social isolation patterns.
    Tracks social event frequency, identifies declining social commitments,
    and helps establish behavioral baselines.
    """
