from typing import Optional
from pydantic import BaseModel, Field


class ActionData(BaseModel):
    actions: Optional[str] = None
