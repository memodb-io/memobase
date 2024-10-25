from typing import Optional
from pydantic import BaseModel, Field


class ClaimData(BaseModel):
    claim: Optional[str] = None
