import pytest
import os
import sys

# Ensure app module is found (copied from conftest)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# Set env vars
os.environ["HONEYPOT_API_KEY"] = "test-secret-key"
os.environ["GROQ_API_KEY"] = "test-groq-key"

from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, AsyncMock
import json

client = TestClient(app)

@pytest.fixture
def sample_first_message_payload():
    return {
        "sessionId": "test-session",
        "message": {
            "sender": "scammer",
            "text": "Urgent! Account blocked.",
            "timestamp": 123456789
        },
        "conversationHistory": [],
        "metadata": {"channel": "TEST"}
    }

@pytest.fixture
def sample_followup_payload():
    return {
        "sessionId": "test-session",
        "message": {
            "sender": "scammer",
            "text": "Send UPI now.",
            "timestamp": 123456799
        },
        "conversationHistory": [
            {"sender": "scammer", "text": "Urgent! Account blocked.", "timestamp": 123456789},
            {"sender": "user", "text": "Why?", "timestamp": 123456790}
        ],
        "metadata": {"channel": "TEST"}
    }


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Agentic Honey-Pot is running"}

def test_auth_missing():
    response = client.post("/chat", json={})
    assert response.status_code == 422

def test_auth_invalid(sample_first_message_payload):
    response = client.post(
        "/chat", 
        json=sample_first_message_payload,
        headers={"x-api-key": "wrong-key"}
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Invalid API Key"

def test_scam_detected_flow(sample_first_message_payload):
    # Manual patching to mirror diagnose.py success
    with patch("app.services.scam_detector.ScamDetector.detect", new_callable=AsyncMock) as mock_detect, \
         patch("app.services.agent_engine.AgentEngine.generate_reply", new_callable=AsyncMock) as mock_agent, \
         patch("app.services.intelligence_extractor.IntelligenceExtractor.extract", new_callable=AsyncMock) as mock_intel, \
         patch("app.services.reporting.ReportingService.report") as mock_report:
        
        mock_detect.return_value = True
        agent_response = "Oh no! Why blocked?"
        mock_agent.return_value = agent_response
        mock_intel.return_value = {}
        
        response = client.post(
            "/chat",
            json=sample_first_message_payload,
            headers={"x-api-key": "test-secret-key"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["reply"] == agent_response
        
        mock_report.assert_not_called()

def test_not_scam_flow(sample_first_message_payload):
    with patch("app.services.scam_detector.ScamDetector.detect", new_callable=AsyncMock) as mock_detect:
        mock_detect.return_value = False
        
        response = client.post(
            "/chat",
            json=sample_first_message_payload,
            headers={"x-api-key": "test-secret-key"}
        )
        
        assert response.status_code == 200
        assert response.json()["status"] == "ignored"

def test_reporting_trigger(sample_followup_payload):
    with patch("app.services.agent_engine.AgentEngine.generate_reply", new_callable=AsyncMock) as mock_agent, \
         patch("app.services.intelligence_extractor.IntelligenceExtractor.extract", new_callable=AsyncMock) as mock_intel, \
         patch("app.services.reporting.ReportingService.report") as mock_report:
         
        mock_agent.return_value = "Here is UPI"
        intel_data = {"upiIds": ["bad@upi"], "bankAccounts": []}
        mock_intel.return_value = intel_data
        
        response = client.post(
            "/chat",
            json=sample_followup_payload,
            headers={"x-api-key": "test-secret-key"}
        )
        
        assert response.status_code == 200
        mock_report.assert_called_once()
        args, _ = mock_report.call_args
        assert args[3] == intel_data
