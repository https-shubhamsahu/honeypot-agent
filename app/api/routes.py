from fastapi import APIRouter, HTTPException, Depends, Header
from app.models import ChatRequest, ChatResponse
from app.core.config import settings
from typing import Optional
import time

router = APIRouter()

async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    if x_api_key != settings.HONEYPOT_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return x_api_key

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, api_key: str = Depends(verify_api_key)):
    from app.services.scam_detector import ScamDetector
    from app.services.agent_engine import AgentEngine
    from app.services.intelligence_extractor import IntelligenceExtractor
    from app.services.reporting import ReportingService
    from app.services.data_store import data_store
    from app.services.admin_logger import admin_logger

    # Get channel from metadata
    channel = "Unknown"
    if request.metadata:
        channel = request.metadata.channel or "Unknown"

    # Initialize session in both stores
    session = data_store.get_or_create_session(request.sessionId, channel)
    admin_logger.get_or_create_session(request.sessionId, channel)
    
    # Log incoming message
    admin_logger.log_message_received(
        request.sessionId,
        request.message.sender,
        request.message.text
    )

    # 1. Scam Detection with timing
    start_time = time.time()
    is_scam = True  # Default assumption for follow-ups
    scam_reasoning = "Follow-up message in existing scam conversation"
    
    if not request.conversationHistory:
        is_scam, scam_reasoning = await ScamDetector.detect_with_reasoning(request.message.text)
    
    detection_time = int((time.time() - start_time) * 1000)
    
    # Log scam detection result
    admin_logger.log_scam_detection(
        request.sessionId,
        is_scam,
        confidence=0.95 if is_scam else 0.1,
        reasoning=scam_reasoning
    )
    
    if not is_scam:
        return ChatResponse(status="ignored", reply="Message received.")

    # Update session with scam detection
    data_store.update_session(
        request.sessionId,
        scam_detected=True,
        conversation_preview=request.message.text[:100]
    )

    # 2. Agent Response with timing
    start_time = time.time()
    reply_text, agent_reasoning = await AgentEngine.generate_reply_with_reasoning(
        request.conversationHistory, 
        request.message.text
    )
    agent_time = int((time.time() - start_time) * 1000)
    
    # Log agent response
    admin_logger.log_agent_response(
        request.sessionId,
        reply_text,
        persona="Grandma Betty",
        reasoning=agent_reasoning,
        duration_ms=agent_time
    )

    # 3. Intelligence Extraction with timing
    start_time = time.time()
    intelligence, intel_reasoning = await IntelligenceExtractor.extract_with_reasoning(
        request.conversationHistory, 
        request.message.text
    )
    intel_time = int((time.time() - start_time) * 1000)
    
    # Log intelligence extraction
    admin_logger.log_intel_extraction(
        request.sessionId,
        intelligence,
        reasoning=intel_reasoning,
        duration_ms=intel_time
    )
    
    # Calculate total messages
    total_messages = len(request.conversationHistory) + 2

    # 4. Reporting logic
    status = "active"
    found_intel = any(len(v) > 0 for k, v in intelligence.items() if isinstance(v, list))
    
    if found_intel or total_messages > 5:
        status = "reported"
        success, response_code, response_body = ReportingService.report_with_response(
            session_id=request.sessionId,
            scam_detected=True,
            message_count=total_messages,
            intelligence=intelligence,
            notes="Engaged with scammer, extracted available intelligence."
        )
        
        # Log report attempt
        admin_logger.log_report_sent(
            request.sessionId,
            success,
            response_code,
            response_body
        )

    # Update data store
    data_store.update_session(
        request.sessionId,
        message_count=total_messages,
        intelligence=intelligence,
        status=status,
        agent_notes=f"Replied: {reply_text[:50]}..."
    )

    return ChatResponse(
        status="success",
        reply=reply_text
    )

