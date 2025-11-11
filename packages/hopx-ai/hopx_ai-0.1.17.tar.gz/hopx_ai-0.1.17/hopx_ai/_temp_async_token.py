# Token management pentru AsyncSandbox (copiat din sandbox.py)

from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class TokenData:
    """JWT token data."""
    token: str
    expires_at: datetime

# Global token cache (shared between Sandbox instances)
_token_cache: Dict[str, TokenData] = {}
