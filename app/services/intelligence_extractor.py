from openai import AsyncOpenAI
from app.core.config import settings
from typing import List, Dict, Any, Tuple
from app.models import Message
import json
import re

client = AsyncOpenAI(
    api_key=settings.GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

class IntelligenceExtractor:
    @staticmethod
    async def extract(history: List[Message], current_message: str) -> Dict[str, Any]:
        """
        Extracts structured intelligence (UPI, Bank, Links) from the conversation.
        """
        intel, _ = await IntelligenceExtractor.extract_with_reasoning(history, current_message)
        return intel
    
    @staticmethod
    async def extract_with_reasoning(history: List[Message], current_message: str) -> Tuple[Dict[str, Any], str]:
        """
        Extracts intelligence and provides reasoning about what was found.
        Returns: (intelligence: Dict, reasoning: str)
        """
        empty_result = {
            "bankAccounts": [],
            "upiIds": [],
            "phishingLinks": [],
            "phoneNumbers": [],
            "suspiciousKeywords": []
        }
        
        if not settings.GROQ_API_KEY:
            # Fallback: regex-based extraction
            all_text = current_message + " " + " ".join(m.text for m in history)
            
            # Basic regex patterns
            upi_pattern = r'[a-zA-Z0-9._-]+@[a-zA-Z]+'
            phone_pattern = r'\b[6-9]\d{9}\b'
            url_pattern = r'https?://[^\s]+'
            
            upis = re.findall(upi_pattern, all_text)
            phones = re.findall(phone_pattern, all_text)
            urls = re.findall(url_pattern, all_text)
            
            keywords = []
            for kw in ['urgent', 'verify', 'blocked', 'suspend', 'immediately', 'kyc']:
                if kw in all_text.lower():
                    keywords.append(kw)
            
            result = {
                "bankAccounts": [],
                "upiIds": upis,
                "phishingLinks": urls,
                "phoneNumbers": phones,
                "suspiciousKeywords": keywords
            }
            
            total = sum(len(v) for v in result.values())
            reasoning = f"Regex extraction (fallback): Found {total} items - {len(upis)} UPIs, {len(phones)} phones, {len(urls)} links, {len(keywords)} keywords"
            
            return result, reasoning

        conversation_text = ""
        for msg in history:
            conversation_text += f"{msg.sender}: {msg.text}\n"
        conversation_text += f"scammer: {current_message}\n"

        prompt = """
        Analyze the following conversation and extract intelligence about the scammer.
        Return JSON format:
        {
            "bankAccounts": ["list of account numbers"],
            "upiIds": ["list of UPI IDs like name@upi"],
            "phishingLinks": ["list of URLs"],
            "phoneNumbers": ["list of phone numbers"],
            "suspiciousKeywords": ["list of keywords like 'urgent', 'verify', 'blocked'"],
            "analysis": "Brief summary of what was found and scam tactics identified"
        }
        Only include items actually found in the text. Return empty lists if not found.
        """

        try:
            response = await client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": conversation_text}
                ],
                temperature=0,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Extract analysis if present
            analysis = result.pop("analysis", "")
            
            # Count findings
            total_found = sum(len(v) for v in result.values() if isinstance(v, list))
            
            reasoning = f"LLM extraction: Found {total_found} intelligence items"
            if analysis:
                reasoning += f" | Analysis: {analysis}"
            
            # Merge with empty result to ensure all keys exist
            for key in empty_result:
                if key not in result:
                    result[key] = []
            
            return result, reasoning
            
        except Exception as e:
            error_msg = f"Error in extraction: {str(e)}"
            print(error_msg)
            return empty_result, error_msg

