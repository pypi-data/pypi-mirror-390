import httpx
from typing import Dict, Any, Optional
from bson import ObjectId
from src.services.config import config
import json


class KariniClient:    
    def __init__(
        self,
        api_base: Optional[str] = None,
        copilot_id: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        """Initialize Karini client."""
        self.api_base = api_base or config.api_base
        self.copilot_id = copilot_id or config.copilot_id
        self.api_key = api_key or config.copilot_api_key
        
        if not all([self.api_base, self.copilot_id, self.api_key]):
            raise ValueError(
                "Missing required configuration. Please set: "
                "KARINI_API_BASE, KARINI_COPILOT_ID, KARINI_API_KEY"
            )
        
        self.headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "x-client-type": "swagger",
        }
    
    async def ask_copilot(
        self,
        question: str,
        suggest_followup_questions: bool = False,
    ) -> Dict[str, Any]:
        """Send a question to the copilot."""
        url = f"{self.api_base}/api/copilot/{self.copilot_id}"
        thread = "68f1efc97c30caba4676f6a0"
        
        payload = {
            "request_id": str(ObjectId()),
            "question": question,
            "suggest_followup_questions": suggest_followup_questions,
            "thread": thread,
        }
        
        async with httpx.AsyncClient(timeout=300.0) as client:
            async with client.stream("POST", url, headers=self.headers, json=payload) as response:
                response.raise_for_status()
                
                full_response = ""
                async for chunk in response.aiter_text():
                    full_response += chunk
                
                return full_response

try:
    karini_client = KariniClient()
except ValueError:
    karini_client = None