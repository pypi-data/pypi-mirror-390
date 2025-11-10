from pydantic import BaseModel

class CorrectedCode(BaseModel):
    code: str  # Only the corrected code