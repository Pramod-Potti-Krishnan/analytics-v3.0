"""
Session Manager for Analytics Microservice v3

Tracks presentation context for narrative flow and consistency.
Stores prior slides to help generate contextually-aware observations.

Simple in-memory storage with TTL-based cleanup.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class SessionManager:
    """
    Manages presentation sessions for context retention.

    Stores presentation metadata and prior slides to maintain
    narrative flow across multiple analytics generations.
    """

    def __init__(self, ttl_hours: int = 1):
        """
        Initialize session manager.

        Args:
            ttl_hours: Time-to-live for sessions in hours (default: 1)
        """
        self.sessions: Dict[str, Dict] = {}
        self.ttl_hours = ttl_hours
        logger.info(f"SessionManager initialized with {ttl_hours}h TTL")

    def _is_expired(self, session_data: Dict) -> bool:
        """Check if session has expired based on TTL."""
        created_at = session_data.get("created_at")
        if not created_at:
            return True

        expiry_time = created_at + timedelta(hours=self.ttl_hours)
        return datetime.now() > expiry_time

    def _cleanup_expired(self):
        """Remove expired sessions."""
        expired_ids = [
            pid for pid, data in self.sessions.items()
            if self._is_expired(data)
        ]

        for pid in expired_ids:
            logger.info(f"Cleaning up expired session: {pid}")
            del self.sessions[pid]

        if expired_ids:
            logger.info(f"Cleaned up {len(expired_ids)} expired sessions")

    def create_session(
        self,
        presentation_id: str,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Create new presentation session.

        Args:
            presentation_id: Unique presentation identifier
            metadata: Optional presentation metadata (theme, audience, etc.)

        Returns:
            Created session data
        """
        logger.info(f"Creating session for presentation: {presentation_id}")

        session_data = {
            "presentation_id": presentation_id,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "slides": [],
            "metadata": metadata or {},
            "themes_used": set(),
            "analytics_types_used": set()
        }

        self.sessions[presentation_id] = session_data
        self._cleanup_expired()

        return session_data

    def update_context(
        self,
        presentation_id: str,
        slide_data: Dict
    ):
        """
        Add slide data to session context.

        Args:
            presentation_id: Presentation identifier
            slide_data: Slide information (slide_number, analytics_type, data, etc.)
        """
        # Create session if it doesn't exist
        if presentation_id not in self.sessions:
            self.create_session(presentation_id)

        session = self.sessions[presentation_id]

        # Add slide to history
        slide_summary = {
            "slide_number": slide_data.get("slide_number"),
            "slide_id": slide_data.get("slide_id"),
            "analytics_type": slide_data.get("analytics_type"),
            "narrative": slide_data.get("narrative", ""),
            "data_points": len(slide_data.get("data", [])),
            "timestamp": datetime.now().isoformat()
        }

        session["slides"].append(slide_summary)
        session["updated_at"] = datetime.now()

        # Track themes and analytics types used
        if "theme" in slide_data:
            session["themes_used"].add(slide_data["theme"])
        if "analytics_type" in slide_data:
            session["analytics_types_used"].add(slide_data["analytics_type"])

        logger.info(
            f"Updated session {presentation_id}: "
            f"{len(session['slides'])} slides, "
            f"latest: {slide_summary['analytics_type']}"
        )

    def get_context(self, presentation_id: str) -> Dict:
        """
        Get full presentation context.

        Args:
            presentation_id: Presentation identifier

        Returns:
            Session data dictionary or empty dict if not found
        """
        session = self.sessions.get(presentation_id, {})

        if session:
            logger.debug(
                f"Retrieved context for {presentation_id}: "
                f"{len(session.get('slides', []))} slides"
            )
        else:
            logger.warning(f"No session found for {presentation_id}")

        return session

    def get_prior_slides(
        self,
        presentation_id: str,
        limit: int = 3
    ) -> List[Dict]:
        """
        Get last N slides for narrative flow.

        Args:
            presentation_id: Presentation identifier
            limit: Maximum number of prior slides to return

        Returns:
            List of slide summaries (most recent first)
        """
        session = self.get_context(presentation_id)
        slides = session.get("slides", [])

        # Return last N slides in reverse order (most recent first)
        prior_slides = slides[-limit:] if slides else []
        prior_slides.reverse()

        logger.debug(
            f"Retrieved {len(prior_slides)} prior slides for {presentation_id}"
        )

        return prior_slides

    def get_session_summary(self, presentation_id: str) -> str:
        """
        Get human-readable session summary.

        Args:
            presentation_id: Presentation identifier

        Returns:
            Summary string
        """
        session = self.get_context(presentation_id)

        if not session:
            return f"No session found for {presentation_id}"

        slides_count = len(session.get("slides", []))
        themes = ", ".join(session.get("themes_used", set()))
        analytics_types = ", ".join(session.get("analytics_types_used", set()))
        created = session.get("created_at", "Unknown")

        return (
            f"Session {presentation_id}:\n"
            f"  Slides: {slides_count}\n"
            f"  Themes: {themes or 'None'}\n"
            f"  Analytics: {analytics_types or 'None'}\n"
            f"  Created: {created}"
        )

    def clear_session(self, presentation_id: str):
        """
        Clear specific presentation session.

        Args:
            presentation_id: Presentation identifier
        """
        if presentation_id in self.sessions:
            logger.info(f"Clearing session: {presentation_id}")
            del self.sessions[presentation_id]
        else:
            logger.warning(f"Session not found: {presentation_id}")

    def clear_all_sessions(self):
        """Clear all sessions (useful for testing/cleanup)."""
        count = len(self.sessions)
        self.sessions.clear()
        logger.info(f"Cleared all sessions ({count} total)")

    def get_active_sessions_count(self) -> int:
        """Get count of active (non-expired) sessions."""
        self._cleanup_expired()
        return len(self.sessions)


# Global session manager instance
_session_manager = None


def get_session_manager() -> SessionManager:
    """
    Get global session manager instance (singleton pattern).

    Returns:
        SessionManager instance
    """
    global _session_manager

    if _session_manager is None:
        _session_manager = SessionManager(ttl_hours=1)
        logger.info("Global SessionManager created")

    return _session_manager
