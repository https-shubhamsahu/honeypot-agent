from openai import AsyncOpenAI
from app.core.config import settings
import json
from typing import Tuple

client = AsyncOpenAI(
    api_key=settings.GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

class ScamDetector:
    @staticmethod
    async def detect(text: str) -> bool:
        """
        Analyzes the message text to determine if it has scam intent.
        """
        is_scam, _ = await ScamDetector.detect_with_reasoning(text)
        return is_scam
    
    @staticmethod
    async def detect_with_reasoning(text: str) -> Tuple[bool, str]:
        """
        Analyzes the message and returns both the result and reasoning.
        Returns: (is_scam: bool, reasoning: str)
        """
        if not settings.GROQ_API_KEY:
            # Fallback for testing/mocking if no key
            keywords = ["bank", "verify", "blocked", "urgent", "upi", "account"]
            found = [k for k in keywords if k in text.lower()]
            if found:
                return True, f"Keyword match detected: {', '.join(found)}"
            return False, "No scam keywords detected"

        try:
            response = await client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": """You are a scam detection expert. Analyze the following message and determine if it is a scam (phishing, fraud, urgency tactics, financial request, impersonation).
                    
Reply with JSON format:
{
    "is_scam": true/false,
    "confidence": 0.0-1.0,
    "reason": "Detailed explanation of why this is/isn't a scam",
    "indicators": ["list", "of", "red", "flags"]
}"""},
                    {"role": "user", "content": text}
                ],
                temperature=0
            )
            content = response.choices[0].message.content
            
            # cleanup markdown
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "")
            if content.startswith("```"):
                content = content.replace("```", "")
            
            result = json.loads(content.strip())
            is_scam = result.get("is_scam", False)
            reason = result.get("reason", "No reason provided")
            indicators = result.get("indicators", [])
            confidence = result.get("confidence", 0.5)
            
            reasoning = f"{reason}"
            if indicators:
                reasoning += f" | Indicators: {', '.join(indicators)}"
            reasoning += f" | Confidence: {confidence:.0%}"
            
            return is_scam, reasoning
            
        except Exception as e:
            error_msg = f"Error in scam detection: {str(e)}"
            print(error_msg)
            return False, error_msg

