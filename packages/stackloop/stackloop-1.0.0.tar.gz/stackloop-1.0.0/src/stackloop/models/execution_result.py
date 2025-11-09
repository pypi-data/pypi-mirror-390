from datetime import datetime
from pydantic import BaseModel, Field

class ExecutionResult(BaseModel):
    """Result of running the application"""
    success: bool
    return_code: int
    stdout: str
    stderr: str
    execution_time: float
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
