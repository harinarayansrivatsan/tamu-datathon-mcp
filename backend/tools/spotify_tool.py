"""
Spotify Tool for mood detection via music listening patterns.

This tool analyzes Spotify listening history to detect mood shifts
and emotional patterns that may indicate loneliness or depression.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from backend.core import get_settings

settings = get_settings()


class SpotifyTool:
    """
    Spotify integration for mood detection through music analysis.

    Analyzes:
    - Audio features (valence, energy, tempo)
    - Genre patterns
    - Listening time patterns (late-night listening)
    - Changes in music taste (shift to sad/melancholic music)
    """

    def __init__(self, access_token: str):
        """
        Initialize Spotify Tool with user's OAuth token.

        Args:
            access_token: Spotify OAuth access token
        """
        self.sp = spotipy.Spotify(auth=access_token)

    async def get_recent_tracks(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch recently played tracks.

        Args:
            limit: Number of recent tracks to fetch (max 50)

        Returns:
            List of recently played tracks with metadata
        """
        try:
            results = self.sp.current_user_recently_played(limit=limit)
            tracks = []

            for item in results.get("items", []):
                track = item.get("track", {})
                played_at = item.get("played_at")

                tracks.append(
                    {
                        "track_id": track.get("id"),
                        "name": track.get("name"),
                        "artist": track.get("artists", [{}])[0].get("name"),
                        "played_at": played_at,
                        "duration_ms": track.get("duration_ms"),
                    }
                )

            return tracks

        except Exception as error:
            print(f"Spotify API error: {error}")
            return []

    async def get_audio_features(self, track_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Get audio features for a list of tracks.

        Args:
            track_ids: List of Spotify track IDs

        Returns:
            List of audio feature dictionaries
        """
        try:
            # Spotify API limits to 100 tracks per request
            features = []
            for i in range(0, len(track_ids), 100):
                batch = track_ids[i : i + 100]
                batch_features = self.sp.audio_features(batch)
                features.extend([f for f in batch_features if f is not None])

            return features

        except Exception as error:
            print(f"Spotify API error: {error}")
            return []

    async def calculate_mood_metrics(self, days_back: int = 14) -> Dict[str, float]:
        """
        Calculate average mood metrics from recent listening history.

        Args:
            days_back: Number of days to analyze

        Returns:
            Dictionary with mood metrics (valence, energy, danceability, etc.)
        """
        tracks = await self.get_recent_tracks(limit=50)

        # Filter tracks within time window
        cutoff = datetime.utcnow() - timedelta(days=days_back)
        recent_tracks = [
            t
            for t in tracks
            if datetime.fromisoformat(t["played_at"].replace("Z", "+00:00")) > cutoff
        ]

        if not recent_tracks:
            return {}

        track_ids = [t["track_id"] for t in recent_tracks if t["track_id"]]
        audio_features = await self.get_audio_features(track_ids)

        if not audio_features:
            return {}

        # Calculate averages
        metrics = {
            "valence": 0.0,  # Musical positiveness (0.0 = sad, 1.0 = happy)
            "energy": 0.0,  # Intensity/activity (0.0 = calm, 1.0 = energetic)
            "danceability": 0.0,
            "tempo": 0.0,
            "acousticness": 0.0,
        }

        for feature in audio_features:
            for key in metrics.keys():
                metrics[key] += feature.get(key, 0.0)

        # Average out
        count = len(audio_features)
        for key in metrics:
            metrics[key] = round(metrics[key] / count, 3) if count > 0 else 0.0

        metrics["track_count"] = count

        return metrics

    async def detect_mood_shift(
        self, baseline_metrics: Dict[str, float], current_period_days: int = 7
    ) -> Dict[str, Any]:
        """
        Detect significant mood shifts compared to baseline.

        Args:
            baseline_metrics: User's baseline mood metrics
            current_period_days: Number of recent days to compare

        Returns:
            Dictionary with mood shift analysis
        """
        current_metrics = await self.calculate_mood_metrics(current_period_days)

        if not current_metrics or not baseline_metrics:
            return {"shift_detected": False, "reason": "Insufficient data"}

        # Calculate changes
        valence_change = baseline_metrics.get("valence", 0.5) - current_metrics.get("valence", 0.5)
        energy_change = baseline_metrics.get("energy", 0.5) - current_metrics.get("energy", 0.5)

        # Significant shift = >20% decrease in valence or energy
        significant_valence_drop = valence_change > 0.2
        significant_energy_drop = energy_change > 0.2

        return {
            "shift_detected": significant_valence_drop or significant_energy_drop,
            "baseline_valence": baseline_metrics.get("valence", 0.0),
            "current_valence": current_metrics.get("valence", 0.0),
            "valence_change": round(valence_change, 3),
            "baseline_energy": baseline_metrics.get("energy", 0.0),
            "current_energy": current_metrics.get("energy", 0.0),
            "energy_change": round(energy_change, 3),
            "is_concerning": significant_valence_drop and significant_energy_drop,
        }

    async def detect_late_night_listening(self, days_back: int = 7) -> Dict[str, Any]:
        """
        Detect late-night listening patterns (potential sleep issues/isolation).

        Args:
            days_back: Number of days to analyze

        Returns:
            Dictionary with late-night listening analysis
        """
        tracks = await self.get_recent_tracks(limit=50)

        late_night_count = 0
        total_count = len(tracks)

        for track in tracks:
            played_at = datetime.fromisoformat(track["played_at"].replace("Z", "+00:00"))
            hour = played_at.hour

            # Consider 11 PM - 4 AM as "late night"
            if hour >= 23 or hour < 4:
                late_night_count += 1

        late_night_percentage = (late_night_count / total_count * 100) if total_count > 0 else 0

        return {
            "late_night_count": late_night_count,
            "total_count": total_count,
            "late_night_percentage": round(late_night_percentage, 2),
            "is_concerning": late_night_percentage > 40,  # >40% is concerning
        }

    async def detect_repeat_listening(self, days_back: int = 7) -> Dict[str, Any]:
        """
        Detect repeat listening patterns (may indicate rumination/obsessive behavior).

        Args:
            days_back: Number of days to analyze

        Returns:
            Dictionary with repeat listening analysis
        """
        tracks = await self.get_recent_tracks(limit=50)

        # Filter tracks within time window
        cutoff = datetime.utcnow() - timedelta(days=days_back)
        recent_tracks = [
            t
            for t in tracks
            if datetime.fromisoformat(t["played_at"].replace("Z", "+00:00")) > cutoff
        ]

        if not recent_tracks:
            return {"repeat_percentage": 0, "most_repeated": None}

        # Count track frequencies
        track_counts = {}
        for track in recent_tracks:
            track_id = track.get("track_id")
            if track_id:
                if track_id not in track_counts:
                    track_counts[track_id] = {
                        "count": 0,
                        "name": track.get("name"),
                        "artist": track.get("artist"),
                    }
                track_counts[track_id]["count"] += 1

        # Find most repeated track
        most_repeated = (
            max(track_counts.values(), key=lambda x: x["count"]) if track_counts else None
        )

        # Calculate repeat percentage
        total_plays = len(recent_tracks)
        unique_tracks = len(track_counts)
        repeat_percentage = (
            ((total_plays - unique_tracks) / total_plays * 100) if total_plays > 0 else 0
        )

        return {
            "total_plays": total_plays,
            "unique_tracks": unique_tracks,
            "repeat_percentage": round(repeat_percentage, 2),
            "most_repeated": most_repeated,
            "is_concerning": repeat_percentage > 30,  # >30% repeats is concerning
        }

    async def calculate_genre_diversity(self, days_back: int = 14) -> Dict[str, Any]:
        """
        Calculate genre/artist diversity (declining diversity may indicate withdrawal).

        Args:
            days_back: Number of days to analyze

        Returns:
            Dictionary with diversity metrics
        """
        tracks = await self.get_recent_tracks(limit=50)

        # Filter tracks within time window
        cutoff = datetime.utcnow() - timedelta(days=days_back)
        recent_tracks = [
            t
            for t in tracks
            if datetime.fromisoformat(t["played_at"].replace("Z", "+00:00")) > cutoff
        ]

        if not recent_tracks:
            return {"diversity_score": 0}

        # Count unique artists
        artists = set()
        for track in recent_tracks:
            artist = track.get("artist")
            if artist:
                artists.add(artist)

        # Diversity score = unique artists / total tracks
        diversity_score = len(artists) / len(recent_tracks) if recent_tracks else 0

        return {
            "total_tracks": len(recent_tracks),
            "unique_artists": len(artists),
            "diversity_score": round(diversity_score, 3),
            "is_diverse": diversity_score > 0.5,  # >50% unique is diverse
        }

    async def calculate_enhanced_mood_metrics(self, days_back: int = 14) -> Dict[str, Any]:
        """
        Calculate comprehensive mood metrics including enhancements from Phase 1.1.

        Args:
            days_back: Number of days to analyze

        Returns:
            Dictionary with enhanced mood metrics
        """
        # Get base metrics
        base_metrics = await self.calculate_mood_metrics(days_back)

        # Get enhanced metrics
        repeat_analysis = await self.detect_repeat_listening(days_back)
        diversity_analysis = await self.calculate_genre_diversity(days_back)
        late_night_analysis = await self.detect_late_night_listening(days_back)

        # Combine all metrics
        return {
            **base_metrics,
            "repeat_listening": repeat_analysis,
            "genre_diversity": diversity_analysis,
            "late_night_listening": late_night_analysis,
        }


def get_spotify_tool_description() -> str:
    """Get tool description for MCP registration."""
    return """
    Analyzes Spotify listening history to detect mood shifts and emotional patterns.
    Tracks musical positivity (valence), energy levels, and late-night listening habits
    that may indicate loneliness or depression.
    """
