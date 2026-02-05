"""
Enhanced logging system for tracking AI reasoning and actions.
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
from threading import Lock
from enum import Enum
import uuid


class ActionType(Enum):
    SESSION_START = "session_start"
    SCAM_DETECTION = "scam_detection"
    AGENT_RESPONSE = "agent_response"
    INTEL_EXTRACTION = "intel_extraction"
    REPORT_SENT = "report_sent"
    MESSAGE_RECEIVED = "message_received"
    ERROR = "error"


class ActionLog:
    """Represents a single action/reasoning log entry"""
    def __init__(
        self,
        session_id: str,
        action_type: ActionType,
        title: str,
        details: str,
        reasoning: str = "",
        input_data: Any = None,
        output_data: Any = None,
        duration_ms: int = 0,
        success: bool = True
    ):
        self.id = str(uuid.uuid4())[:12]
        self.session_id = session_id
        self.action_type = action_type
        self.title = title
        self.details = details
        self.reasoning = reasoning
        self.input_data = input_data
        self.output_data = output_data
        self.duration_ms = duration_ms
        self.success = success
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "sessionId": self.session_id,
            "actionType": self.action_type.value,
            "title": self.title,
            "details": self.details,
            "reasoning": self.reasoning,
            "inputData": self.input_data,
            "outputData": self.output_data,
            "durationMs": self.duration_ms,
            "success": self.success,
            "timestamp": self.timestamp.isoformat(),
            "timeAgo": self._get_time_ago()
        }
    
    def _get_time_ago(self) -> str:
        delta = datetime.now() - self.timestamp
        if delta.seconds < 5:
            return "Just now"
        elif delta.seconds < 60:
            return f"{delta.seconds}s ago"
        elif delta.seconds < 3600:
            return f"{delta.seconds // 60}m ago"
        else:
            return f"{delta.seconds // 3600}h ago"


class ConversationMessage:
    """Represents a message in a conversation"""
    def __init__(self, sender: str, text: str, timestamp: datetime = None):
        self.sender = sender
        self.text = text
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "sender": self.sender,
            "text": self.text,
            "timestamp": self.timestamp.isoformat()
        }


class SessionDetail:
    """Detailed session tracking for admin view"""
    def __init__(self, session_id: str, channel: str = "Unknown"):
        self.session_id = session_id
        self.channel = channel
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.status = "active"
        self.scam_detected = False
        self.scam_confidence = 0.0
        self.scam_reasoning = ""
        self.messages: List[ConversationMessage] = []
        self.action_logs: List[ActionLog] = []
        self.intelligence = {
            "bankAccounts": [],
            "upiIds": [],
            "phishingLinks": [],
            "phoneNumbers": [],
            "suspiciousKeywords": []
        }
        self.agent_persona = "Grandma Betty"
        self.total_engagement_time = 0
        self.report_attempts = 0
        self.last_agent_reply = ""
    
    def add_message(self, sender: str, text: str):
        self.messages.append(ConversationMessage(sender, text))
        self.updated_at = datetime.now()
    
    def add_action_log(self, log: ActionLog):
        self.action_logs.append(log)
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "sessionId": self.session_id,
            "channel": self.channel,
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat(),
            "status": self.status,
            "scamDetected": self.scam_detected,
            "scamConfidence": self.scam_confidence,
            "scamReasoning": self.scam_reasoning,
            "messageCount": len(self.messages),
            "messages": [m.to_dict() for m in self.messages],
            "actionLogs": [a.to_dict() for a in self.action_logs],
            "intelligence": self.intelligence,
            "agentPersona": self.agent_persona,
            "totalEngagementTime": self.total_engagement_time,
            "reportAttempts": self.report_attempts,
            "lastAgentReply": self.last_agent_reply
        }
    
    def to_summary(self) -> Dict[str, Any]:
        return {
            "sessionId": self.session_id,
            "channel": self.channel,
            "status": self.status,
            "scamDetected": self.scam_detected,
            "messageCount": len(self.messages),
            "actionCount": len(self.action_logs),
            "updatedAt": self.updated_at.isoformat(),
            "lastMessage": self.messages[-1].text[:50] + "..." if self.messages else ""
        }


class AdminLogger:
    """Singleton logger for admin panel"""
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
        
        self._sessions: Dict[str, SessionDetail] = {}
        self._global_logs: List[ActionLog] = []
        self._data_lock = Lock()
        self._initialized = True
    
    def get_or_create_session(self, session_id: str, channel: str = "Unknown") -> SessionDetail:
        with self._data_lock:
            if session_id not in self._sessions:
                self._sessions[session_id] = SessionDetail(session_id, channel)
                self._log_action(
                    session_id,
                    ActionType.SESSION_START,
                    "New Session Started",
                    f"Honeypot session initiated from {channel}",
                    reasoning="New conversation detected, initializing session tracking"
                )
            return self._sessions[session_id]
    
    def log_message_received(self, session_id: str, sender: str, text: str):
        with self._data_lock:
            if session_id in self._sessions:
                session = self._sessions[session_id]
                session.add_message(sender, text)
                self._log_action(
                    session_id,
                    ActionType.MESSAGE_RECEIVED,
                    f"Message from {sender.upper()}",
                    text[:100] + ("..." if len(text) > 100 else ""),
                    input_data={"sender": sender, "text": text}
                )
    
    def log_scam_detection(
        self,
        session_id: str,
        is_scam: bool,
        confidence: float = 0.0,
        reasoning: str = "",
        raw_response: str = ""
    ):
        with self._data_lock:
            if session_id in self._sessions:
                session = self._sessions[session_id]
                session.scam_detected = is_scam
                session.scam_confidence = confidence
                session.scam_reasoning = reasoning
                
                self._log_action(
                    session_id,
                    ActionType.SCAM_DETECTION,
                    f"Scam Detection: {'POSITIVE' if is_scam else 'NEGATIVE'}",
                    reasoning or ("Scam intent detected" if is_scam else "No scam detected"),
                    reasoning=f"LLM Analysis: {raw_response[:200]}..." if raw_response else reasoning,
                    output_data={"isScam": is_scam, "confidence": confidence},
                    success=True
                )
    
    def log_agent_response(
        self,
        session_id: str,
        reply: str,
        persona: str = "Grandma Betty",
        reasoning: str = "",
        duration_ms: int = 0
    ):
        with self._data_lock:
            if session_id in self._sessions:
                session = self._sessions[session_id]
                session.last_agent_reply = reply
                session.add_message("agent", reply)
                
                self._log_action(
                    session_id,
                    ActionType.AGENT_RESPONSE,
                    f"Agent Response ({persona})",
                    reply[:100] + ("..." if len(reply) > 100 else ""),
                    reasoning=reasoning or f"Generated response as {persona} to engage scammer",
                    output_data={"reply": reply, "persona": persona},
                    duration_ms=duration_ms
                )
    
    def log_intel_extraction(
        self,
        session_id: str,
        intelligence: Dict[str, List],
        reasoning: str = "",
        duration_ms: int = 0
    ):
        with self._data_lock:
            if session_id in self._sessions:
                session = self._sessions[session_id]
                
                # Merge intelligence
                for key, values in intelligence.items():
                    if key in session.intelligence and isinstance(values, list):
                        existing = set(session.intelligence[key])
                        new_items = [v for v in values if v not in existing]
                        session.intelligence[key].extend(new_items)
                
                # Count total new intel
                total_new = sum(
                    len([v for v in values if v not in session.intelligence.get(key, [])])
                    for key, values in intelligence.items()
                    if isinstance(values, list)
                )
                
                self._log_action(
                    session_id,
                    ActionType.INTEL_EXTRACTION,
                    "Intelligence Extracted",
                    f"Found {total_new} new intelligence items",
                    reasoning=reasoning or "Analyzed conversation for UPIs, phone numbers, links, etc.",
                    output_data=intelligence,
                    duration_ms=duration_ms
                )
    
    def log_report_sent(
        self,
        session_id: str,
        success: bool,
        response_code: int = 0,
        response_body: str = ""
    ):
        with self._data_lock:
            if session_id in self._sessions:
                session = self._sessions[session_id]
                session.report_attempts += 1
                if success:
                    session.status = "reported"
                
                self._log_action(
                    session_id,
                    ActionType.REPORT_SENT,
                    f"Report {'Sent' if success else 'Failed'}",
                    f"GUVI callback {'succeeded' if success else 'failed'} (HTTP {response_code})",
                    reasoning="Sending extracted intelligence to GUVI evaluation endpoint",
                    output_data={"responseCode": response_code, "responseBody": response_body[:200]},
                    success=success
                )
    
    def log_error(self, session_id: str, title: str, error: str):
        with self._data_lock:
            self._log_action(
                session_id,
                ActionType.ERROR,
                title,
                error,
                success=False
            )
    
    def _log_action(
        self,
        session_id: str,
        action_type: ActionType,
        title: str,
        details: str,
        reasoning: str = "",
        input_data: Any = None,
        output_data: Any = None,
        duration_ms: int = 0,
        success: bool = True
    ):
        """Internal method to log action (must be called with lock held)"""
        log = ActionLog(
            session_id=session_id,
            action_type=action_type,
            title=title,
            details=details,
            reasoning=reasoning,
            input_data=input_data,
            output_data=output_data,
            duration_ms=duration_ms,
            success=success
        )
        
        self._global_logs.insert(0, log)
        if len(self._global_logs) > 500:
            self._global_logs = self._global_logs[:500]
        
        if session_id in self._sessions:
            self._sessions[session_id].add_action_log(log)
    
    def get_all_sessions_summary(self) -> List[Dict]:
        with self._data_lock:
            sessions = sorted(
                self._sessions.values(),
                key=lambda s: s.updated_at,
                reverse=True
            )
            return [s.to_summary() for s in sessions]
    
    def get_session_detail(self, session_id: str) -> Optional[Dict]:
        with self._data_lock:
            if session_id in self._sessions:
                return self._sessions[session_id].to_dict()
            return None
    
    def get_global_logs(self, limit: int = 50) -> List[Dict]:
        with self._data_lock:
            return [log.to_dict() for log in self._global_logs[:limit]]
    
    def get_stats(self) -> Dict[str, Any]:
        with self._data_lock:
            total = len(self._sessions)
            active = sum(1 for s in self._sessions.values() if s.status == "active")
            scams = sum(1 for s in self._sessions.values() if s.scam_detected)
            reported = sum(1 for s in self._sessions.values() if s.status == "reported")
            
            total_messages = sum(len(s.messages) for s in self._sessions.values())
            total_intel = sum(
                sum(len(v) for v in s.intelligence.values() if isinstance(v, list))
                for s in self._sessions.values()
            )
            
            return {
                "totalSessions": total,
                "activeSessions": active,
                "scamsDetected": scams,
                "sessionsReported": reported,
                "totalMessages": total_messages,
                "totalIntelligence": total_intel,
                "totalLogs": len(self._global_logs)
            }


# Global singleton instance
admin_logger = AdminLogger()
