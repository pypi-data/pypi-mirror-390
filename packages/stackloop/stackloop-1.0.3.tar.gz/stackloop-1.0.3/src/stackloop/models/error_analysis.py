from pydantic import BaseModel
from typing import List, Optional

class FileFix(BaseModel):
    file_path: Optional[str]      # Path relative to working dir, None for non-file errors
    suggested_fix: str            # Code patch or textual instruction
    can_fix_automatically: bool  # Whether the fix can be applied automatically

class ErrorAnalysis(BaseModel):
    message: str                  # General description of the error
    fixes: List[FileFix]          # One or more file-specific fixes
