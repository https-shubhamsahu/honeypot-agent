import requests
from app.core.config import settings
from typing import Dict, Any, Tuple

class ReportingService:
    @staticmethod
    def report(session_id: str, scam_detected: bool, message_count: int, intelligence: Dict[str, Any], notes: str):
        """
        Sends the final report to the GUVI evaluation endpoint.
        """
        ReportingService.report_with_response(session_id, scam_detected, message_count, intelligence, notes)
    
    @staticmethod
    def report_with_response(session_id: str, scam_detected: bool, message_count: int, intelligence: Dict[str, Any], notes: str) -> Tuple[bool, int, str]:
        """
        Sends report and returns response details.
        Returns: (success: bool, status_code: int, response_body: str)
        """
        # Ensure all required keys exist
        for key in ["bankAccounts", "upiIds", "phishingLinks", "phoneNumbers", "suspiciousKeywords"]:
            if key not in intelligence:
                intelligence[key] = []
        
        payload = {
            "sessionId": session_id,
            "scamDetected": scam_detected,
            "totalMessagesExchanged": message_count,
            "extractedIntelligence": intelligence,
            "agentNotes": notes
        }
        
        url = settings.GUVI_CALLBACK_URL
        if not url:
            print("No callback URL configured.")
            return False, 0, "No callback URL configured"

        try:
            print(f"Reporting to {url} with payload: {payload}")
            response = requests.post(url, json=payload, timeout=10)
            response_body = response.text[:500]  # Limit response body length
            print(f"Report status: {response.status_code}, Body: {response_body}")
            
            success = 200 <= response.status_code < 300
            return success, response.status_code, response_body
            
        except requests.Timeout:
            error_msg = "Request timed out after 10 seconds"
            print(f"Failed to report results: {error_msg}")
            return False, 0, error_msg
            
        except requests.RequestException as e:
            error_msg = f"Request error: {str(e)}"
            print(f"Failed to report results: {error_msg}")
            return False, 0, error_msg
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            print(f"Failed to report results: {error_msg}")
            return False, 0, error_msg

