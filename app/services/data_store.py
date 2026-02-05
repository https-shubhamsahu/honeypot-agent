"""
Data store for tracking honeypot sessions and intelligence.
Uses in-memory storage with thread-safe operations.
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
from threading import Lock
import uuid

class SessionData:
    """Represents a single honeypot session"""
    def __init__(self, session_id: str, channel: str = "Unknown"):
        self.session_id = session_id
        self.channel = channel
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.message_count = 0
        self.scam_detected = False
        self.status = "active"  # active, completed, reported
        self.intelligence = {
            "bankAccounts": [],
            "upiIds": [],
            "phishingLinks": [],
            "phoneNumbers": [],
            "suspiciousKeywords": []
        }
        self.agent_notes = ""
        self.conversation_preview = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "sessionId": self.session_id,
            "channel": self.channel,
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat(),
            "messageCount": self.message_count,
            "scamDetected": self.scam_detected,
            "status": self.status,
            "intelligence": self.intelligence,
            "agentNotes": self.agent_notes,
            "conversationPreview": self.conversation_preview
        }


class ActivityEvent:
    """Represents an activity event for the feed"""
    def __init__(self, event_type: str, title: str, description: str, channel: str = ""):
        self.id = str(uuid.uuid4())[:8]
        self.type = event_type  # scam, intel, engaged, reported
        self.title = title
        self.description = description
        self.channel = channel
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        # Calculate relative time
        delta = datetime.now() - self.timestamp
        if delta.seconds < 60:
            time_str = "Just now"
        elif delta.seconds < 3600:
            time_str = f"{delta.seconds // 60} min ago"
        elif delta.seconds < 86400:
            time_str = f"{delta.seconds // 3600} hours ago"
        else:
            time_str = f"{delta.days} days ago"
        
        return {
            "id": self.id,
            "type": self.type,
            "title": self.title,
            "description": self.description,
            "channel": self.channel,
            "time": time_str,
            "timestamp": self.timestamp.isoformat()
        }


class HoneypotDataStore:
    """Thread-safe data store for honeypot operations"""
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._sessions: Dict[str, SessionData] = {}
        self._activities: List[ActivityEvent] = []
        self._data_lock = Lock()
        self._initialized = True
        
        # Aggregate counters
        self._total_scams = 0
        self._total_intel = 0
        self._total_engagement_time = 0  # in seconds
    
    def get_or_create_session(self, session_id: str, channel: str = "Unknown") -> SessionData:
        """Get existing session or create new one"""
        with self._data_lock:
            if session_id not in self._sessions:
                self._sessions[session_id] = SessionData(session_id, channel)
                self._add_activity_unlocked(
                    "engaged",
                    "New Session Started",
                    f"Honeypot engaged with potential scammer",
                    channel
                )
            return self._sessions[session_id]
    
    def update_session(self, session_id: str, 
                       scam_detected: bool = None,
                       message_count: int = None,
                       intelligence: Dict = None,
                       status: str = None,
                       agent_notes: str = None,
                       conversation_preview: str = None) -> Optional[SessionData]:
        """Update session data"""
        with self._data_lock:
            if session_id not in self._sessions:
                return None
            
            session = self._sessions[session_id]
            session.updated_at = datetime.now()
            
            if scam_detected is not None and scam_detected and not session.scam_detected:
                session.scam_detected = True
                self._total_scams += 1
                self._add_activity_unlocked(
                    "scam",
                    "Scam Detected",
                    f"Fraudulent intent confirmed in session",
                    session.channel
                )
            
            if message_count is not None:
                session.message_count = message_count
            
            if intelligence is not None:
                # Merge intelligence
                for key, values in intelligence.items():
                    if key in session.intelligence and isinstance(values, list):
                        # Add new unique values
                        existing = set(session.intelligence[key])
                        new_items = [v for v in values if v not in existing]
                        if new_items:
                            session.intelligence[key].extend(new_items)
                            self._total_intel += len(new_items)
                            self._add_activity_unlocked(
                                "intel",
                                "Intelligence Extracted",
                                f"Captured {len(new_items)} new {key} from conversation",
                                session.channel
                            )
            
            if status is not None:
                old_status = session.status
                session.status = status
                if status == "reported" and old_status != "reported":
                    self._add_activity_unlocked(
                        "reported",
                        "Session Reported",
                        f"Intelligence sent to evaluation endpoint",
                        session.channel
                    )
            
            if agent_notes is not None:
                session.agent_notes = agent_notes
            
            if conversation_preview is not None:
                session.conversation_preview = conversation_preview
            
            return session
    
    def _add_activity_unlocked(self, event_type: str, title: str, description: str, channel: str):
        """Add activity event (must be called with lock held)"""
        event = ActivityEvent(event_type, title, description, channel)
        self._activities.insert(0, event)
        # Keep only last 100 activities
        if len(self._activities) > 100:
            self._activities = self._activities[:100]
    
    def add_activity(self, event_type: str, title: str, description: str, channel: str = ""):
        """Add activity event (thread-safe)"""
        with self._data_lock:
            self._add_activity_unlocked(event_type, title, description, channel)
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get aggregated stats for dashboard"""
        with self._data_lock:
            total_sessions = len(self._sessions)
            active_sessions = sum(1 for s in self._sessions.values() if s.status == "active")
            
            # Calculate average engagement (messages per session as proxy)
            avg_messages = 0
            if total_sessions > 0:
                avg_messages = sum(s.message_count for s in self._sessions.values()) / total_sessions
            
            # Calculate threat level (0-100)
            threat_level = min(100, (self._total_scams * 10) + (active_sessions * 5))
            
            return {
                "totalSessions": total_sessions,
                "activeSessions": active_sessions,
                "scamsDetected": self._total_scams,
                "avgEngagement": round(avg_messages, 1),
                "intelExtracted": self._total_intel,
                "threatLevel": threat_level
            }
    
    def get_recent_activities(self, limit: int = 10) -> List[Dict]:
        """Get recent activity events"""
        with self._data_lock:
            return [a.to_dict() for a in self._activities[:limit]]
    
    def get_recent_sessions(self, limit: int = 10) -> List[Dict]:
        """Get recent sessions"""
        with self._data_lock:
            sessions = sorted(
                self._sessions.values(),
                key=lambda s: s.updated_at,
                reverse=True
            )[:limit]
            return [s.to_dict() for s in sessions]
    
    def get_intelligence_summary(self) -> Dict[str, int]:
        """Get aggregated intelligence counts"""
        with self._data_lock:
            summary = {
                "phoneNumbers": 0,
                "upiIds": 0,
                "phishingLinks": 0,
                "bankAccounts": 0,
                "suspiciousKeywords": 0
            }
            for session in self._sessions.values():
                for key in summary:
                    if key in session.intelligence:
                        summary[key] += len(session.intelligence[key])
            return summary


# Global singleton instance
data_store = HoneypotDataStore()
