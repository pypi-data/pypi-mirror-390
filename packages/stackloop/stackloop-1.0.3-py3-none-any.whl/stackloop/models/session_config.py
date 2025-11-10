from dataclasses import dataclass, field
import json
from pathlib import Path

@dataclass
class SessionConfig:
    runtime: str
    script: str
    root_directory: Path
    working_directory: Path
    timestamp: str
    relative_path: str
    modified_files: set[str] = field(default_factory=set)
    
    @classmethod
    def from_json(cls, path: Path):
        with open(path, "r") as f:
            data = json.load(f)
        return cls(
            runtime=data["runtime"],
            script=data["script"],
            root_directory=Path(data["root_directory"]),
            working_directory=Path(data["working_directory"]),
            timestamp=data["timestamp"],
            relative_path=data["relative_path"],
            modified_files=set(data.get("modified_files", []))
        )

    
    def to_dict(self):
        return {
            "runtime": self.runtime,
            "script": self.script,
            "root_directory": str(self.root_directory),
            "working_directory": str(self.working_directory),
            "timestamp": self.timestamp,
            "relative_path": self.relative_path,
            "modified_files": list(self.modified_files)
        }
        
    def to_json(self, **kwargs):
        return json.dumps(self.to_dict(), **kwargs)