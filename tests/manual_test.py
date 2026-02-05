import os
import sys

# Setup Path and Env
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ["HONEYPOT_API_KEY"] = "test-secret-key"
os.environ["GROQ_API_KEY"] = "test-groq-key"

from unittest.mock import AsyncMock, patch
# Import app AFTER env set
from main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def run_test():
    print("Starting manual test...")
    try:
        # Patching manually
        p1 = patch("app.services.scam_detector.ScamDetector.detect", new_callable=AsyncMock)
        p2 = patch("app.services.agent_engine.AgentEngine.generate_reply", new_callable=AsyncMock)
        p3 = patch("app.services.intelligence_extractor.IntelligenceExtractor.extract", new_callable=AsyncMock)
        p4 = patch("app.services.reporting.ReportingService.report")
        
        m_detect = p1.start()
        m_detect.return_value = True
        
        m_agent = p2.start()
        m_agent.return_value = "Manual Reply"
        
        m_intel = p3.start()
        m_intel.return_value = {}
        
        m_report = p4.start()
        
        print("Sending request...")
        response = client.post(
            "/chat",
            json={
                "sessionId": "test-session",
                "message": {
                    "sender": "scammer",
                    "text": "Urgent!",
                    "timestamp": 123456
                },
                "conversationHistory": []
            },
            headers={"x-api-key": "test-secret-key"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code != 200:
             print("Test Failed!")
             return False
        else:
             print("Test Passed!")

        p1.stop()
        p2.stop()
        p3.stop()
        p4.stop()
        return True
        
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    run_test()
