import os
from typing import Optional
from dataclasses import dataclass


@dataclass
class Config:    
    api_base: str
    copilot_id: Optional[str] = None
    copilot_api_key: Optional[str] = None
    copilot_origin: Optional[str] = None
    webhook_url: Optional[str] = None
    webhook_api_key: Optional[str] = None
    
    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        return cls(
            api_base=os.getenv("KARINI_API_BASE"),
            copilot_id=os.getenv("KARINI_COPILOT_ID"),
            copilot_api_key=os.getenv("KARINI_API_KEY"),
        )
    
    def validate_copilot_config(self) -> bool:
        """Validate that required copilot configuration is present."""
        return all([
            self.api_base,
            self.copilot_id,
            self.copilot_api_key,
        ])

config = Config.from_env()