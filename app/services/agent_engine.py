from openai import AsyncOpenAI
from app.core.config import settings
from typing import List, Tuple
from app.models import Message

client = AsyncOpenAI(
    api_key=settings.GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

PERSONA = """You are an elderly person named 'Grandma Betty'. 
You are non-tech savvy, polite, slightly confused, and worried about your accounts. 
Your goal is to waste the scammer's time by asking clarifying questions, acting confused, 
and pretending to comply but failing at technical steps. 
Do NOT reveal you are an AI. 
Keep responses short and conversational."""

class AgentEngine:
    @staticmethod
    async def generate_reply(history: List[Message], current_message: str) -> str:
        """
        Generates a human-like response to engage the scammer.
        """
        reply, _ = await AgentEngine.generate_reply_with_reasoning(history, current_message)
        return reply
    
    @staticmethod
    async def generate_reply_with_reasoning(history: List[Message], current_message: str) -> Tuple[str, str]:
        """
        Generates a response and returns reasoning about the strategy used.
        Returns: (reply: str, reasoning: str)
        """
        if not settings.GROQ_API_KEY:
            return "Oh no, really? What should I do?", "Fallback response (no API key)"

        messages = [
            {"role": "system", "content": PERSONA}
        ]

        # Convert history format
        for msg in history:
            role = "user" if msg.sender == "scammer" else "assistant"
            messages.append({"role": role, "content": msg.text})
        
        # Add current
        messages.append({"role": "user", "content": current_message})
        
        # Determine strategy based on conversation length
        turn_count = len(history) // 2 + 1
        if turn_count <= 2:
            strategy = "Initial engagement: Acting confused and asking for clarification"
        elif turn_count <= 5:
            strategy = "Building rapport: Pretending to try but having technical difficulties"
        else:
            strategy = "Prolonged engagement: Stalling with more questions to waste scammer's time"

        try:
            response = await client.chat.completions.create(
                model="llama3-70b-8192",
                messages=messages,
                temperature=0.7
            )
            reply = response.choices[0].message.content
            
            reasoning = f"Strategy: {strategy} | Persona: Grandma Betty | Turn: {turn_count} | Response length: {len(reply)} chars"
            
            return reply, reasoning
        except Exception as e:
            error_msg = f"Error in agent generation: {str(e)}"
            print(error_msg)
            return "I am confused. Can you explain again?", error_msg

