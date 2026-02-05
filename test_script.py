import requests
import json
import time
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://127.0.0.1:8000"
API_KEY = os.getenv("HONEYPOT_API_KEY")

def test_first_message():
    print("Testing First Message...")
    payload = {
        "sessionId": "test-session-123",
        "message": {
            "sender": "scammer",
            "text": "Your bank account will be blocked today. Verify immediately.",
            "timestamp": 1770005528731
        },
        "conversationHistory": [],
        "metadata": {
            "channel": "SMS",
            "language": "English",
            "locale": "IN"
        }
    }
    headers = {"x-api-key": API_KEY}
    
    try:
        response = requests.post(f"{BASE_URL}/chat", json=payload, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Failed: {e}")

def test_follow_up():
    print("\nTesting Follow-Up Message...")
    payload = {
        "sessionId": "test-session-123",
        "message": {
            "sender": "scammer",
            "text": "Share your UPI ID to avoid account suspension.",
            "timestamp": 1770005528731
        },
        "conversationHistory": [
            {
                "sender": "scammer",
                "text": "Your bank account will be blocked today. Verify immediately.",
                "timestamp": 1770005528731
            },
            {
                "sender": "user",
                "text": "Why will my account be blocked?",
                "timestamp": 1770005528731
            }
        ],
        "metadata": {
            "channel": "SMS",
            "language": "English",
            "locale": "IN"
        }
    }
    headers = {"x-api-key": API_KEY}
    
    try:
        response = requests.post(f"{BASE_URL}/chat", json=payload, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    # Wait for server to start if running immediately
    time.sleep(2)
    test_first_message()
    test_follow_up()
