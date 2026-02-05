from pydantic import BaseModel, Field
from typing import List, Optional, Any

class Message(BaseModel):
    sender: str  # "scammer" or "user"
    text: str
    timestamp: int

class MetaData(BaseModel):
    channel: Optional[str] = None
    language: Optional[str] = None
    locale: Optional[str] = None

class ChatRequest(BaseModel):
    sessionId: str
    message: Message
    conversationHistory: List[Message] = []
    metadata: Optional[MetaData] = None

class ChatResponse(BaseModel):
    status: str
    reply: str
